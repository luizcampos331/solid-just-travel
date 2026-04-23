# after/app/domain/packages/package_repository.py — ISP cure
from __future__ import annotations
from typing import Protocol


class PackageWriter(Protocol):
    def add(self, package: TravelPackage) -> TravelPackage: ...
    def update(self, package: TravelPackage) -> TravelPackage: ...


class PackageReader(Protocol):
    def by_id(self, package_id: PackageId) -> TravelPackage | None: ...
    def list(self) -> list[TravelPackage]: ...
    def by_traveler(self, traveler_id: int) -> list[TravelPackage]: ...


# Use case CreatePackage depende só de PackageWriter (2 métodos):
class CreatePackage:
    def __init__(self, writer: PackageWriter):
        self._writer = writer
    def execute(self, input):
        return self._writer.add(TravelPackage(...))


# O adapter SQLAlchemy pode unificar — ISP é sobre o CONTRATO, não a
# implementação. Um mock de teste pra CreatePackage tem só 2 métodos:
class FakePackageWriter:
    def add(self, p): self.added.append(p)
    def update(self, p): ...
