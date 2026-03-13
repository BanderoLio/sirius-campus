"""Map domain models and gRPC proto messages. Uses generated application_pb2 at runtime."""

from datetime import datetime
from uuid import UUID


def _dt_iso(d: datetime | None) -> str:
    return d.isoformat() if d else ""


def _str_uuid(u: UUID | None) -> str:
    return str(u) if u else ""


def get_user_context_from_metadata(context) -> tuple[UUID | None, list[str]]:
    """Read x-user-id and x-user-roles from gRPC metadata. Keys are lowercased by gRPC."""
    user_id: UUID | None = None
    roles: list[str] = []
    for key, value in (context.invocation_metadata() or []):
        if key == "x-user-id" and value:
            try:
                user_id = UUID(value)
            except ValueError:
                pass
            break
    for key, value in (context.invocation_metadata() or []):
        if key == "x-user-roles" and value:
            roles = [r.strip() for r in value.split(",") if r.strip()]
            break
    return user_id, roles


def model_to_application_proto(pb2, model, user_name: str | None = None, room: str | None = None, entrance: int | None = None):
    """Convert domain application model to proto Application."""
    return pb2.Application(
        id=_str_uuid(getattr(model, "id", None)),
        user_id=_str_uuid(getattr(model, "user_id", None)),
        is_minor=getattr(model, "is_minor", False),
        leave_time=_dt_iso(getattr(model, "leave_time", None)),
        return_time=_dt_iso(getattr(model, "return_time", None)),
        reason=getattr(model, "reason", "") or "",
        contact_phone=getattr(model, "contact_phone", "") or "",
        status=getattr(model, "status", "") or "",
        decided_by=_str_uuid(getattr(model, "decided_by", None)),
        decided_at=_dt_iso(getattr(model, "decided_at", None)),
        reject_reason=getattr(model, "reject_reason", None) or "",
        created_at=_dt_iso(getattr(model, "created_at", None)),
        updated_at=_dt_iso(getattr(model, "updated_at", None)),
        user_name=user_name or "",
        room=room or "",
        entrance=entrance or 0,
    )


def model_to_document_proto(pb2, model):
    """Convert domain document model to proto Document."""
    return pb2.Document(
        id=_str_uuid(getattr(model, "id", None)),
        application_id=_str_uuid(getattr(model, "application_id", None)),
        document_type=getattr(model, "document_type", "") or "",
        file_url=getattr(model, "file_url", "") or "",
        uploaded_by=_str_uuid(getattr(model, "uploaded_by", None)),
        created_at=_dt_iso(getattr(model, "created_at", None)),
    )


def application_detail_to_proto(pb2, app_model, documents: list, can_decide: bool, user_name: str | None = None, room: str | None = None, entrance: int | None = None):
    """Build ApplicationDetail from application model and documents. Never pass None for base (protobuf serialize fails)."""
    base = model_to_application_proto(pb2, app_model, user_name=user_name, room=room, entrance=entrance)
    if base is None:
        base = pb2.Application()
    doc_list = [model_to_document_proto(pb2, d) for d in documents if d is not None]
    return pb2.ApplicationDetail(base=base, documents=doc_list, can_decide=can_decide)
