"""Pytest fixtures for `after/` tests.

Compared to `before/tests/conftest.py`, this is dramatically simpler. DIP
cure in action: we override ONE dependency (`get_db`) instead of
monkeypatching SessionLocal in three module-level locations. The
application remains strictly strict about errors — no `raise_server_exceptions=False`
needed for equivalence tests because the LSP bomb no longer exists.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from after.app.infra.database import Base
from after.app.infra.persistence import models  # noqa: F401
from after.app.main import app as fastapi_app
from after.app.presentation.dependencies import get_db


@pytest.fixture
def test_engine():
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
def client(test_engine):
    """Strict TestClient with a dependency override for the DB session.

    ONE override replaces all three `SessionLocal` monkeypatches from
    `before/`. That single line IS the DIP payoff.
    """
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()
