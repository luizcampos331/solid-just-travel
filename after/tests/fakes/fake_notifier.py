"""RecordingWelcomeNotifier — captures notifications for assertion."""

from after.app.domain.travelers.traveler import Traveler


class RecordingWelcomeNotifier:
    def __init__(self) -> None:
        self.notified: list[Traveler] = []

    def notify_welcome(self, traveler: Traveler) -> None:
        self.notified.append(traveler)
