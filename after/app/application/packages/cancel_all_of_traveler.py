"""CancelAllOfTraveler — honest partial-result use case.

The LSP cure in action: no `for p in packages: p.cancel()` bomb. We ask
the policy whether each package is cancellable, and return both lists.
"""

from dataclasses import dataclass

from after.app.domain.packages.cancellation_policy import CancellationPolicy
from after.app.domain.packages.package_repository import PackageReader, PackageWriter
from after.app.domain.packages.travel_package import TravelPackage


@dataclass(slots=True)
class CancelResult:
    cancelled: list[TravelPackage]
    skipped: list[TravelPackage]


class CancelAllOfTraveler:
    def __init__(
        self,
        repo: PackageReader,
        policy: CancellationPolicy,
        writer: PackageWriter | None = None,
    ):
        # We accept a single repo for both read + write when the concrete
        # implementation satisfies both Protocols (SQLAlchemy adapter does).
        # `writer` overrides if different bindings are needed in tests.
        self._reader = repo
        self._writer: PackageWriter = writer if writer is not None else repo  # type: ignore[assignment]
        self._policy = policy

    def execute(self, traveler_id: int) -> CancelResult:
        packages = self._reader.by_traveler(traveler_id)
        cancelled: list[TravelPackage] = []
        skipped: list[TravelPackage] = []
        for package in packages:
            if package.refundable:
                updated = self._policy.cancel(package)
                self._writer.update(updated)
                cancelled.append(updated)
            else:
                skipped.append(package)
        return CancelResult(cancelled=cancelled, skipped=skipped)
