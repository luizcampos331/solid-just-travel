"""CreatePackage use case.

Note: depends ONLY on `PackageWriter`, not the full repo. Even if a future
refactor adds 10 reader methods, this use case — and its fake in tests —
does not grow.
"""

from dataclasses import dataclass
from decimal import Decimal

from after.app.domain.packages.package_repository import PackageWriter
from after.app.domain.packages.travel_package import TravelPackage


@dataclass(slots=True)
class CreatePackageInput:
    name: str
    destination: str
    base_price: Decimal
    refundable: bool
    traveler_id: int | None = None


class CreatePackage:
    def __init__(self, writer: PackageWriter):
        self._writer = writer

    def execute(self, input: CreatePackageInput) -> TravelPackage:
        package = TravelPackage(
            name=input.name,
            destination=input.destination,
            base_price=input.base_price,
            refundable=input.refundable,
            traveler_id=input.traveler_id,
        )
        return self._writer.add(package)
