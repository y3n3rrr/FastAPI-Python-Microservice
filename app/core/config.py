from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fastapi-microservice"
    environment: str = "development"
    debug: bool = True
    database_url: str
    database_schema: str = "bookstore"
    log_level: str = "INFO"
    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 60
    api_request_logging_enabled: bool = True
    api_request_log_queue_size: int = 1000
    api_request_log_body_max_length: int = 4000

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
