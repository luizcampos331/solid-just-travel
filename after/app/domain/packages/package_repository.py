"""Package repository Protocols, segregated per role (ISP cure).

The `before/` version had a single `PackageRepository` with 12 methods.
Tests and use cases had to depend on the whole fat interface. Here we
split into two small Protocols:

- `PackageWriter` — use cases that add/update
- `PackageReader` — use cases that read/filter/list

The concrete SQLAlchemy adapter (in `infra/`) implements BOTH. Only the
CONTRACT surface that each client depends on is small.
"""

from __future__ import annotations

from typing import Protocol

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.travel_package import TravelPackage


class PackageWriter(Protocol):
    def add(self, package: TravelPackage) -> TravelPackage: ...
    def update(self, package: TravelPackage) -> TravelPackage: ...


class PackageReader(Protocol):
    def by_id(self, package_id: PackageId) -> TravelPackage | None: ...
    def list(self) -> list[TravelPackage]: ...
    def by_traveler(self, traveler_id: int) -> list[TravelPackage]: ...
