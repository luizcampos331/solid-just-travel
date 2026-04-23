"""SQLAlchemy models — INFRA, not domain.

Keeping these separate from domain entities is the DIP insight: the shape
of persistence (columns, indexes, relationships) is a detail. The domain
dataclasses live in `domain/` and know nothing about this file.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from after.app.infra.database import Base


class TravelerModel(Base):
    __tablename__ = "travelers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    document = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    packages = relationship("PackageModel", back_populates="traveler")


class PackageModel(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    base_price = Column(Numeric(12, 2), nullable=False)
    refundable = Column(Boolean, nullable=False, default=True)
    status = Column(String, nullable=False, default="active")
    cancelled_at = Column(DateTime, nullable=True)
    traveler_id = Column(Integer, ForeignKey("travelers.id"), nullable=True)

    traveler = relationship("TravelerModel", back_populates="packages")
