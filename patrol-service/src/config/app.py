from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "patrol-service"
    log_level: str = "INFO"
    loki_url: str = ""
    grpc_port: int = 50052
    jwt_secret_key: str = "supersecretkey"
    environment: str = "development"


settings = AppSettings()
