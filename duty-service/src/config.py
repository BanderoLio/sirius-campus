from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "duty-service"
    service_port: int = 8003
    grpc_port: int = 50053
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://user:password@db:5432/duty_db"
    auth_service_host: str = "auth-service"
    auth_service_port: int = 50051
    grpc_timeout_seconds: float = 5.0


settings = Settings()
