"""GetTraveler use case."""

from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.domain.travelers.traveler_repository import TravelerRepository


class TravelerNotFound(Exception):
    """Raised when a traveler lookup misses."""


class GetTraveler:
    def __init__(self, repo: TravelerRepository):
        self._repo = repo

    def execute(self, traveler_id: TravelerId) -> Traveler:
        found = self._repo.by_id(traveler_id)
        if found is None:
            raise TravelerNotFound(f"traveler {traveler_id} not found")
        return found
