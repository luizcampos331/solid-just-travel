# before/app/models.py + booking_service.py — LSP trap
class TravelPackage(Base):
    def cancel(self) -> None:
        self.status = "cancelled"
        self.cancelled_at = datetime.utcnow()


class NonRefundablePackage(TravelPackage):
    def cancel(self) -> None:
        raise ValueError("Non-refundable packages cannot be cancelled")


# booking_service.py
def cancel_all_of_traveler(session, traveler_id: int) -> int:
    packages = session.query(TravelPackage).filter_by(
        traveler_id=traveler_id
    ).all()

    cancelled = 0
    for package in packages:
        package.cancel()        # ← BOOM on NonRefundablePackage
        cancelled += 1

    session.commit()
    return cancelled
