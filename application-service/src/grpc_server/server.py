import sys
from datetime import date, datetime, timezone
from pathlib import Path

import grpc
import structlog

from src.config import settings
from src.database import async_session_factory
from src.domain.exceptions import (
    ApplicationAlreadyDecidedError,
    ApplicationNotFoundError,
    DocumentNotFoundError,
    ForbiddenApplicationError,
    InvalidDocumentTypeError,
    MinorVoiceRequiredError,
    ValidationError,
)
from src.grpc_clients.auth_client import get_auth_client
from src.grpc_server.grpc_mapping import (
    application_detail_to_proto,
    get_user_context_from_metadata,
    model_to_application_proto,
    model_to_document_proto,
)
from src.repositories.application_document_repository import ApplicationDocumentRepository
from src.repositories.application_repository import ApplicationRepository
from src.services.application_service import ApplicationService
from src.storage.minio_storage import MinioStorage

logger = structlog.get_logger(__name__)


def _import_generated() -> tuple[object, object]:
    """
    grpcio-tools generates `application_pb2.py` and `application_pb2_grpc.py`
    into `src/grpc_server/`. Those modules use absolute imports like
    `import application_pb2`, so we add this directory to sys.path at runtime.
    """
    grpc_dir = Path(__file__).resolve().parent
    if str(grpc_dir) not in sys.path:
        sys.path.insert(0, str(grpc_dir))

    import application_pb2  # type: ignore[import-not-found]
    import application_pb2_grpc  # type: ignore[import-not-found]

    return application_pb2, application_pb2_grpc


def _user_name_from_info(info: object | None) -> str | None:
    if info is None:
        return None
    last = getattr(info, "last_name", "") or ""
    first = getattr(info, "first_name", "") or ""
    patronymic = getattr(info, "patronymic", "") or ""
    return f"{last} {first} {patronymic}".strip() or None


async def _domain_exception_to_grpc(context, exc: Exception) -> None:
    """Map domain exceptions to gRPC abort. context.abort is a coroutine in aio."""
    if isinstance(exc, ApplicationNotFoundError):
        await context.abort(grpc.StatusCode.NOT_FOUND, exc.args[0] if exc.args else "Not found")
    elif isinstance(exc, DocumentNotFoundError):
        await context.abort(grpc.StatusCode.NOT_FOUND, exc.args[0] if exc.args else "Document not found")
    elif isinstance(exc, ForbiddenApplicationError):
        await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Forbidden")
    elif isinstance(
        exc,
        (InvalidDocumentTypeError, MinorVoiceRequiredError, ApplicationAlreadyDecidedError, ValidationError),
    ):
        await context.abort(grpc.StatusCode.INVALID_ARGUMENT, exc.args[0] if exc.args else "Invalid")
    else:
        logger.exception("grpc_handler_error", error=str(exc))
        await context.abort(grpc.StatusCode.INTERNAL, "Internal error")


