"""FastAPI entrypoint for the `before/` version.

Run:
    uv run uvicorn before.app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from before.app.database import Base, engine
from before.app import models  # noqa: F401 — register ORM models with Base.metadata
from before.app.routers import packages, travelers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables at startup — good enough for the demo."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Just Travel — SOLID talk (BEFORE)",
    description=(
        "Versão ingênua do CRUD com violações SOLID curadas. "
        "Veja `after/` para a versão refatorada."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(travelers.router)
app.include_router(packages.router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "version": f"before/{app.version}"}
