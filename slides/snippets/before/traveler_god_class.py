# before/app/models.py — intencional God Class
class Traveler(Base):
    __tablename__ = "travelers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    document = Column(String, nullable=False)

    # --- Validation (Compliance stakeholder) ---
    def validate(self) -> None:
        if not self.name or len(self.name) < 2:
            raise ValueError("name must have at least 2 characters")
        if "@" not in (self.email or ""):
            raise ValueError("invalid email")
        if not self.document or len(self.document) != 11:
            raise ValueError("document must be 11 digits")

    # --- Persistence (DBA stakeholder) ---
    def save(self, session) -> "Traveler":
        session.add(self); session.commit(); session.refresh(self)
        return self

    # --- Notification (SRE stakeholder) ---
    def send_welcome_email(self) -> None:
        print(f"[FAKE SMTP] Welcome email to {self.email}")

    # --- Presentation (Frontend stakeholder) ---
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email}
