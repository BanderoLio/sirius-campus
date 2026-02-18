import sys
from datetime import date
from pathlib import Path

import grpc
import structlog

from src.config import settings
from src.database import async_session_factory
from src.grpc_clients.auth_client import get_auth_client
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


class _ApplicationGrpcServicer:  # instantiated with generated base class
    def __init__(self) -> None:
        self._storage = MinioStorage()
        self._auth = get_auth_client()

    async def GetApprovedLeaves(self, request, context):  # noqa: N802
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
        async def GetApprovedLeaves(self, request, context):  # noqa: N802
            return await servicer.GetApprovedLeaves(request, context)

    application_pb2_grpc.add_ApplicationServiceServicer_to_server(Servicer(), server)
    server.add_insecure_port(f"[::]:{settings.grpc_port}")
    await server.start()
    logger.info("grpc_server_started", port=settings.grpc_port)
    return server

