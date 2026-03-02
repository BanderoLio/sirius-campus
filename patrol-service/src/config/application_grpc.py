from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationGrpcSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    application_grpc_host: str = "localhost"
    application_grpc_port: int = 50055


application_grpc_settings = ApplicationGrpcSettings()