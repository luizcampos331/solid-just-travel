"""DiscountPolicy — Protocol + strategies.

OCP cure: in `before/`, adding a new discount type meant editing
`calculate_price`'s `if/elif` chain. Here, a new discount is a new class
that implements `DiscountPolicy` — zero edit to existing code.

The strategies match the 5 discount types from `before/` exactly, so
equivalence contracts pass without change:

- seasonal: 15% off
- black_friday: 30% off
- corporate: flat -200 (floored at 0)
- cyber_monday: 25% off if base > 5000, else 10%
- none: unchanged
"""

from decimal import Decimal
from typing import Protocol

from after.app.domain.packages.travel_package import TravelPackage


class DiscountPolicy(Protocol):
    def apply(self, package: TravelPackage) -> Decimal: ...


class NoDiscount:
    def apply(self, package: TravelPackage) -> Decimal:
        return package.base_price


class SeasonalDiscount:
    def apply(self, package: TravelPackage) -> Decimal:
        return (package.base_price * Decimal("0.85")).quantize(Decimal("0.01"))


class BlackFridayDiscount:
    def apply(self, package: TravelPackage) -> Decimal:
        return (package.base_price * Decimal("0.70")).quantize(Decimal("0.01"))


class CorporateDiscount:
    FLAT_OFF = Decimal("200.00")

    def apply(self, package: TravelPackage) -> Decimal:
        return max(Decimal("0"), package.base_price - self.FLAT_OFF)


class CyberMondayDiscount:
    THRESHOLD = Decimal("5000")

    def apply(self, package: TravelPackage) -> Decimal:
        factor = Decimal("0.75") if package.base_price > self.THRESHOLD else Decimal("0.90")
        return (package.base_price * factor).quantize(Decimal("0.01"))
