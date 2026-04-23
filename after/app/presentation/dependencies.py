"""FastAPI dependency providers — composition root.

This is the ONE place that knows how every piece is wired. The handlers
call `Depends(get_X_uc)`; the providers know infra is SQLAlchemy; the use
cases see only Protocols.

To swap SQLAlchemy for another ORM: edit this file. To swap stdout
notifier for SMTP: edit this file. Everything else stays.
"""

from typing import Annotated, Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from after.app.application.packages.calculate_price import CalculatePackagePrice
from after.app.application.packages.cancel_all_of_traveler import CancelAllOfTraveler
from after.app.application.packages.create_package import CreatePackage
from after.app.application.packages.list_packages import ListPackages
from after.app.application.travelers.create_traveler import CreateTraveler
from after.app.application.travelers.get_traveler import GetTraveler
from after.app.application.travelers.list_travelers import ListTravelers
from after.app.domain.packages.cancellation_policy import CancellationPolicy
from after.app.domain.packages.discount_policy import (
    BlackFridayDiscount,
    CorporateDiscount,
    CyberMondayDiscount,
    DiscountPolicy,
    NoDiscount,
    SeasonalDiscount,
)
from after.app.infra.database import SessionLocal
from after.app.infra.notifications.stdout_welcome_notifier import StdoutWelcomeNotifier
from after.app.infra.persistence.sqlalchemy_package_repository import (
    SqlAlchemyPackageRepository,
)
from after.app.infra.persistence.sqlalchemy_traveler_repository import (
    SqlAlchemyTravelerRepository,
)


def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_traveler_repo(session: DbSession) -> SqlAlchemyTravelerRepository:
    return SqlAlchemyTravelerRepository(session)


def get_package_repo(session: DbSession) -> SqlAlchemyPackageRepository:
    return SqlAlchemyPackageRepository(session)


def get_welcome_notifier() -> StdoutWelcomeNotifier:
    return StdoutWelcomeNotifier()


TravelerRepo = Annotated[SqlAlchemyTravelerRepository, Depends(get_traveler_repo)]
PackageRepo = Annotated[SqlAlchemyPackageRepository, Depends(get_package_repo)]
WelcomeNotifierDep = Annotated[StdoutWelcomeNotifier, Depends(get_welcome_notifier)]


def get_create_traveler_uc(
    repo: TravelerRepo, notifier: WelcomeNotifierDep
) -> CreateTraveler:
    return CreateTraveler(repo=repo, notifier=notifier)


def get_list_travelers_uc(repo: TravelerRepo) -> ListTravelers:
    return ListTravelers(repo)


def get_get_traveler_uc(repo: TravelerRepo) -> GetTraveler:
    return GetTraveler(repo)


def get_create_package_uc(repo: PackageRepo) -> CreatePackage:
    return CreatePackage(repo)


def get_list_packages_uc(repo: PackageRepo) -> ListPackages:
    return ListPackages(repo)


def _pick_discount_policy(discount_type: str) -> DiscountPolicy:
    match discount_type:
        case "none":
            return NoDiscount()
        case "seasonal":
            return SeasonalDiscount()
        case "black_friday":
            return BlackFridayDiscount()
        case "corporate":
            return CorporateDiscount()
        case "cyber_monday":
            return CyberMondayDiscount()
        case _:
            raise ValueError(f"unknown discount_type: {discount_type}")


def calculate_price_uc_for(discount_type: str) -> CalculatePackagePrice:
    return CalculatePackagePrice(_pick_discount_policy(discount_type))


def get_cancel_all_uc(repo: PackageRepo) -> CancelAllOfTraveler:
    return CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())
