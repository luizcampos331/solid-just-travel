"""Unit tests for CalculatePackagePrice — each strategy isolated.

This is the OCP payoff: 6 test cases, each exercising a different policy
with ZERO setup — the use case composes policies without a banco.
"""

from decimal import Decimal

import pytest

from after.app.application.packages.calculate_price import CalculatePackagePrice
from after.app.domain.packages.discount_policy import (
    BlackFridayDiscount,
    CorporateDiscount,
    CyberMondayDiscount,
    NoDiscount,
    SeasonalDiscount,
)
from after.app.domain.packages.travel_package import TravelPackage


def _pkg(price: str) -> TravelPackage:
    return TravelPackage(
        name="p", destination="x", base_price=Decimal(price), refundable=True
    )


@pytest.mark.parametrize(
    "policy, base, expected",
    [
        (NoDiscount(),           "1000", "1000"),
        (SeasonalDiscount(),     "1000",  "850.00"),
        (BlackFridayDiscount(),  "1000",  "700.00"),
        (CorporateDiscount(),    "1000",  "800.00"),
        (CyberMondayDiscount(),  "6000", "4500.00"),
        (CyberMondayDiscount(),  "2000", "1800.00"),
    ],
)
def test_price_per_policy(policy, base, expected):
    result = CalculatePackagePrice(policy).execute(_pkg(base))
    assert result == Decimal(expected)


def test_corporate_does_not_go_negative():
    result = CalculatePackagePrice(CorporateDiscount()).execute(_pkg("100"))
    assert result == Decimal("0")
