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
    FRONTEND_ORIGINS: list[str] = [
        "http://localhost:8000",
        "https://localhost:8000",
        "null",
        "file://"
    ]

    # Database
    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
    DATABASE_URL: Optional[str] = None  # Will be resolved below

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # If no DATABASE_URL set (e.g., local dev), default to SQLite
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"sqlite:///{(self.DATA_DIR / 'app.db').as_posix()}"

        # In production, enforce DEBUG=False
        if self.ENV == "production":
            self.DEBUG = False

settings = Settings()

# Make sure SQLite folder exists locally
if settings.DATABASE_URL.startswith("sqlite"):
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
