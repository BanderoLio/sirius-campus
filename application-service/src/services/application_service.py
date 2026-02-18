from datetime import date, datetime
from uuid import UUID

from src.constants.document_type import (
    DOCUMENT_TYPES,
    DOCUMENT_TYPE_VOICE_MESSAGE,
    MAX_SCAN_SIZE_BYTES,
    MAX_VOICE_SIZE_BYTES,
    SCAN_ALLOWED_EXTENSIONS,
    VOICE_ALLOWED_EXTENSIONS,
)
from src.domain.exceptions import (
    ApplicationAlreadyDecidedError,
    ApplicationNotFoundError,
    ForbiddenApplicationError,
    InvalidDocumentTypeError,
    MinorVoiceRequiredError,
)
from src.grpc_clients.auth_client import AuthClientProtocol
from src.repositories.application_document_repository import ApplicationDocumentRepository
from src.repositories.application_repository import ApplicationRepository
from src.storage.minio_storage import MinioStorage


class ApplicationService:
    def __init__(
        self,
        application_repository: ApplicationRepository,
        document_repository: ApplicationDocumentRepository,
        storage: MinioStorage,
        auth_client: AuthClientProtocol,
    ) -> None:
        self._app_repo = application_repository
        self._doc_repo = document_repository
        self._storage = storage
        self._auth = auth_client

    async def create_application(
        self,
        user_id: UUID,
        leave_time: datetime,
        return_time: datetime,
        reason: str,
        contact_phone: str,
    ) -> tuple[object, bool]:
        user_info = await self._auth.get_user_info(str(user_id))
        if not user_info:
            raise ForbiddenApplicationError()
        is_minor = user_info.is_minor
        model = await self._app_repo.create(
            user_id=user_id,
            is_minor=is_minor,
            leave_time=leave_time,
            return_time=return_time,
            reason=reason,
            contact_phone=contact_phone,
        )
        return model, is_minor

    async def ensure_minor_voice_if_required(self, application_id: UUID) -> None:
        app = await self._app_repo.get_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError(str(application_id))
        if not app.is_minor:
            return
        count = await self._doc_repo.count_voice_messages_for_application(application_id)
        if count == 0:
            raise MinorVoiceRequiredError()

    async def list_applications(
        self,
        *,
        user_id: UUID | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[object], int]:
        items, total = await self._app_repo.get_list(
            user_id=user_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            page=page,
            size=size,
        )
        return items, total

    async def get_application(
        self,
        application_id: UUID,
        current_user_id: UUID,
        current_user_roles: list[str],
    ) -> object:
        app = await self._app_repo.get_by_id_with_documents(application_id)
        if not app:
            raise ApplicationNotFoundError(str(application_id))
        is_owner = app.user_id == current_user_id
        is_educator = any(
            r in current_user_roles for r in ("educator", "educator_head", "admin")
        )
        if not is_owner and not is_educator:
            raise ForbiddenApplicationError()
        return app

    async def decide_application(
        self,
        application_id: UUID,
        status: str,
        decided_by: UUID,
        decided_at: datetime,
        reject_reason: str | None = None,
    ) -> object:
        app = await self._app_repo.get_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError(str(application_id))
        if app.status != "pending":
            raise ApplicationAlreadyDecidedError()
        if status not in ("approved", "rejected"):
            raise InvalidDocumentTypeError(f"status={status}")
        if app.is_minor:
            count = await self._doc_repo.count_voice_messages_for_application(application_id)
            if count == 0:
                raise MinorVoiceRequiredError()
        updated = await self._app_repo.update_status(
            application_id=application_id,
            status=status,
            decided_by=decided_by,
            decided_at=decided_at,
            reject_reason=reject_reason,
        )
        return updated

    async def upload_document(
        self,
        application_id: UUID,
        document_type: str,
        file_data: bytes,
        content_type: str,
        filename: str,
        uploaded_by: UUID,
    ) -> object:
        if document_type not in DOCUMENT_TYPES:
            raise InvalidDocumentTypeError(document_type)
        app = await self._app_repo.get_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError(str(application_id))
        if app.user_id != uploaded_by:
            raise ForbiddenApplicationError()
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if document_type == DOCUMENT_TYPE_VOICE_MESSAGE:
            if ext not in VOICE_ALLOWED_EXTENSIONS:
                raise InvalidDocumentTypeError(f"voice extension .{ext}")
            if len(file_data) > MAX_VOICE_SIZE_BYTES:
                raise InvalidDocumentTypeError("voice file too large")
        else:
            if ext not in SCAN_ALLOWED_EXTENSIONS:
                raise InvalidDocumentTypeError(f"scan extension .{ext}")
            if len(file_data) > MAX_SCAN_SIZE_BYTES:
                raise InvalidDocumentTypeError("scan file too large")
        from uuid import uuid4

        doc_id = uuid4()
        object_name = await self._storage.upload_file(
            application_id=application_id,
            document_id=doc_id,
            data=file_data,
            content_type=content_type,
            extension=ext,
        )
        doc = await self._doc_repo.create(
            application_id=application_id,
            document_type=document_type,
            file_url=object_name,
            uploaded_by=uploaded_by,
            document_id=doc_id,
        )
        return doc

    async def get_approved_leaves_for_date(
        self,
        leave_date: date,
        building: str | None = None,
        entrance: int | None = None,
    ) -> list[tuple[str, str, str, datetime, datetime, str]]:
        applications = await self._app_repo.get_approved_for_leave_date(
            leave_date=leave_date,
            building=building,
        )
        result: list[tuple[str, str, str, datetime, datetime, str]] = []
        for app in applications:
            user_info = await self._auth.get_user_info(str(app.user_id))
            user_name = ""
            room = ""
            if user_info:
                if building and user_info.building != building:
                    continue
                if entrance is not None and entrance != 0 and user_info.entrance != entrance:
                    continue
                user_name = f"{user_info.last_name} {user_info.first_name} {user_info.patronymic or ''}".strip()
                room = user_info.room
            result.append(
                (
                    str(app.user_id),
                    user_name,
                    room,
                    app.leave_time,
                    app.return_time,
                    app.reason,
                )
            )
        return result
