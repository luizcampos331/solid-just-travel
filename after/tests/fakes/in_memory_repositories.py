"""In-memory fakes for unit tests — tiny and obvious.

A fake per Protocol. Each fake implements the whole Protocol surface AND
NOTHING ELSE — contrast with the `before/` fake that had to raise
NotImplementedError for 11 of 12 methods.
"""

from __future__ import annotations

from dataclasses import replace

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId


class InMemoryTravelerRepository:
    def __init__(self) -> None:
        self._rows: dict[int, Traveler] = {}
        self._next_id = 1

    def add(self, traveler: Traveler) -> Traveler:
        saved = replace(traveler, id=TravelerId(self._next_id))
        self._rows[self._next_id] = saved
        self._next_id += 1
        return saved

    def by_id(self, traveler_id: TravelerId) -> Traveler | None:
        return self._rows.get(int(traveler_id))

    def list(self) -> list[Traveler]:
        return list(self._rows.values())


class InMemoryPackageRepository:
    def __init__(self) -> None:
        self._rows: dict[int, TravelPackage] = {}
        self._next_id = 1

    # --- PackageWriter ---
    def add(self, package: TravelPackage) -> TravelPackage:
        saved = replace(package, id=PackageId(self._next_id))
        self._rows[self._next_id] = saved
        self._next_id += 1
        return saved

    def update(self, package: TravelPackage) -> TravelPackage:
        assert package.id is not None, "update requires persisted package"
        self._rows[int(package.id)] = package
        return package

    # --- PackageReader ---
    def by_id(self, package_id: PackageId) -> TravelPackage | None:
        return self._rows.get(int(package_id))

    def list(self) -> list[TravelPackage]:
        return list(self._rows.values())

    def by_traveler(self, traveler_id: int) -> list[TravelPackage]:
        return [p for p in self._rows.values() if p.traveler_id == traveler_id]
