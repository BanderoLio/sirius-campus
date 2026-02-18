import asyncio
from datetime import timedelta
from io import BytesIO
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from src.config import minio_settings


class MinioStorage:
    def __init__(self) -> None:
        self._client = Minio(
            minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.secure,
        )
        self._presign_client = (
            Minio(
                minio_settings.public_endpoint,
                access_key=minio_settings.access_key,
                secret_key=minio_settings.secret_key,
                secure=minio_settings.secure,
                region="us-east-1",
            )
            if minio_settings.public_endpoint
            else self._client
        )
        self._bucket = minio_settings.bucket_applications

    def _ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except S3Error:
            pass

    async def upload_file(
        self,
        application_id: UUID,
        document_id: UUID,
        data: bytes,
        content_type: str,
        extension: str,
    ) -> str:
        def _put() -> str:
            self._ensure_bucket()
            object_name = f"{application_id}/{document_id}.{extension}"
            self._client.put_object(
                self._bucket,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            return object_name

        return await asyncio.to_thread(_put)

    async def get_presigned_download_url(
        self,
        object_name: str,
        expiry_seconds: int = 3600,
    ) -> str:
        def _presign() -> str:
            return self._presign_client.presigned_get_object(
                self._bucket,
                object_name,
                expires=timedelta(seconds=expiry_seconds),
            )

        return await asyncio.to_thread(_presign)

    async def get_object(
        self,
        object_name: str,
    ) -> tuple[bytes, str]:
        """Get object bytes and content_type. Uses internal endpoint (no public URL)."""

        def _get() -> tuple[bytes, str]:
            self._ensure_bucket()
            response = self._client.get_object(self._bucket, object_name)
            try:
                data = response.read()
                content_type = (
                    response.headers.get("Content-Type")
                    if hasattr(response.headers, "get")
                    else getattr(response, "content_type", None)
                ) or "application/octet-stream"
                return data, content_type
            finally:
                response.close()

        return await asyncio.to_thread(_get)
