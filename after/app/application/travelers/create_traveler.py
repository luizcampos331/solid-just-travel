"""CreateTraveler use case.

Single responsibility: take validated input, build a domain entity, persist,
notify. Dependencies are Protocols — no SQLAlchemy, no FastAPI.
"""

from dataclasses import dataclass

from after.app.domain.travelers.document import Document
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_repository import TravelerRepository
from after.app.domain.travelers.welcome_notifier import WelcomeNotifier


@dataclass(slots=True)
class CreateTravelerInput:
    name: str
    email: str
    document: str


class CreateTraveler:
    def __init__(self, repo: TravelerRepository, notifier: WelcomeNotifier):
        self._repo = repo
        self._notifier = notifier

    def execute(self, input: CreateTravelerInput) -> Traveler:
        traveler = Traveler(
            name=input.name,
            email=Email(input.email),
            document=Document(input.document),
        )
        saved = self._repo.add(traveler)
        self._notifier.notify_welcome(saved)
        return saved
