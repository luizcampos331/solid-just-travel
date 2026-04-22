"""SQLAlchemy models.

WARNING: the classes here intentionally violate SOLID principles — they are the
"before" of a refactoring talk. Do not take any of this as a pattern to follow.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from before.app.database import Base


class Traveler(Base):
    """God Class: ORM model + validation + persistence + email + JSON formatting.

    Responds to at least four different stakeholders:
    - DBA owns the schema (Column definitions)
    - Compliance owns `validate()`
    - SRE owns `send_welcome_email()` (SMTP config)
    - Frontend owns `to_dict()` (JSON shape)

    → SRP violated.
    """

    __tablename__ = "travelers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    document = Column(String, nullable=False)  # CPF, 11 digits
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    packages = relationship("TravelPackage", back_populates="traveler")

    # --- Validation (Compliance stakeholder) ---
    def validate(self) -> None:
        if not self.name or len(self.name) < 2:
            raise ValueError("name must have at least 2 characters")
        if "@" not in (self.email or ""):
            raise ValueError("invalid email")
        if not self.document or len(self.document) != 11 or not self.document.isdigit():
            raise ValueError("document must be an 11-digit CPF")

    # --- Persistence (DBA stakeholder — should be repository) ---
    def save(self, session) -> "Traveler":
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    # --- Notification (SRE / Marketing stakeholder — should be notifier service) ---
    def send_welcome_email(self) -> None:
        # Intentionally fake — we don't want to actually send email during the talk.
        print(f"[FAKE SMTP] Welcome email sent to {self.email}")

    # --- Presentation (Frontend stakeholder — should be schema / DTO) ---
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "document": self.document,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TravelPackage(Base):
    """Base package class. Supports cancellation.

    Subclasses will break LSP by overriding `cancel()` to throw — see below.
    """

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    status = Column(String, default="active")  # active | cancelled
    cancelled_at = Column(DateTime, nullable=True)
    kind = Column(String, default="standard")  # discriminator: standard | non_refundable
    traveler_id = Column(Integer, ForeignKey("travelers.id"), nullable=True)

    traveler = relationship("Traveler", back_populates="packages")

    __mapper_args__ = {
        "polymorphic_on": kind,
        "polymorphic_identity": "standard",
    }

    def cancel(self) -> None:
        """Cancel the package — contract: always succeeds for a base TravelPackage."""
        self.status = "cancelled"
        self.cancelled_at = datetime.now(timezone.utc)


class NonRefundablePackage(TravelPackage):
    """LSP trap: overrides `cancel()` to throw.

    A naive `for p in packages: p.cancel()` loop will blow up mid-iteration
    when it hits an instance of this class — even though the static type is
    `TravelPackage` and "should" support cancellation.
    """

    __mapper_args__ = {
        "polymorphic_identity": "non_refundable",
    }

    def cancel(self) -> None:
        raise ValueError("Non-refundable packages cannot be cancelled")
