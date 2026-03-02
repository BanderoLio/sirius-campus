import sys
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

import grpc
import structlog

from src.config import settings
from src.database import async_session_factory
from src.domain.exceptions import (
    PatrolNotFoundError,
    ValidationError,
    ForbiddenError,
    PatrolAlreadyCompletedError,
    PatrolAlreadyExistsError,
    PatrolEntryNotFoundError,
    PatrolNotInProgressError,
)
from src.grpc_clients.auth_client import get_auth_client
from src.grpc_clients.application_client import get_application_client
from src.repositories.patrol_repository import PatrolRepository
from src.repositories.patrol_entry_repository import PatrolEntryRepository

logger = structlog.get_logger(__name__)


def _import_generated() -> tuple[object, object]:
    """
    grpcio-tools generates `patrol_pb2.py` and `patrol_pb2_grpc.py`
    into `src/grpc_server/`. Those modules use absolute imports like
    `import patrol_pb2`, so we add this directory to sys.path at runtime.
    """
    grpc_dir = Path(__file__).resolve().parent
    if str(grpc_dir) not in sys.path:
        sys.path.insert(0, str(grpc_dir))

    import patrol_pb2  # type: ignore[import-not-found]
    import patrol_pb2_grpc  # type: ignore[import-not-found]

    return patrol_pb2, patrol_pb2_grpc


def _user_name_from_info(info: object | None) -> str | None:
    if info is None:
        return None
    last = getattr(info, "last_name", "") or ""
    first = getattr(info, "first_name", "") or ""
    patronymic = getattr(info, "patronymic", "") or ""
    return f"{last} {first} {patronymic}".strip() or None


async def _domain_exception_to_grpc(context, exc: Exception) -> None:
    """Map domain exceptions to gRPC abort. context.abort is a coroutine in aio."""
    if isinstance(exc, PatrolNotFoundError):
        await context.abort(grpc.StatusCode.NOT_FOUND, exc.args[0] if exc.args else "Not found")
    elif isinstance(exc, ForbiddenError):
        await context.abort(grpc.StatusCode.PERMISSION_DENIED, exc.args[0] if exc.args else "Forbidden")
    elif isinstance(exc, ValidationError):
        await context.abort(grpc.StatusCode.INVALID_ARGUMENT, exc.args[0] if exc.args else "Invalid")
    else:
        logger.exception("grpc_handler_error", error=str(exc))
        await context.abort(grpc.StatusCode.INTERNAL, "Internal error")


