from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.core.config import settings

if settings.database_url.startswith("sqlite"):
    sqlite_connect_args = {"check_same_thread": False}
    if ":memory:" in settings.database_url:
        engine = create_engine(
            settings.database_url,
            connect_args=sqlite_connect_args,
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            settings.database_url,
            connect_args=sqlite_connect_args,
            pool_pre_ping=True,
        )
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
