# after/app/domain/travelers/traveler.py — pure dataclass
@dataclass(slots=True)
class Traveler:
    name: str
    email: Email              # VO — validates `@` at construction
    document: Document         # VO — validates 11-digit CPF
    id: TravelerId | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.name or len(self.name) < 2:
            raise ValueError("name must have at least 2 characters")


# Each stakeholder got its own class:
# - infra/persistence/sqlalchemy_traveler_repository.py   ← DBA
# - domain/travelers/document.py                          ← Compliance
# - infra/notifications/stdout_welcome_notifier.py        ← SRE
# - presentation/schemas.py::TravelerOut                  ← Frontend
