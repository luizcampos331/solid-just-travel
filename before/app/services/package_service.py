"""Package service.

Two intentional violations on display:

1. OCP: `calculate_price()` uses `if/elif` per discount type — every new discount
   forces editing this function, risking regression.

2. ISP: `PackageRepository` exposes 12 methods, while `CreatePackageHandler` only
   needs `add()`. Writing a fake for tests becomes a nightmare.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from before.app.models import TravelPackage


# --- OCP violation: discount selection via if/elif ---
def calculate_price(package: TravelPackage, discount_type: str) -> float:
    """Compute the final price of `package` for the given discount kind.

    Adding a new discount type means editing this function — the exact signature
    of OCP violation.
    """
    price = package.base_price

    if discount_type == "seasonal":
        price *= 0.85
    elif discount_type == "black_friday":
        price *= 0.70
    elif discount_type == "corporate":
        price = max(0.0, price - 200.0)
    elif discount_type == "cyber_monday":
        # Added last week; now we have four branches and counting.
        price *= 0.75 if package.base_price > 5000 else 0.90
    elif discount_type == "none":
        price = price
    else:
        raise ValueError(f"unknown discount_type: {discount_type}")

    return round(price, 2)


# --- ISP violation: fat repository interface ---
class PackageRepository:
    """A 12-method repository.

    The `CreatePackage` flow only needs `add()`, yet every test double has to
    implement — or raise NotImplementedError for — all 12 methods. That is ISP
    screaming for help.
    """

    def __init__(self, session: Session):
        self._session = session

    def add(self, package: TravelPackage) -> TravelPackage:
        self._session.add(package)
        self._session.commit()
        self._session.refresh(package)
        return package

    def by_id(self, package_id: int) -> TravelPackage | None:
        return self._session.get(TravelPackage, package_id)

    def list(self) -> list[TravelPackage]:
        return list(self._session.query(TravelPackage).all())

    def update(self, package: TravelPackage) -> TravelPackage:
        self._session.commit()
        return package

    def delete(self, package_id: int) -> None:
        pkg = self.by_id(package_id)
        if pkg is not None:
            self._session.delete(pkg)
            self._session.commit()

    def find_by_destination(self, destination: str) -> list[TravelPackage]:
        return list(
            self._session.query(TravelPackage).filter_by(destination=destination).all()
        )

    def find_by_price_range(self, lo: float, hi: float) -> list[TravelPackage]:
        return list(
            self._session.query(TravelPackage)
            .filter(TravelPackage.base_price >= lo)
            .filter(TravelPackage.base_price <= hi)
            .all()
        )

    def paginated(self, page: int, size: int = 10) -> list[TravelPackage]:
        return list(
            self._session.query(TravelPackage)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

    def count_by_traveler(self, traveler_id: int) -> int:
        return (
            self._session.query(TravelPackage)
            .filter_by(traveler_id=traveler_id)
            .count()
        )

    def upsert(self, package: TravelPackage) -> TravelPackage:
        self._session.merge(package)
        self._session.commit()
        return package

    def archive(self, package_id: int) -> None:
        pkg = self.by_id(package_id)
        if pkg is not None:
            pkg.status = "archived"
            self._session.commit()

    def bulk_insert(self, packages: list[TravelPackage]) -> None:
        self._session.add_all(packages)
        self._session.commit()
