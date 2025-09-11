from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Writing Data Collection API"

    # Deploy / logging
    ENV: str = "development"          # development | staging | production
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Frontend origins (comma-separated or JSON list)
    FRONTEND_ORIGINS: list[str] = ["http://localhost:8000", "null", "file://"]

    # Database (future: RDS/Aurora/etc.). Default stays SQLite for dev.
    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
    DATABASE_URL: str = f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}"

    # ---- AWS (optional; if unset, S3 is disabled) ----
    STORE_ESSAY_S3: bool = False
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_PREFIX: str = "writing-feedback/"  # will prefix all keys, e.g. "writing-feedback/essays/..."
    AWS_PROFILE: Optional[str] = None         # optional: local dev profile
    AWS_KMS_KEY_ID: Optional[str] = None      # optional: use KMS instead of SSE-S3

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
