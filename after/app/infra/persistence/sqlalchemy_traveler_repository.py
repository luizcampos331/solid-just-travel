"""SqlAlchemyTravelerRepository — implements TravelerRepository Protocol.

Translates between domain entities and SQLAlchemy rows. The domain stays
pure; this is the ONLY place where ORM calls are issued for travelers.
"""

from sqlalchemy.orm import Session

from after.app.domain.travelers.document import Document
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.infra.persistence.models import TravelerModel


def _to_domain(row: TravelerModel) -> Traveler:
    return Traveler(
        name=row.name,
        email=Email(row.email),
        document=Document(row.document),
        id=TravelerId(row.id),
        created_at=row.created_at,
    )


def _to_row(t: Traveler) -> TravelerModel:
    return TravelerModel(
        name=t.name,
        email=str(t.email),
        document=str(t.document),
        created_at=t.created_at,
    )


class SqlAlchemyTravelerRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, traveler: Traveler) -> Traveler:
        row = _to_row(traveler)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return _to_domain(row)

    def by_id(self, traveler_id: TravelerId) -> Traveler | None:
        row = self._session.get(TravelerModel, int(traveler_id))
        return _to_domain(row) if row is not None else None

    def list(self) -> list[Traveler]:
        rows = self._session.query(TravelerModel).all()
        return [_to_domain(r) for r in rows]