class _ApplicationGrpcServicer:
    def __init__(self) -> None:
        self._storage = MinioStorage()
        self._auth = get_auth_client()

    async def _get_service(self):
        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            yield ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )

    async def GetApprovedLeaves(self, request, context):
        try:
            leave_date = date.fromisoformat(request.date)
        except Exception:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid date format, expected YYYY-MM-DD")
            return None

        building = request.building or None
        entrance = int(request.entrance) if request.entrance is not None else 0

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            records = await service.get_approved_leaves_for_date(
                leave_date=leave_date,
                building=building,
                entrance=entrance,
            )

        application_pb2, _ = _import_generated()
        leave_records = [
            application_pb2.LeaveRecord(
                user_id=user_id,
                user_name=user_name,
                room=room,
                leave_time=leave_time.isoformat(),
                return_time=return_time.isoformat(),
                reason=reason,
            )
            for (user_id, user_name, room, leave_time, return_time, reason) in records
        ]
        return application_pb2.GetApprovedLeavesResponse(records=leave_records)

    async def ListApplications(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, roles = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        try:
            page = request.page if request.page > 0 else 1
            size = request.size if request.size > 0 else 20
            size = min(size, 100)
            date_from = None
            if request.date_from:
                date_from = date.fromisoformat(request.date_from)
            date_to = None
            if request.date_to:
                date_to = date.fromisoformat(request.date_to)
        except (ValueError, TypeError) as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            return None

        is_educator = any(r in roles for r in ("educator", "educator_head", "admin"))
        filter_user_id = None if is_educator else user_id
        entrance = request.entrance if request.entrance else None
        room = request.room if request.room else None
        status_filter = request.status if request.status else None

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                items, total = await service.list_applications(
                    user_id=filter_user_id,
                    entrance=entrance if is_educator else None,
                    room=room if is_educator else None,
                    status=status_filter,
                    date_from=date_from,
                    date_to=date_to,
                    page=page,
                    size=size,
                )
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None  # unreachable when abort raises

            pages = (total + size - 1) // size if total else 0
            enriched = []
            for m in items:
                user_info = await self._auth.get_user_info(str(m.user_id))
                proto_app = model_to_application_proto(
                    application_pb2, m,
                    user_name=_user_name_from_info(user_info),
                    room=user_info.room if user_info else None,
                    entrance=user_info.entrance if user_info else None,
                )
                enriched.append(proto_app)

            return application_pb2.ListApplicationsResponse(
                items=enriched,
                total=total,
                page=page,
                size=size,
                pages=pages,
            )

    async def CreateApplication(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, _ = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        try:
            leave_time = datetime.fromisoformat(request.leave_time.replace("Z", "+00:00"))
            return_time = datetime.fromisoformat(request.return_time.replace("Z", "+00:00"))
        except (ValueError, TypeError) as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid datetime: {e}")
            return None

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                model, _ = await service.create_application(
                    user_id=user_id,
                    leave_time=leave_time,
                    return_time=return_time,
                    reason=request.reason or "",
                    contact_phone=request.contact_phone or "",
                )
                await session.commit()
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None

            return application_pb2.CreateApplicationResponse(
                application=model_to_application_proto(application_pb2, model),
            )

    async def GetApplication(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, roles = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        try:
            application_id = __import__("uuid").UUID(request.application_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid application_id")
            return None

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                app = await service.get_application(
                    application_id=application_id,
                    current_user_id=user_id,
                    current_user_roles=roles,
                )
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None

            can_decide = any(r in roles for r in ("educator", "educator_head", "admin"))
            user_info = await self._auth.get_user_info(str(app.user_id))
            documents = getattr(app, "documents", []) or []
            detail = application_detail_to_proto(
                application_pb2,
                app,
                documents=documents,
                can_decide=can_decide,
                user_name=_user_name_from_info(user_info),
                room=user_info.room if user_info else None,
                entrance=user_info.entrance if user_info else None,
            )
            # Ensure submessage base is set (protobuf serialize fails if None)
            if getattr(detail, "base", None) is None:
                base = model_to_application_proto(
                    application_pb2, app,
                    user_name=_user_name_from_info(user_info),
                    room=user_info.room if user_info else None,
                    entrance=user_info.entrance if user_info else None,
                )
                detail = application_pb2.ApplicationDetail(base=base, documents=detail.documents, can_decide=detail.can_decide)
            return application_pb2.GetApplicationResponse(application=detail)

    async def DecideApplication(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, roles = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        is_educator = any(r in roles for r in ("educator", "educator_head", "admin"))
        if not is_educator:
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Forbidden")
            return None

        try:
            application_id = __import__("uuid").UUID(request.application_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid application_id")
            return None

        status_val = request.status or ""
        if status_val not in ("approved", "rejected"):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "status must be approved or rejected")
            return None

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                updated = await service.decide_application(
                    application_id=application_id,
                    status=status_val,
                    decided_by=user_id,
                    decided_at=datetime.now(timezone.utc),
                    reject_reason=request.reject_reason or None,
                )
                await session.commit()
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None

            return application_pb2.DecideApplicationResponse(
                application=model_to_application_proto(application_pb2, updated),
            )

    async def UploadDocument(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, _ = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        try:
            application_id = __import__("uuid").UUID(request.application_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid application_id")
            return None

        file_content = request.file_content or b""
        content_type = request.content_type or "application/octet-stream"
        filename = request.filename or "file"
        document_type = request.document_type or ""

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                doc = await service.upload_document(
                    application_id=application_id,
                    document_type=document_type,
                    file_data=file_content,
                    content_type=content_type,
                    filename=filename,
                    uploaded_by=user_id,
                )
                doc_proto = model_to_document_proto(application_pb2, doc)
                await session.commit()
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None

            return application_pb2.UploadDocumentResponse(document=doc_proto)

    async def GetDocumentDownloadUrl(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, roles = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        try:
            application_id = __import__("uuid").UUID(request.application_id)
            document_id = __import__("uuid").UUID(request.document_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid application_id or document_id")
            return None

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                url = await service.get_document_download_url(
                    application_id=application_id,
                    document_id=document_id,
                    current_user_id=user_id,
                    current_user_roles=roles,
                )
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None

            return application_pb2.GetDocumentDownloadUrlResponse(url=url)

    async def DeleteDocument(self, request, context):
        application_pb2, _ = _import_generated()
        user_id, roles = get_user_context_from_metadata(context)
        if not user_id:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing x-user-id")
            return None

        try:
            application_id = __import__("uuid").UUID(request.application_id)
            document_id = __import__("uuid").UUID(request.document_id)
        except (ValueError, TypeError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid application_id or document_id")
            return None

        async with async_session_factory() as session:
            app_repo = ApplicationRepository(session)
            doc_repo = ApplicationDocumentRepository(session)
            service = ApplicationService(
                application_repository=app_repo,
                document_repository=doc_repo,
                storage=self._storage,
                auth_client=self._auth,
            )
            try:
                await service.delete_document(
                    application_id=application_id,
                    document_id=document_id,
                    current_user_id=user_id,
                    current_user_roles=roles,
                )
                await session.commit()
            except Exception as e:
                await _domain_exception_to_grpc(context, e)
                return None

            return application_pb2.DeleteDocumentResponse()


async def create_and_start_grpc_server() -> grpc.aio.Server | None:
    """
    Starts gRPC server if generated modules exist in the image.
    Returns the server instance or None if gRPC codegen is not available.
    """
    try:
        application_pb2, application_pb2_grpc = _import_generated()
    except Exception as e:
        logger.warning("grpc_codegen_missing", error=str(e))
        return None

    server = grpc.aio.server()
    servicer = _ApplicationGrpcServicer()

    class Servicer(application_pb2_grpc.ApplicationServiceServicer):  # type: ignore[misc]
        async def GetApprovedLeaves(self, request, context):
            return await servicer.GetApprovedLeaves(request, context)

        async def ListApplications(self, request, context):
            return await servicer.ListApplications(request, context)

        async def CreateApplication(self, request, context):
            return await servicer.CreateApplication(request, context)

        async def GetApplication(self, request, context):
            return await servicer.GetApplication(request, context)

        async def DecideApplication(self, request, context):
            return await servicer.DecideApplication(request, context)

        async def UploadDocument(self, request, context):
            return await servicer.UploadDocument(request, context)

        async def GetDocumentDownloadUrl(self, request, context):
            return await servicer.GetDocumentDownloadUrl(request, context)

        async def DeleteDocument(self, request, context):
            return await servicer.DeleteDocument(request, context)

    application_pb2_grpc.add_ApplicationServiceServicer_to_server(Servicer(), server)
    server.add_insecure_port(f"[::]:{settings.grpc_port}")
    await server.start()
    logger.info("grpc_server_started", port=settings.grpc_port)
    return server
