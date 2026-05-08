from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    environment: str
    debug: bool
    database_url: str
    database_schema: str
    log_level: str
    jwt_secret_key: str
    jwt_access_token_expire_minutes: int
    api_request_logging_enabled: bool
    api_request_log_queue_size: int
    api_request_log_body_max_length: int
    cors_origins: str
    cors_allow_credentials: bool
    cors_allow_methods: str
    cors_allow_headers: str
    assistant_llm_provider: str
    assistant_ollama_base_url: str
    assistant_ollama_model: str
    assistant_ollama_timeout_seconds: int

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