class _PatrolGrpcServicer:
    def __init__(self) -> None:
        self._auth = get_auth_client()
        self._application = get_application_client()

    async def ListPatrols(self, request, context):
        try:
            # Parse optional date
            patrol_date = None
            if request.date:
                try:
                    patrol_date = date.fromisoformat(request.date)
                except ValueError:
                    await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid date format, expected YYYY-MM-DD")
                    return None

            # Parse optional entrance
            entrance = None
            if request.entrance:
                try:
                    entrance = int(request.entrance)
                except ValueError:
                    await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid entrance, expected integer")
                    return None

            async with async_session_factory() as session:
                patrol_repo = PatrolRepository(session)
                entry_repo = PatrolEntryRepository(session)

                items, total = await patrol_repo.get_list(
                    patrol_date=patrol_date,
                    building=request.building or None,
                    entrance=entrance,
                    status=request.status or None,
                    page=request.page,
                    size=request.size,
                )

            patrol_pb2, _ = _import_generated()
            patrols = []
            for patrol in items:
                entries = await entry_repo.get_by_patrol_id(patrol.patrol_id)
                present_count = sum(1 for e in entries if e.is_present is True)
                absent_count = sum(1 for e in entries if e.is_present is False)

                patrol_proto = patrol_pb2.PatrolSummary(
                    patrol_id=str(patrol.patrol_id),
                    date=patrol.date.isoformat(),
                    building=patrol.building,
                    entrance=str(patrol.entrance),
                    status=patrol.status,
                    started_at=patrol.started_at.isoformat() if patrol.started_at else "",
                    submitted_at=patrol.submitted_at.isoformat() if patrol.submitted_at else "",
                    entries_count=len(entries),
                    present_count=present_count,
                    absent_count=absent_count,
                )
                patrols.append(patrol_proto)

            pages = (total + request.size - 1) // request.size if request.size > 0 else 0

            return patrol_pb2.ListPatrolsResponse(
                items=patrols,
                total=total,
                page=request.page,
                size=request.size,
                pages=pages,
            )

    async def GetPatrolsForDate(self, request, context):
        try:
            patrol_date = date.fromisoformat(request.date)
        except Exception:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid date format, expected YYYY-MM-DD")
            return None

        building = request.building or None
        entrance = request.entrance or None

        async with async_session_factory() as session:
            patrol_repo = PatrolRepository(session)
            entry_repo = PatrolEntryRepository(session)

            # Get all patrols for the date
            items, total = await patrol_repo.get_list(
                patrol_date=patrol_date,
                building=building,
                entrance=entrance if entrance else None,
            )

        patrol_pb2, _ = _import_generated()
        patrols = []
        for patrol in items:
            # Get entries count
            entries = await entry_repo.get_by_patrol_id(patrol.patrol_id)
            present_count = sum(1 for e in entries if e.is_present is True)
            absent_count = sum(1 for e in entries if e.is_present is False)

            patrol_proto = patrol_pb2.PatrolSummary(
                patrol_id=str(patrol.patrol_id),
                date=patrol.date.isoformat(),
                building=patrol.building,
                entrance=patrol.entrance,
                status=patrol.status,
                started_at=patrol.started_at.isoformat() if patrol.started_at else "",
                submitted_at=patrol.submitted_at.isoformat() if patrol.submitted_at else "",
                entries_count=len(entries),
                present_count=present_count,
                absent_count=absent_count,
            )
            patrols.append(patrol_proto)

        return patrol_pb2.GetPatrolsForDateResponse(patrols=patrols)

    async def GetPatrolDetails(self, request, context):
        try:
            patrol_id = UUID(request.patrol_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid patrol_id")
            return None

        async with async_session_factory() as session:
            patrol_repo = PatrolRepository(session)
            entry_repo = PatrolEntryRepository(session)

            patrol = await patrol_repo.get_by_id_with_entries(patrol_id)
            if not patrol:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Patrol not found")
                return None

            # Get user info for patrol_by
            patrol_by_info = await self._auth.get_user_info(str(patrol.patrol_by))
            patrol_by_name = _user_name_from_info(patrol_by_info) or "Unknown"

        patrol_pb2, _ = _import_generated()
        entries_proto = []
        for entry in patrol.entries:
            # Get user info for each entry
            user_info = await self._auth.get_user_info(str(entry.user_id))
            user_name = _user_name_from_info(user_info) or "Unknown"

            entry_proto = patrol_pb2.PatrolEntryProto(
                patrol_entry_id=str(entry.patrol_entry_id),
                user_id=str(entry.user_id),
                user_name=user_name,
                room=entry.room,
                is_present=entry.is_present if entry.is_present is not None else False,
                absence_reason=entry.absence_reason or "",
                checked_at=entry.checked_at.isoformat() if entry.checked_at else "",
            )
            entries_proto.append(entry_proto)

        return patrol_pb2.GetPatrolDetailsResponse(
            patrol_id=str(patrol.patrol_id),
            date=patrol.date.isoformat(),
            building=patrol.building,
            entrance=str(patrol.entrance),
            status=patrol.status,
            started_at=patrol.started_at.isoformat() if patrol.started_at else "",
            submitted_at=patrol.submitted_at.isoformat() if patrol.submitted_at else "",
            patrol_by=str(patrol.patrol_by),
            patrol_by_name=patrol_by_name,
            entries=entries_proto,
        )

    async def CreatePatrol(self, request, context):
        # Get user_id and roles from metadata
        user_id = context.invocation_metadata().get("x-user-id")
        user_roles_str = context.invocation_metadata().get("x-user-roles", "")
        user_roles = user_roles_str.split(",") if user_roles_str else []

        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing user_id in metadata")
            return None

        try:
            patrol_date = date.fromisoformat(request.date)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid date format, expected YYYY-MM-DD")
            return None

        try:
            entrance = int(request.entrance)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid entrance, expected integer")
            return None

        # Check user roles
        PATROL_CREATOR_ROLES = frozenset({"student_patrol", "educator", "educator_head", "admin"})
        if not any(role in PATROL_CREATOR_ROLES for role in user_roles):
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Insufficient permissions to create patrol")
            return None

        async with async_session_factory() as session:
            patrol_repo = PatrolRepository(session)
            entry_repo = PatrolEntryRepository(session)

            # Check if patrol already exists
            existing = await patrol_repo.get_by_date_building_entrance(
                patrol_date=patrol_date,
                building=request.building,
                entrance=entrance,
            )
            if existing:
                await context.abort(grpc.StatusCode.ALREADY_EXISTS, "Patrol already exists for this date, building and entrance")
                return None

            # Create patrol
            started_at = datetime.now(timezone.utc)
            patrol = await patrol_repo.create(
                patrol_date=patrol_date,
                building=request.building,
                entrance=entrance,
                patrol_by=UUID(user_id),
                started_at=started_at,
            )

            # Get minor students from auth-service
            minor_students = await self._auth.get_minor_students_by_entrance(
                building=request.building,
                entrance=entrance,
            )

            # Get approved leaves from application-service
            approved_leaves = await self._application.get_approved_leaves(
                date=request.date,
                building=request.building,
                entrance=entrance,
            )

            # Create a map of user_id -> leave record for quick lookup
            leave_map = {leave.user_id: leave for leave in approved_leaves}

            # Create entries for each minor student
            entries_to_create = []
            for student in minor_students:
                entry_data = {
                    "patrol_id": patrol.patrol_id,
                    "user_id": UUID(student.user_id),
                    "room": student.room,
                }

                # Check if student has approved leave
                if student.user_id in leave_map:
                    leave = leave_map[student.user_id]
                    entry_data["is_present"] = False
                    entry_data["absence_reason"] = f"Заявление на выход: {leave.reason}"

                entries_to_create.append(entry_data)

            if entries_to_create:
                await entry_repo.create_batch(entries_to_create)

            await session.commit()

        patrol_pb2, _ = _import_generated()
        return patrol_pb2.CreatePatrolResponse(
            patrol_id=str(patrol.patrol_id),
            date=patrol.date.isoformat(),
            building=patrol.building,
            entrance=str(patrol.entrance),
            status=patrol.status,
            started_at=patrol.started_at.isoformat() if patrol.started_at else "",
            patrol_by=str(patrol.patrol_by),
        )

    async def UpdatePatrol(self, request, context):
        try:
            patrol_id = UUID(request.patrol_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid patrol_id")
            return None

        if request.status != "completed":
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Only status='completed' is supported")
            return None

        async with async_session_factory() as session:
            patrol_repo = PatrolRepository(session)

            patrol = await patrol_repo.get_by_id(patrol_id)
            if not patrol:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Patrol not found")
                return None

            if patrol.status == "completed":
                await context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Patrol already completed")
                return None

            submitted_at = datetime.now(timezone.utc)
            updated = await patrol_repo.update_status(
                patrol_id=patrol_id,
                status="completed",
                submitted_at=submitted_at,
            )

            patrol = await patrol_repo.get_by_id_with_entries(patrol_id)
            await session.commit()

        patrol_pb2, _ = _import_generated()
        return patrol_pb2.UpdatePatrolResponse(
            patrol_id=str(patrol.patrol_id),
            date=patrol.date.isoformat(),
            building=patrol.building,
            entrance=str(patrol.entrance),
            status=patrol.status,
            started_at=patrol.started_at.isoformat() if patrol.started_at else "",
            submitted_at=patrol.submitted_at.isoformat() if patrol.submitted_at else "",
            patrol_by=str(patrol.patrol_by),
        )

    async def DeletePatrol(self, request, context):
        try:
            patrol_id = UUID(request.patrol_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid patrol_id")
            return None

        async with async_session_factory() as session:
            patrol_repo = PatrolRepository(session)

            patrol = await patrol_repo.get_by_id(patrol_id)
            if not patrol:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Patrol not found")
                return None

            await patrol_repo.delete(patrol_id)
            await session.commit()

        patrol_pb2, _ = _import_generated()
        return patrol_pb2.DeletePatrolResponse(success=True)

    async def GetPatrolEntry(self, request, context):
        try:
            patrol_id = UUID(request.patrol_id)
            patrol_entry_id = UUID(request.patrol_entry_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid patrol_id or patrol_entry_id")
            return None

        async with async_session_factory() as session:
            entry_repo = PatrolEntryRepository(session)

            entry = await entry_repo.get_by_patrol_and_entry_id(patrol_id, patrol_entry_id)
            if not entry:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Patrol entry not found")
                return None

            # Get user info
            user_info = await self._auth.get_user_info(str(entry.user_id))
            user_name = _user_name_from_info(user_info) or "Unknown"

        patrol_pb2, _ = _import_generated()
        return patrol_pb2.GetPatrolEntryResponse(
            patrol_entry_id=str(entry.patrol_entry_id),
            patrol_id=str(entry.patrol_id),
            user_id=str(entry.user_id),
            user_name=user_name,
            room=entry.room,
            is_present=entry.is_present if entry.is_present is not None else False,
            absence_reason=entry.absence_reason or "",
            checked_at=entry.checked_at.isoformat() if entry.checked_at else "",
        )

    async def UpdatePatrolEntry(self, request, context):
        try:
            patrol_id = UUID(request.patrol_id)
            patrol_entry_id = UUID(request.patrol_entry_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid patrol_id or patrol_entry_id")
            return None

        async with async_session_factory() as session:
            patrol_repo = PatrolRepository(session)
            entry_repo = PatrolEntryRepository(session)

            # Check patrol exists and is in progress
            patrol = await patrol_repo.get_by_id(patrol_id)
            if not patrol:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Patrol not found")
                return None

            if patrol.status != "in_progress":
                await context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Patrol is not in progress")
                return None

            # Check entry exists
            entry = await entry_repo.get_by_patrol_and_entry_id(patrol_id, patrol_entry_id)
            if not entry:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Patrol entry not found")
                return None

            # Update entry
            checked_at = datetime.now(timezone.utc)
            updated = await entry_repo.update(
                patrol_entry_id=patrol_entry_id,
                is_present=request.is_present,
                absence_reason=request.absence_reason if request.absence_reason else None,
                checked_at=checked_at,
            )

            await session.commit()

            # Get user info
            user_info = await self._auth.get_user_info(str(entry.user_id))
            user_name = _user_name_from_info(user_info) or "Unknown"

        patrol_pb2, _ = _import_generated()
        return patrol_pb2.UpdatePatrolEntryResponse(
            patrol_entry_id=str(updated.patrol_entry_id),
            patrol_id=str(updated.patrol_id),
            user_id=str(updated.user_id),
            user_name=user_name,
            room=updated.room,
            is_present=updated.is_present if updated.is_present is not None else False,
            absence_reason=updated.absence_reason or "",
            checked_at=updated.checked_at.isoformat() if updated.checked_at else "",
        )


async def create_and_start_grpc_server() -> grpc.aio.Server | None:
    """
    Starts gRPC server if generated modules exist in the image.
    Returns the server instance or None if gRPC codegen is not available.
    """
    try:
        patrol_pb2, patrol_pb2_grpc = _import_generated()
    except Exception as e:
        logger.warning("grpc_codegen_missing", error=str(e))
        return None

    server = grpc.aio.server()
    servicer = _PatrolGrpcServicer()

    class Servicer(patrol_pb2_grpc.PatrolServiceServicer):  # type: ignore[misc]
        async def ListPatrols(self, request, context):
            return await servicer.ListPatrols(request, context)

        async def GetPatrolsForDate(self, request, context):
            return await servicer.GetPatrolsForDate(request, context)

        async def GetPatrolDetails(self, request, context):
            return await servicer.GetPatrolDetails(request, context)

        async def CreatePatrol(self, request, context):
            return await servicer.CreatePatrol(request, context)

        async def UpdatePatrol(self, request, context):
            return await servicer.UpdatePatrol(request, context)

        async def DeletePatrol(self, request, context):
            return await servicer.DeletePatrol(request, context)

        async def GetPatrolEntry(self, request, context):
            return await servicer.GetPatrolEntry(request, context)

        async def UpdatePatrolEntry(self, request, context):
            return await servicer.UpdatePatrolEntry(request, context)

    servicer = Servicer()
    patrol_pb2_grpc.add_PatrolServiceServicer_to_server(servicer, server)

    grpc_port = getattr(settings, "grpc_port", 50052)
    server.add_insecure_port(f"[::]:{grpc_port}")
    await server.start()
    logger.info("grpc_server_started", port=grpc_port)
    return server
