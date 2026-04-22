"""SQLAlchemy engine, session factory and declarative base.

This module wires SQLAlchemy directly at import time — that is the whole point of the
`before/` version. The `after/` version will invert this so the domain has no idea
SQLAlchemy exists.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./before.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM-mapped classes."""
    pass


def get_db():
    """FastAPI dependency that yields a SQLAlchemy session per request.

    Note: handlers in `before/` bypass this and import `SessionLocal` directly —
    that is the DIP violation we want to show.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
