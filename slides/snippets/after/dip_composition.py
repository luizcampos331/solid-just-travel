# after/app/presentation/dependencies.py — DIP cure (composition root)
def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_traveler_repo(session: DbSession) -> SqlAlchemyTravelerRepository:
    return SqlAlchemyTravelerRepository(session)


TravelerRepo = Annotated[SqlAlchemyTravelerRepository, Depends(get_traveler_repo)]
WelcomeNotifierDep = Annotated[StdoutWelcomeNotifier, Depends(get_welcome_notifier)]


def get_create_traveler_uc(
    repo: TravelerRepo, notifier: WelcomeNotifierDep
) -> CreateTraveler:
    return CreateTraveler(repo=repo, notifier=notifier)


# after/app/presentation/routers/travelers.py — handler 5 linhas
@router.post("", response_model=TravelerOut, status_code=201)
def create_traveler(
    body: TravelerIn,
    use_case: Annotated[CreateTraveler, Depends(get_create_traveler_uc)],
) -> TravelerOut:
    traveler = use_case.execute(body.to_input())
    return TravelerOut.from_domain(traveler)
