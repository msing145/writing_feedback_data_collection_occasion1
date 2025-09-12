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
    FRONTEND_ORIGINS: list[str] = ["http://localhost:8000", "https://localhost:8000", "null", "file://"]

    # Database (future: RDS/Aurora/etc.). Default stays SQLite for dev.
    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
    DATABASE_URL: str = f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}"


    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # In production, adjust settings
        if self.ENV == "production":
            self.DEBUG = False
            
settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
