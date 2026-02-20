from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MINIO_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    endpoint: str = "localhost:9000"
    """Endpoint for server-to-MinIO requests (e.g. minio:9000 in Docker)."""
    public_endpoint: str | None = None
    """Endpoint for presigned URLs so the browser can reach MinIO (e.g. localhost:9000). If set, presigned URLs are signed for this host."""
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket_applications: str = "applications"
    secure: bool = False


minio_settings = MinioSettings()
