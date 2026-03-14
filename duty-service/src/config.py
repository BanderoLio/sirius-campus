from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str
    service_port: int
    grpc_port: int
    environment: str
    log_level: str
    database_url: str
    auth_service_host: str
    auth_service_port: int
    grpc_timeout_seconds: float
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str
    minio_secure: bool
    request_audit_log_file: str


settings = Settings()
