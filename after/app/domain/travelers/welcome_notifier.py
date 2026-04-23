"""WelcomeNotifier — Protocol for post-create side effects.

SRP cure: welcoming a new traveler is a separate responsibility from
creating it. The use case `CreateTraveler` depends on this Protocol; the
actual implementation (`StdoutWelcomeNotifier` in infra, or `EmailNotifier`
in a production setup) is chosen in the composition root.
"""

from typing import Protocol

from after.app.domain.travelers.traveler import Traveler


class WelcomeNotifier(Protocol):
    def notify_welcome(self, traveler: Traveler) -> None: ...
