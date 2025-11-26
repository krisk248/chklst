"""Application configuration settings"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "chklst"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/chklst.db"
    DATABASE_ECHO: bool = False

    # Paths
    BASE_PATH: Path = Path(__file__).parent.parent
    DATA_PATH: Path = BASE_PATH / "data"
    REPORTS_PATH: Path = BASE_PATH / "reports"
    PROJECTS_PATH: Path = BASE_PATH / "projects"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list = ["*"]

    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list = ["*"]

    # WebSocket
    WEBSOCKET_PING_INTERVAL: float = 20.0
    WEBSOCKET_PING_TIMEOUT: float = 10.0

    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


settings = get_settings()
