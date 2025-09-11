from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Writing Data Collection API"
    FRONTEND_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "null", "file://"]
    # SQLite database in ./data directory
    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
    DATABASE_URL: str = f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
# ensure data dir exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
