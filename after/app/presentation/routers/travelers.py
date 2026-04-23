"""Traveler HTTP router — thin handlers, DIP-clean.

Each handler is 3-5 lines: parse input, call use case, format output. No
SQLAlchemy import, no business rules, no inline validation.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from after.app.application.travelers.create_traveler import CreateTraveler
from after.app.application.travelers.get_traveler import GetTraveler, TravelerNotFound
from after.app.application.travelers.list_travelers import ListTravelers
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.presentation.dependencies import (
    get_create_traveler_uc,
    get_get_traveler_uc,
    get_list_travelers_uc,
)
from after.app.presentation.schemas import TravelerIn, TravelerOut

router = APIRouter(prefix="/travelers", tags=["travelers"])


@router.post("", response_model=TravelerOut, status_code=201)
def create_traveler(
    body: TravelerIn,
    use_case: Annotated[CreateTraveler, Depends(get_create_traveler_uc)],
) -> TravelerOut:
    try:
        traveler = use_case.execute(body.to_input())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return TravelerOut.from_domain(traveler)


@router.get("", response_model=list[TravelerOut])
def list_travelers(
    use_case: Annotated[ListTravelers, Depends(get_list_travelers_uc)],
) -> list[TravelerOut]:
    return [TravelerOut.from_domain(t) for t in use_case.execute()]


@router.get("/{traveler_id}", response_model=TravelerOut)
def get_traveler(
    traveler_id: int,
    use_case: Annotated[GetTraveler, Depends(get_get_traveler_uc)],
) -> TravelerOut:
    try:
        traveler = use_case.execute(TravelerId(traveler_id))
    except TravelerNotFound:
        raise HTTPException(status_code=404, detail="traveler not found")
    return TravelerOut.from_domain(traveler)
