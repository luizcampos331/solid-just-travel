"""Traveler HTTP router.

DIP violation on display: the handler imports `SessionLocal` directly, constructs
a SQLAlchemy session inside the function body, and calls ORM methods. A unit test
for this handler would need a real database.
"""

from fastapi import APIRouter, HTTPException

from before.app.database import SessionLocal
from before.app.models import Traveler
from before.app.schemas import TravelerIn, TravelerOut

router = APIRouter(prefix="/travelers", tags=["travelers"])


@router.post("", response_model=TravelerOut, status_code=201)
def create_traveler(body: TravelerIn) -> TravelerOut:
    session = SessionLocal()  # ← DIP violation: handler owns infra
    try:
        traveler = Traveler(
            name=body.name,
            email=body.email,
            document=body.document,
        )
        traveler.validate()         # ← SRP violation leaks here
        traveler.save(session)      # ← SRP violation leaks here
        traveler.send_welcome_email()  # ← SRP violation leaks here
        return TravelerOut.model_validate(traveler)
    finally:
        session.close()


@router.get("", response_model=list[TravelerOut])
def list_travelers() -> list[TravelerOut]:
    session = SessionLocal()
    try:
        travelers = session.query(Traveler).all()
        return [TravelerOut.model_validate(t) for t in travelers]
    finally:
        session.close()


@router.get("/{traveler_id}", response_model=TravelerOut)
def get_traveler(traveler_id: int) -> TravelerOut:
    session = SessionLocal()
    try:
        traveler = session.get(Traveler, traveler_id)
        if traveler is None:
            raise HTTPException(status_code=404, detail="traveler not found")
        return TravelerOut.model_validate(traveler)
    finally:
        session.close()
