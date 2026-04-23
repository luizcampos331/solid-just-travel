"""FastAPI entrypoint for the `after/` version.

Run:
    uv run uvicorn after.app.main:app --port 8001 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from after.app.infra.database import Base, engine
from after.app.infra.persistence import models  # noqa: F401 — register on Base.metadata
from after.app.presentation.routers import packages, travelers


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Just Travel — SOLID talk (AFTER)",
    description=(
        "Versão refatorada do CRUD com Clean Arch minimalista e SOLID aplicado. "
        "Comportamento HTTP idêntico ao `before/` — veja tests/test_equivalence_contracts.py."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(travelers.router)
app.include_router(packages.router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "version": f"after/{app.version}"}
