from datetime import datetime
from uuid import UUID


class Application:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        is_minor: bool,
        leave_time: datetime,
        return_time: datetime,
        reason: str,
        contact_phone: str,
        status: str,
        created_at: datetime,
        updated_at: datetime,
        decided_by: UUID | None = None,
        decided_at: datetime | None = None,
        reject_reason: str | None = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_minor = is_minor
        self.leave_time = leave_time
        self.return_time = return_time
        self.reason = reason
        self.contact_phone = contact_phone
        self.status = status
        self.decided_by = decided_by
        self.decided_at = decided_at
        self.reject_reason = reject_reason
        self.created_at = created_at
        self.updated_at = updated_at


class ApplicationDocument:
    def __init__(
        self,
        id: UUID,
        application_id: UUID,
        document_type: str,
        file_url: str,
        uploaded_by: UUID,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = id
        self.application_id = application_id
        self.document_type = document_type
        self.file_url = file_url
        self.uploaded_by = uploaded_by
        self.created_at = created_at
        self.updated_at = updated_at
