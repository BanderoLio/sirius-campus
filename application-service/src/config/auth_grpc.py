from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthGrpcSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    grpc_url: str = "localhost:50051"


auth_grpc_settings = AuthGrpcSettings()
