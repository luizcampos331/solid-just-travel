"""SqlAlchemyPackageRepository — satisfies BOTH PackageWriter and PackageReader.

The ISP cure at the domain level: clients see segregated interfaces. The
concrete adapter can still unify implementation — separation of concern
was about the CONTRACT surface, not the implementation.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.travel_package import TravelPackage
from after.app.infra.persistence.models import PackageModel


def _to_domain(row: PackageModel) -> TravelPackage:
    return TravelPackage(
        name=row.name,
        destination=row.destination,
        base_price=Decimal(str(row.base_price)),
        refundable=bool(row.refundable),
        status=PackageStatus(row.status),
        cancelled_at=row.cancelled_at,
        traveler_id=row.traveler_id,
        id=PackageId(row.id),
    )


def _to_row(p: TravelPackage) -> PackageModel:
    return PackageModel(
        name=p.name,
        destination=p.destination,
        base_price=p.base_price,
        refundable=p.refundable,
        status=p.status.value,
        cancelled_at=p.cancelled_at,
        traveler_id=p.traveler_id,
    )


class SqlAlchemyPackageRepository:
    def __init__(self, session: Session):
        self._session = session

    # --- PackageWriter ---
    def add(self, package: TravelPackage) -> TravelPackage:
        row = _to_row(package)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return _to_domain(row)

    def update(self, package: TravelPackage) -> TravelPackage:
        assert package.id is not None, "update requires persisted package"
        row = self._session.get(PackageModel, int(package.id))
        if row is None:
            raise LookupError(f"package {package.id} not found")
        row.name = package.name
        row.destination = package.destination
        row.base_price = package.base_price
        row.refundable = package.refundable
        row.status = package.status.value
        row.cancelled_at = package.cancelled_at
        row.traveler_id = package.traveler_id
        self._session.commit()
        self._session.refresh(row)
        return _to_domain(row)

    # --- PackageReader ---
    def by_id(self, package_id: PackageId) -> TravelPackage | None:
        row = self._session.get(PackageModel, int(package_id))
        return _to_domain(row) if row is not None else None

    def list(self) -> list[TravelPackage]:
        rows = self._session.query(PackageModel).all()
        return [_to_domain(r) for r in rows]

    def by_traveler(self, traveler_id: int) -> list[TravelPackage]:
        rows = (
            self._session.query(PackageModel)
            .filter(PackageModel.traveler_id == traveler_id)
            .all()
        )
        return [_to_domain(r) for r in rows]
