"""Pydantic IO schemas.

Translates between JSON (what FastAPI serves) and domain entities (what
use cases consume). The classmethods `from_domain` on the Out schemas
keep the translation centralized.

Decision: `PackageOut` exposes BOTH `kind` (legacy, derived from
`refundable`) AND `refundable` (new), so equivalence contracts from
`before/` keep passing without modification. Docstring marks `kind` as
legacy.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from after.app.application.packages.create_package import CreatePackageInput
from after.app.application.travelers.create_traveler import CreateTravelerInput
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.travelers.traveler import Traveler


class TravelerIn(BaseModel):
    name: str
    email: str
    document: str

    def to_input(self) -> CreateTravelerInput:
        return CreateTravelerInput(name=self.name, email=self.email, document=self.document)


class TravelerOut(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    name: str
    email: str
    document: str
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, t: Traveler) -> "TravelerOut":
        assert t.id is not None
        return cls(
            id=int(t.id),
            name=t.name,
            email=str(t.email),
            document=str(t.document),
            created_at=t.created_at,
        )


class PackageIn(BaseModel):
    name: str
    destination: str
    base_price: Decimal
    kind: str = "standard"  # legacy: "standard" | "non_refundable"
    traveler_id: int | None = None

    def to_input(self) -> CreatePackageInput:
        return CreatePackageInput(
            name=self.name,
            destination=self.destination,
            base_price=self.base_price,
            refundable=(self.kind != "non_refundable"),
            traveler_id=self.traveler_id,
        )


class PackageOut(BaseModel):
    """Response shape. `kind` is legacy (derived); prefer `refundable`."""

    id: int
    name: str
    destination: str
    base_price: float  # float to match `before/` response exactly
    status: str
    kind: str
    refundable: bool
    traveler_id: int | None = None

    @classmethod
    def from_domain(cls, p: TravelPackage) -> "PackageOut":
        assert p.id is not None
        return cls(
            id=int(p.id),
            name=p.name,
            destination=p.destination,
            base_price=float(p.base_price),
            status=p.status.value,
            kind=("non_refundable" if not p.refundable else "standard"),
            refundable=p.refundable,
            traveler_id=p.traveler_id,
        )


class PriceCalcIn(BaseModel):
    discount_type: str


class PriceCalcOut(BaseModel):
    package_id: int
    discount_type: str
    base_price: float
    final_price: float


class CancelResultOut(BaseModel):
    """Response shape for DELETE /travelers/{id}/packages — equivalence-breaking:

    The `before/` returned 500 on LSP bomb; we return 200 with both lists.
    The `cancelled` int field keeps the happy-path contract equivalent.
    """

    cancelled: int
    cancelled_ids: list[int]
    skipped_ids: list[int]
