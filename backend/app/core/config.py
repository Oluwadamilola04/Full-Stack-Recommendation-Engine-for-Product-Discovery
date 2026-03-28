"""Application configuration"""

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "change-me-in-production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    # Default to SQLite so the API can run locally without PostgreSQL.
    # If you have Postgres running, set DATABASE_URL in backend/.env instead.
    DATABASE_URL: str = "sqlite:///./ecommerce_recommendations.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ML Models
    MODEL_PATH: str = "./ml/models"
    BATCH_SIZE: int = 32
    EMBEDDING_DIM: int = 50
    AUTO_LOAD_DEMO_DATA: bool = False

    # Prefix avoids collisions with common system env vars like DEBUG.
    # Use an absolute path so running scripts from repo root still loads backend/.env.
    _backend_dir = Path(__file__).resolve().parents[2]
    model_config = SettingsConfigDict(
        env_file=str(_backend_dir / ".env"), env_prefix="ECRS_", extra="ignore"
    )


settings = Settings()

