# before/app/routers/travelers.py — DIP violation
from before.app.database import SessionLocal   # ← importa infra direto
from before.app.models import Traveler

@router.post("/travelers", response_model=TravelerOut, status_code=201)
def create_traveler(body: TravelerIn) -> TravelerOut:
    session = SessionLocal()                    # ← handler constrói infra
    try:
        traveler = Traveler(
            name=body.name, email=body.email, document=body.document
        )
        traveler.validate()                     # ← SRP leak
        traveler.save(session)                  # ← SRP leak
        traveler.send_welcome_email()           # ← SRP leak
        return TravelerOut.model_validate(traveler)
    finally:
        session.close()
