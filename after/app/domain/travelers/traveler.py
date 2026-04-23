"""Traveler — pure domain entity.

SRP cure: this class answers to ONE stakeholder — the domain. It knows about
invariants between its own fields (via the VOs it holds). It does NOT know
about SQLAlchemy, FastAPI, SMTP, or JSON. Those concerns live in other
layers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from after.app.domain.travelers.document import Document
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.traveler_id import TravelerId


@dataclass(slots=True)
class Traveler:
    name: str
    email: Email
    document: Document
    id: TravelerId | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name or len(self.name) < 2:
            raise ValueError("name must have at least 2 characters")
