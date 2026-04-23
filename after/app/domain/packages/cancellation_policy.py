"""CancellationPolicy — explicit policy for cancelling packages.

LSP cure (part 2): with `refundable: bool` on `TravelPackage`, this policy
decides whether a cancellation is allowed and mutates state consistently.
No subclass lies about `.cancel()` anymore.
"""

from dataclasses import replace
from datetime import datetime, timezone

from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.travel_package import TravelPackage


class CannotCancelError(Exception):
    """Raised when a non-refundable package is asked to cancel."""


class CancellationPolicy:
    def cancel(self, package: TravelPackage) -> TravelPackage:
        """Return a cancelled COPY of the package.

        Raises `CannotCancelError` for non-refundable packages. Callers that
        iterate over mixed packages should check `package.refundable` BEFORE
        calling — the use case `CancelAllOfTraveler` does exactly that and
        skips non-refundables into a separate list instead of raising.
        """
        if not package.refundable:
            raise CannotCancelError(
                f"package {package.id} is non-refundable and cannot be cancelled"
            )
        return replace(
            package,
            status=PackageStatus.CANCELLED,
            cancelled_at=datetime.now(timezone.utc),
        )
