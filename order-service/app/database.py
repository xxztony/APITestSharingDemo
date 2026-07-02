import os
import time
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _database_url() -> str:
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "trading_demo")
    user = os.getenv("MYSQL_USER", "demo_user")
    password = os.getenv("MYSQL_PASSWORD", "demo_password")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


engine = create_engine(_database_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def wait_for_database(retries: int = 40, delay_seconds: float = 2.0) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except Exception as exc:  # pragma: no cover - only used during container startup
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"Database is not ready: {last_error}") from last_error


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

