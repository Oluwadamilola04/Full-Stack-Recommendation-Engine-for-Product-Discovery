"""Database configuration and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

from app.core.config import settings

def _create_engine():
    database_url = settings.DATABASE_URL

    # SQLite needs different defaults (and doesn't support the same pooling options).
    if database_url.startswith("sqlite"):
        # Make relative SQLite paths stable regardless of current working directory.
        # Example: sqlite:///./ecommerce_recommendations.db should always live in backend/.
        if database_url.startswith("sqlite:///"):
            path_part = database_url[len("sqlite:///") :]
            is_windows_abs = ":" in path_part[:10]
            is_posix_abs = path_part.startswith("/")
            if not is_windows_abs and not is_posix_abs:
                backend_dir = Path(__file__).resolve().parents[2]
                abs_path = (backend_dir / path_part).resolve()
                database_url = f"sqlite:///{abs_path.as_posix()}"

        return create_engine(
            database_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )

    return create_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# Create database engine
engine = _create_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
