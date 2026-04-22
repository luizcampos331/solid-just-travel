"""Pytest fixtures for `before/` equivalence-contract tests.

These contracts MUST pass identically in both `before/` and `after/` (Plan B).
They describe observable behavior through the HTTP API — never internal structure.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Explicit import so SQLAlchemy registers all ORM models on Base.metadata
# before `create_all` runs. Do not remove.
from before.app import models  # noqa: F401
from before.app import database as db_module
from before.app.database import Base
from before.app.main import app as fastapi_app


@pytest.fixture
def test_engine():
    """Per-test SQLite engine in-memory with a StaticPool.

    StaticPool + `check_same_thread=False` ensures that every checkout of a
    connection from the pool returns the SAME underlying in-memory database —
    otherwise DDL created in one connection is invisible to another.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_engine, monkeypatch):
    """FastAPI TestClient wired to the in-memory test engine.

    Monkeypatches `SessionLocal` everywhere it is bound. This is ugly — and it IS
    the DIP violation we show on stage. The `after/` version uses `Depends()` and
    needs a single clean override.

    `raise_server_exceptions=False` is required so the LSP-bomb test can assert
    the 500 HTTP response instead of having the underlying ValueError re-raised.
    """
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestSession)
    monkeypatch.setattr("before.app.routers.travelers.SessionLocal", TestSession)
    monkeypatch.setattr("before.app.routers.packages.SessionLocal", TestSession)

    with TestClient(fastapi_app, raise_server_exceptions=False) as c:
        yield c
