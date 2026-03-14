from io import BytesIO
from uuid import UUID, uuid4
from urllib.parse import urlsplit

from minio import Minio

from src.config import settings


class MinioStorage:
    def __init__(self) -> None:
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._bucket = settings.minio_bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def upload_report_image(
        self,
        report_id: UUID,
        category_id: UUID,
        filename: str,
        content_type: str,
        payload: bytes,
    ) -> str:
        object_name = f"reports/{report_id}/{category_id}/{uuid4()}_{filename}"
        stream = BytesIO(payload)
        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_name,
            data=stream,
            length=len(payload),
            content_type=content_type,
        )
        scheme = "https" if settings.minio_secure else "http"
        return f"{scheme}://{settings.minio_endpoint}/{self._bucket}/{object_name}"

    def delete_object_by_url(self, object_url: str) -> None:
        parsed = urlsplit(object_url)
        prefix = f"/{self._bucket}/"
        if parsed.path.startswith(prefix):
            object_name = parsed.path[len(prefix):]
            if object_name:
                self._client.remove_object(self._bucket, object_name)


_minio_storage: MinioStorage | None = None


def get_minio_storage() -> MinioStorage:
    global _minio_storage
    if _minio_storage is None:
        _minio_storage = MinioStorage()
    return _minio_storage
