from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthGrpcSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    auth_grpc_host: str = "localhost"
    auth_grpc_port: int = 50051
    grpc_timeout_seconds: int = 5
    grpc_max_retries: int = 3


auth_grpc_settings = AuthGrpcSettings()