"""
gRPC client for application-service. Generated code (application_pb2, application_pb2_grpc)
is produced at build time into app/grpc_gen/.
"""
import sys
from pathlib import Path

import grpc

from app.config import APPLICATION_GRPC_URL

_grpc_gen = Path(__file__).resolve().parent / "grpc_gen"
if _grpc_gen.exists() and str(_grpc_gen) not in sys.path:
    sys.path.insert(0, str(_grpc_gen))

try:
    import application_pb2  # type: ignore[import-not-found]
    import application_pb2_grpc  # type: ignore[import-not-found]
except ImportError:
    application_pb2 = None
    application_pb2_grpc = None


def _metadata(user_id: str, roles: list[str]) -> list[tuple[str, str]]:
    return [
        ("x-user-id", user_id),
        ("x-user-roles", ",".join(roles)),
    ]


async def list_applications(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    page: int = 1,
    size: int = 20,
    status: str | None = None,
    entrance: int | None = None,
    room: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    if application_pb2 is None or application_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = application_pb2_grpc.ApplicationServiceStub(channel)
    req = application_pb2.ListApplicationsRequest(
        page=page,
        size=size,
        status=status or "",
        entrance=entrance or 0,
        room=room or "",
        date_from=date_from or "",
        date_to=date_to or "",
    )
    return await stub.ListApplications(req, metadata=_metadata(user_id, roles))


async def create_application(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    leave_time: str,
    return_time: str,
    reason: str,
    contact_phone: str,
):
    if application_pb2 is None or application_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = application_pb2_grpc.ApplicationServiceStub(channel)
    req = application_pb2.CreateApplicationRequest(
        leave_time=leave_time,
        return_time=return_time,
        reason=reason,
        contact_phone=contact_phone,
    )
    return await stub.CreateApplication(req, metadata=_metadata(user_id, roles))


async def get_application(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    application_id: str,
):
    if application_pb2 is None or application_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = application_pb2_grpc.ApplicationServiceStub(channel)
    req = application_pb2.GetApplicationRequest(application_id=application_id)
    return await stub.GetApplication(req, metadata=_metadata(user_id, roles))


async def decide_application(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    application_id: str,
    status: str,
    reject_reason: str | None = None,
):
    if application_pb2 is None or application_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = application_pb2_grpc.ApplicationServiceStub(channel)
    req = application_pb2.DecideApplicationRequest(
        application_id=application_id,
        status=status,
        reject_reason=reject_reason or "",
    )
    return await stub.DecideApplication(req, metadata=_metadata(user_id, roles))


async def upload_document(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    application_id: str,
    document_type: str,
    file_content: bytes,
    content_type: str,
    filename: str,
):
    if application_pb2 is None or application_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = application_pb2_grpc.ApplicationServiceStub(channel)
    req = application_pb2.UploadDocumentRequest(
        application_id=application_id,
        document_type=document_type,
        file_content=file_content,
        content_type=content_type,
        filename=filename,
    )
    return await stub.UploadDocument(req, metadata=_metadata(user_id, roles))


async def get_document_download_url(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    application_id: str,
    document_id: str,
):
    if application_pb2 is None or application_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = application_pb2_grpc.ApplicationServiceStub(channel)
    req = application_pb2.GetDocumentDownloadUrlRequest(
        application_id=application_id,
        document_id=document_id,
    )
    return await stub.GetDocumentDownloadUrl(req, metadata=_metadata(user_id, roles))


def get_channel() -> grpc.aio.Channel:
    return grpc.aio.insecure_channel(APPLICATION_GRPC_URL)
