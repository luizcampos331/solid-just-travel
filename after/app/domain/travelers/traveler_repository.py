"""TravelerRepository — Protocol the domain owns.

DIP cure: the application layer depends on THIS abstraction, not on
SQLAlchemy. Infra implements it. If we switch from SQLite to Postgres
to MongoDB, only `infra/persistence/` changes.

ISP note: the repository is intentionally small (3 methods) — each use
case only needs a subset, but with 3 methods total it is not worth
splitting into reader/writer Protocols yet. Packages go the other way
(see `package_repository.py`) because that one reaches 12 methods in
`before/`.
"""

from typing import Protocol

from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId


class TravelerRepository(Protocol):
    def add(self, traveler: Traveler) -> Traveler: ...
    def by_id(self, traveler_id: TravelerId) -> Traveler | None: ...
    def list(self) -> list[Traveler]: ...
