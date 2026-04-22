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
