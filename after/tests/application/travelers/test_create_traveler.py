"""Unit tests for CreateTraveler use case.

These tests run in milliseconds against fakes — no database, no HTTP. That
is the testability payoff of applying DIP: the use case depends on
Protocols, so tests inject fakes.
"""

import pytest

from after.app.application.travelers.create_traveler import (
    CreateTraveler,
    CreateTravelerInput,
)
from after.tests.fakes.fake_notifier import RecordingWelcomeNotifier
from after.tests.fakes.in_memory_repositories import InMemoryTravelerRepository


def test_creates_persists_and_notifies():
    repo = InMemoryTravelerRepository()
    notifier = RecordingWelcomeNotifier()
    use_case = CreateTraveler(repo=repo, notifier=notifier)

    traveler = use_case.execute(
        CreateTravelerInput(
            name="Maria Silva", email="maria@example.com", document="12345678909"
        )
    )

    assert traveler.id is not None
    assert traveler.name == "Maria Silva"
    assert repo.list() == [traveler]
    assert notifier.notified == [traveler]


def test_rejects_invalid_document():
    repo = InMemoryTravelerRepository()
    notifier = RecordingWelcomeNotifier()
    use_case = CreateTraveler(repo=repo, notifier=notifier)

    with pytest.raises(ValueError, match="11-digit"):
        use_case.execute(
            CreateTravelerInput(name="Maria", email="m@x.com", document="123")
        )

    assert repo.list() == []
    assert notifier.notified == []


def test_rejects_short_name():
    repo = InMemoryTravelerRepository()
    notifier = RecordingWelcomeNotifier()
    use_case = CreateTraveler(repo=repo, notifier=notifier)

    with pytest.raises(ValueError, match="at least 2"):
        use_case.execute(
            CreateTravelerInput(name="M", email="m@x.com", document="12345678909")
        )

    assert repo.list() == []
    assert notifier.notified == []
