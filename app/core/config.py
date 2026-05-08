from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fastapi-microservice"
    environment: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./fastapi_microservice.db"
    database_schema: str = "migros_store"
    log_level: str = "INFO"
    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 60
    api_request_logging_enabled: bool = True
    api_request_log_queue_size: int = 1000
    api_request_log_body_max_length: int = 4000
    cors_origins: str = "http://127.0.0.1:3000,http://localhost:3000"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @staticmethod
    def _split_csv(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return self._split_csv(self.cors_origins)

    @property
    def cors_allow_methods_list(self) -> list[str]:
        return self._split_csv(self.cors_allow_methods)

    @property
    def cors_allow_headers_list(self) -> list[str]:
        return self._split_csv(self.cors_allow_headers)


@lru_cache
def get_settings() -> Settings:
    return Settings()
