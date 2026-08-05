from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]

ENV_FILE_PATH = BACKEND_DIRECTORY / ".env"


class Settings(BaseSettings):
    app_name: str = "SkillBeacon"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    frontend_url: str = "http://localhost:5173"
    upload_directory: str = "uploads"
    max_upload_size_mb: int = 5

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        return [self.frontend_url]
    @property
    def upload_root(self) -> Path:
        return BACKEND_DIRECTORY / self.upload_directory


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()