"""Package HTTP router.

Contains:
- DIP violation: same `SessionLocal` + ORM coupling as `travelers.py`.
- Inline price calculation call (OCP).
- `cancel_all_of_traveler` endpoint that triggers the LSP bomb on purpose.
"""

from fastapi import APIRouter, HTTPException

from before.app.database import SessionLocal
from before.app.models import NonRefundablePackage, TravelPackage
from before.app.schemas import PackageIn, PackageOut, PriceCalcIn, PriceCalcOut
from before.app.services.booking_service import cancel_all_of_traveler
from before.app.services.package_service import PackageRepository, calculate_price

router = APIRouter(tags=["packages"])


def _build_package(body: PackageIn) -> TravelPackage:
    """Pick the right subclass based on `kind` — fragile pattern we'll remove."""
    if body.kind == "non_refundable":
        return NonRefundablePackage(
            name=body.name,
            destination=body.destination,
            base_price=body.base_price,
            kind="non_refundable",
            traveler_id=body.traveler_id,
        )
    return TravelPackage(
        name=body.name,
        destination=body.destination,
        base_price=body.base_price,
        kind="standard",
        traveler_id=body.traveler_id,
    )


@router.post("/packages", response_model=PackageOut, status_code=201)
def create_package(body: PackageIn) -> PackageOut:
    session = SessionLocal()
    try:
        repo = PackageRepository(session)  # ← ISP: we only need `add`, repo has 12 methods
        package = _build_package(body)
        repo.add(package)
        return PackageOut.model_validate(package)
    finally:
        session.close()


@router.get("/packages", response_model=list[PackageOut])
def list_packages() -> list[PackageOut]:
    session = SessionLocal()
    try:
        packages = session.query(TravelPackage).all()
        return [PackageOut.model_validate(p) for p in packages]
    finally:
        session.close()


@router.post("/packages/{package_id}/price", response_model=PriceCalcOut)
def price_of_package(package_id: int, body: PriceCalcIn) -> PriceCalcOut:
    session = SessionLocal()
    try:
        package = session.get(TravelPackage, package_id)
        if package is None:
            raise HTTPException(status_code=404, detail="package not found")
        final = calculate_price(package, body.discount_type)  # ← OCP: see inside
        return PriceCalcOut(
            package_id=package.id,
            discount_type=body.discount_type,
            base_price=package.base_price,
            final_price=final,
        )
    finally:
        session.close()


@router.delete("/travelers/{traveler_id}/packages", status_code=200)
def cancel_all(traveler_id: int) -> dict:
    """Cancel ALL packages of a traveler — designed to trip the LSP bomb.

    If the traveler owns at least one NonRefundablePackage, this handler will
    return a 500 AFTER cancelling some of the packages. That partial failure IS
    the pedagogical moment we want during the talk.
    """
    session = SessionLocal()
    try:
        count = cancel_all_of_traveler(session, traveler_id)
        return {"cancelled": count}
    finally:
        session.close()
