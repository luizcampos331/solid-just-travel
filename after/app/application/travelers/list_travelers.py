"""ListTravelers use case — thin wrapper around the repository."""

from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_repository import TravelerRepository


class ListTravelers:
    def __init__(self, repo: TravelerRepository):
        self._repo = repo

    def execute(self) -> list[Traveler]:
        return self._repo.list()
