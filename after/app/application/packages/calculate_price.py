"""CalculatePackagePrice use case.

Composes with a DiscountPolicy. A new discount type is a new policy class
— the use case itself never changes. That is OCP.
"""

from decimal import Decimal

from after.app.domain.packages.discount_policy import DiscountPolicy
from after.app.domain.packages.travel_package import TravelPackage


class CalculatePackagePrice:
    def __init__(self, policy: DiscountPolicy):
        self._policy = policy

    def execute(self, package: TravelPackage) -> Decimal:
        return self._policy.apply(package)
