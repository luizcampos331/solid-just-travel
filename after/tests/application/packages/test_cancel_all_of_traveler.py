"""Unit tests for CancelAllOfTraveler — the LSP cure use case.

The `before/` version raised mid-loop on NonRefundablePackage. The `after/`
version returns a partial result: cancelled + skipped. Callers KNOW what
they got.
"""

from dataclasses import replace
from decimal import Decimal

from after.app.application.packages.cancel_all_of_traveler import (
    CancelAllOfTraveler,
    CancelResult,
)
from after.app.domain.packages.cancellation_policy import CancellationPolicy
from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.travel_package import TravelPackage
from after.tests.fakes.in_memory_repositories import InMemoryPackageRepository


def _seed(repo: InMemoryPackageRepository, traveler_id: int, refundable_flags: list[bool]) -> None:
    for i, r in enumerate(refundable_flags):
        repo.add(
            TravelPackage(
                name=f"p-{i}",
                destination="X",
                base_price=Decimal("100"),
                refundable=r,
                traveler_id=traveler_id,
            )
        )


def test_cancels_every_refundable_package():
    repo = InMemoryPackageRepository()
    _seed(repo, traveler_id=1, refundable_flags=[True, True, True])
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    result = use_case.execute(traveler_id=1)

    assert isinstance(result, CancelResult)
    assert len(result.cancelled) == 3
    assert len(result.skipped) == 0
    assert all(p.status == PackageStatus.CANCELLED for p in result.cancelled)


def test_skips_non_refundable_and_reports():
    repo = InMemoryPackageRepository()
    _seed(repo, traveler_id=1, refundable_flags=[True, False, True])
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    result = use_case.execute(traveler_id=1)

    assert len(result.cancelled) == 2
    assert len(result.skipped) == 1
    assert all(p.refundable is False for p in result.skipped)


def test_empty_traveler_returns_empty_result():
    repo = InMemoryPackageRepository()
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    result = use_case.execute(traveler_id=999)

    assert result.cancelled == []
    assert result.skipped == []


def test_cancelled_packages_are_persisted_via_update():
    repo = InMemoryPackageRepository()
    _seed(repo, traveler_id=1, refundable_flags=[True])
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    use_case.execute(traveler_id=1)

    persisted = repo.by_traveler(1)
    assert len(persisted) == 1
    assert persisted[0].status == PackageStatus.CANCELLED
