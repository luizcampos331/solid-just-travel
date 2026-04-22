"""Pydantic schemas for request/response.

Intentional duplication: we repeat fields instead of composing — part of the
SRP / DIP tangle we'll show on stage. Also, the schemas are used for both HTTP
input and output, which blurs boundaries.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TravelerIn(BaseModel):
    name: str
    email: str
    document: str


class TravelerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    document: str
    created_at: datetime | None = None


class PackageIn(BaseModel):
    name: str
    destination: str
    base_price: float
    kind: str = "standard"  # standard | non_refundable
    traveler_id: int | None = None


class PackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    destination: str
    base_price: float
    status: str
    kind: str
    traveler_id: int | None = None


class PriceCalcIn(BaseModel):
    discount_type: str  # seasonal | black_friday | corporate | cyber_monday | none


class PriceCalcOut(BaseModel):
    package_id: int
    discount_type: str
    base_price: float
    final_price: float
