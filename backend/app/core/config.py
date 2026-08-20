from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]

ENV_FILE_PATH = BACKEND_DIRECTORY / ".env"
LOCAL_ENV_FILE_PATH = BACKEND_DIRECTORY / ".env.local"


class Settings(BaseSettings):
    app_name: str = "SkillBeacon"
    app_env: str = "development"
    debug: bool = True

    database_url: str
    database_url_unpooled: str | None = None

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    frontend_url: str = "http://localhost:5173"
    upload_directory: str = "uploads"
    max_upload_size_mb: int = 5

    neon_auth_base_url: str
    neon_auth_jwks_url: str

    # Cloudflare R2 / S3 Object Storage
    cloudflare_account_id: str
    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_base_url: str
    user_storage_quota_mb: int = 50
    employer_storage_quota_mb: int = 100

    app_profile: str = "main"

    model_config = SettingsConfigDict(
        env_file=(ENV_FILE_PATH, LOCAL_ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_local_profile(self) -> bool:
        return self.app_profile.strip().lower() == "local"

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