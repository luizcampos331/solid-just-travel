"""Package HTTP router.

Owns /packages* plus the DELETE /travelers/{id}/packages endpoint. The
cancel-all endpoint now returns 200 + partial-result JSON — the LSP bomb
is gone.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from after.app.application.packages.calculate_price import CalculatePackagePrice
from after.app.application.packages.cancel_all_of_traveler import CancelAllOfTraveler
from after.app.application.packages.create_package import CreatePackage
from after.app.application.packages.list_packages import ListPackages
from after.app.domain.packages.package_id import PackageId
from after.app.presentation.dependencies import (
    calculate_price_uc_for,
    get_cancel_all_uc,
    get_create_package_uc,
    get_list_packages_uc,
    get_package_repo,
)
from after.app.presentation.schemas import (
    CancelResultOut,
    PackageIn,
    PackageOut,
    PriceCalcIn,
    PriceCalcOut,
)

router = APIRouter(tags=["packages"])


@router.post("/packages", response_model=PackageOut, status_code=201)
def create_package(
    body: PackageIn,
    use_case: Annotated[CreatePackage, Depends(get_create_package_uc)],
) -> PackageOut:
    return PackageOut.from_domain(use_case.execute(body.to_input()))


@router.get("/packages", response_model=list[PackageOut])
def list_packages(
    use_case: Annotated[ListPackages, Depends(get_list_packages_uc)],
) -> list[PackageOut]:
    return [PackageOut.from_domain(p) for p in use_case.execute()]


@router.post("/packages/{package_id}/price", response_model=PriceCalcOut)
def price_of_package(
    package_id: int,
    body: PriceCalcIn,
    repo: Annotated[
        "SqlAlchemyPackageRepository",  # noqa: F821 — string avoids circular
        Depends(get_package_repo),
    ],
) -> PriceCalcOut:
    package = repo.by_id(PackageId(package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="package not found")
    try:
        use_case = calculate_price_uc_for(body.discount_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    final = use_case.execute(package)
    return PriceCalcOut(
        package_id=int(package.id) if package.id is not None else 0,
        discount_type=body.discount_type,
        base_price=float(package.base_price),
        final_price=float(final),
    )


@router.delete("/travelers/{traveler_id}/packages", response_model=CancelResultOut)
def cancel_all(
    traveler_id: int,
    use_case: Annotated[CancelAllOfTraveler, Depends(get_cancel_all_uc)],
) -> CancelResultOut:
    result = use_case.execute(traveler_id=traveler_id)
    return CancelResultOut(
        cancelled=len(result.cancelled),
        cancelled_ids=[int(p.id) for p in result.cancelled if p.id is not None],
        skipped_ids=[int(p.id) for p in result.skipped if p.id is not None],
    )
