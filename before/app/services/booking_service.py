"""Booking service — contains the `for package: package.cancel()` bomb.

This is the clearest LSP violation demo: iterating over `TravelPackage` and calling
`.cancel()` blows up mid-iteration when one of the items is a `NonRefundablePackage`.
"""

from sqlalchemy.orm import Session

from before.app.models import TravelPackage


def cancel_all_of_traveler(session: Session, traveler_id: int) -> int:
    """Cancel every package belonging to `traveler_id`.

    Returns the number of cancelled packages.

    LSP trap: raises ValueError mid-loop if the traveler has at least one
    `NonRefundablePackage`. Some packages may have been cancelled already when
    the exception is raised — this is exactly the "39 out of 40" partial failure
    scenario we use in the talk.
    """
    packages = session.query(TravelPackage).filter_by(traveler_id=traveler_id).all()

    cancelled = 0
    for package in packages:
        package.cancel()  # ← BOOM on NonRefundablePackage
        cancelled += 1

    session.commit()
    return cancelled
