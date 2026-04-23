"""TravelPackage — pure domain entity.

LSP cure: the `before/` version had a `NonRefundablePackage(TravelPackage)`
subclass that overrode `.cancel()` to raise — breaking substitutability. The
capability "refundable" is now data on the base class, not a new type. Any
function accepting `TravelPackage` can iterate without fear of mid-loop
exceptions.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.package_status import PackageStatus


@dataclass(slots=True)
class TravelPackage:
    name: str
    destination: str
    base_price: Decimal
    refundable: bool
    status: PackageStatus = PackageStatus.ACTIVE
    cancelled_at: datetime | None = None
    traveler_id: int | None = None  # int, not TravelerId, to ease serialization
    id: PackageId | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if self.base_price < 0:
            raise ValueError("base_price cannot be negative")
