# Plan A — Setup do Repositório + `before/` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a estrutura raiz do repositório `solid-just-travel/` e implementar a versão `before/` do CRUD de Viajantes e Pacotes em FastAPI + SQLAlchemy + SQLite, com violações curadas dos 5 princípios SOLID e uma suíte de testes de contrato de equivalência que vai servir como espelho de comportamento pro `after/` (Plan B).

**Architecture:** App monolítica em `before/app/` seguindo padrão de tutorial FastAPI ingênuo — classes God, handlers gordos, acoplamento direto com SQLAlchemy e SMTP. Os testes de equivalência (`before/tests/test_equivalence_contracts.py`) validam apenas comportamento observável pelos endpoints HTTP. Python 3.12 com `uv` como gerenciador de deps.

**Tech Stack:** Python 3.12 · FastAPI (>=0.110) · SQLAlchemy 2.x · Pydantic 2.x · SQLite (file + in-memory pra testes) · pytest · httpx (TestClient) · uv (deps)

---

## File Structure

Arquivos criados neste plano, agrupados por responsabilidade:

**Raiz do repositório (entregáveis compartilhados pelos 3 planos):**
- `.gitignore` — ignores Python + Node + macOS
- `.python-version` — pin Python 3.12
- `README.md` — visão geral, links pros sub-READMEs
- `pyproject.toml` — deps Python raiz (uv workspace root)

**`before/` — CRUD ingênuo com violações curadas:**
- `before/README.md` — como rodar o `before/` em pt-BR
- `before/app/__init__.py` — marcador de pacote
- `before/app/database.py` — SQLAlchemy engine + SessionLocal + Base declarativa
- `before/app/models.py` — `Traveler` (God Class: SRP) + `TravelPackage` + `NonRefundablePackage` (LSP trap)
- `before/app/schemas.py` — Pydantic com duplicação intencional
- `before/app/services/__init__.py`
- `before/app/services/package_service.py` — `calculate_price` com `if/elif` (OCP) + `PackageRepository` com 12 métodos (ISP)
- `before/app/services/booking_service.py` — `cancel_all_of_traveler` que explode com LSP
- `before/app/routers/__init__.py`
- `before/app/routers/travelers.py` — handler que importa `SessionLocal` direto (DIP)
- `before/app/routers/packages.py` — idem + cálculo inline
- `before/app/main.py` — FastAPI app + `include_router` + startup que cria tabelas
- `before/tests/__init__.py`
- `before/tests/conftest.py` — fixtures pytest: app + TestClient + banco in-memory
- `before/tests/test_equivalence_contracts.py` — contratos de comportamento observável

---

## Task 1: Inicializar repositório raiz e arquivos base

**Files:**
- Create: `.gitignore`
- Create: `.python-version`
- Create: `README.md`

- [ ] **Step 1: Inicializar git**

Run: `cd /Users/luizcampos/Documents/lectures/just-travel && git init`
Expected: `Initialized empty Git repository in ...`

- [ ] **Step 2: Criar `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.eggs/
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/

# SQLite (banco de dev do before/)
*.db
*.sqlite
*.sqlite3

# Node (slides Slidev — futuro Plan C)
node_modules/
.output/
dist/

# Editor / OS
.DS_Store
.vscode/
.idea/
*.swp

# Slidev build
slides/dist/
```

- [ ] **Step 3: Criar `.python-version`**

```
3.12
```

- [ ] **Step 4: Criar `README.md` raiz**

```markdown
# Palestra SOLID + Clean Arch — Just Travel

Material da palestra "SOLID na prática com Clean Architecture minimalista" para o time de desenvolvimento da Just Travel.

## Estrutura

- [`before/`](./before) — CRUD FastAPI realista-ingênuo, com violações curadas dos 5 princípios SOLID
- [`after/`](./after) — mesmo CRUD refatorado com Clean Arch minimalista + SOLID aplicado *(em construção)*
- [`slides/`](./slides) — deck Slidev da palestra *(em construção)*
- [`docs/`](./docs) — specs e planos de implementação

## Objetivo pedagógico

Mostrar que **Clean Architecture não é uma arquitetura à parte** — ela emerge naturalmente quando os 5 princípios SOLID são aplicados com disciplina em código que você já escreve hoje.

## Como rodar

Cada subprojeto tem seu próprio `README.md` com instruções. Comece pelo [`before/`](./before/README.md) para ver a versão "antes da refatoração".

## Stack

- Python 3.12
- FastAPI + SQLAlchemy + SQLite
- pytest + httpx
- [uv](https://docs.astral.sh/uv/) como gerenciador de dependências
- Slidev (deck) — Plan C
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore .python-version README.md
git commit -m "chore: initialize repository with base files"
```

---

## Task 2: Configurar pyproject.toml raiz com dependências

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Criar `pyproject.toml` raiz**

```toml
[project]
name = "solid-just-travel"
version = "0.1.0"
description = "Palestra SOLID + Clean Arch para Just Travel"
requires-python = ">=3.12"
readme = "README.md"
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "sqlalchemy>=2.0",
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "httpx>=0.27",
    "ruff>=0.3",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["before/tests", "after/tests"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

- [ ] **Step 2: Criar venv com uv e instalar deps**

Run: `uv sync`
Expected: `Creating virtual environment ...` e a criação de `.venv/` com deps instaladas. Se `uv` não estiver instalado, pedir ao usuário para instalar: `brew install uv` (macOS) ou ver https://docs.astral.sh/uv/.

- [ ] **Step 3: Verificar Python disponível na venv**

Run: `uv run python --version`
Expected: `Python 3.12.x`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add pyproject.toml with fastapi + sqlalchemy deps"
```

---

## Task 3: Criar esqueleto de pastas do `before/`

**Files:**
- Create: `before/README.md`
- Create: `before/app/__init__.py`
- Create: `before/app/routers/__init__.py`
- Create: `before/app/services/__init__.py`
- Create: `before/tests/__init__.py`

- [ ] **Step 1: Criar diretórios e arquivos `__init__.py` vazios**

Run:
```bash
mkdir -p before/app/routers before/app/services before/tests
touch before/app/__init__.py before/app/routers/__init__.py before/app/services/__init__.py before/tests/__init__.py
```

- [ ] **Step 2: Criar `before/README.md`**

```markdown
# `before/` — CRUD FastAPI ingênuo com violações SOLID

Esta é a versão "antes" da refatoração. Parece um tutorial FastAPI comum: organizada por camadas (routers / services / models), mas com **acoplamento direto** e **classes que fazem coisas demais**. As violações dos 5 princípios SOLID aqui são **intencionais e didáticas** — cada uma será endereçada no [`../after/`](../after).

## Violações plantadas por princípio

| Princípio | Onde dói | Arquivo |
|---|---|---|
| **S** (Single Responsibility) | `Traveler` faz ORM + validação + email + formatação | `app/models.py` |
| **O** (Open/Closed) | `calculate_price` com `if/elif` por tipo de desconto | `app/services/package_service.py` |
| **L** (Liskov) | `NonRefundablePackage.cancel()` joga exceção | `app/models.py` + `app/services/booking_service.py` |
| **I** (Interface Segregation) | `PackageRepository` com 12 métodos | `app/services/package_service.py` |
| **D** (Dependency Inversion) | Handlers importam `SessionLocal` direto | `app/routers/travelers.py`, `app/routers/packages.py` |

## Como rodar

```bash
# Na raiz do repo
uv sync

# Subir a API (porta 8000)
uv run uvicorn before.app.main:app --reload

# Documentação automática do FastAPI
# Abrir http://localhost:8000/docs
```

## Como testar

```bash
# Rodar os testes de contrato de equivalência (before/)
uv run pytest before/tests -v
```

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| POST | `/travelers` | Cria um viajante |
| GET | `/travelers` | Lista viajantes |
| GET | `/travelers/{id}` | Busca viajante por ID |
| POST | `/packages` | Cria um pacote |
| GET | `/packages` | Lista pacotes |
| POST | `/packages/{id}/price` | Calcula preço com desconto |
| DELETE | `/travelers/{id}/packages` | Cancela todos os pacotes do viajante (observar LSP trap) |
```

- [ ] **Step 3: Commit**

```bash
git add before/
git commit -m "feat(before): scaffold directory structure and README"
```

---

## Task 4: Criar `before/app/database.py` (SQLAlchemy setup)

**Files:**
- Create: `before/app/database.py`

- [ ] **Step 1: Criar `before/app/database.py`**

```python
"""SQLAlchemy engine, session factory and declarative base.

This module wires SQLAlchemy directly at import time — that is the whole point of the
`before/` version. The `after/` version will invert this so the domain has no idea
SQLAlchemy exists.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./before.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM-mapped classes."""
    pass


def get_db():
    """FastAPI dependency that yields a SQLAlchemy session per request.

    Note: handlers in `before/` bypass this and import `SessionLocal` directly —
    that is the DIP violation we want to show.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Commit**

```bash
git add before/app/database.py
git commit -m "feat(before): add SQLAlchemy engine and session factory"
```

---

## Task 5: Criar `Traveler` como God Class (violação SRP)

**Files:**
- Create: `before/app/models.py` (primeira parte)

- [ ] **Step 1: Criar `before/app/models.py` com a classe `Traveler`**

```python
"""SQLAlchemy models.

WARNING: the classes here intentionally violate SOLID principles — they are the
"before" of a refactoring talk. Do not take any of this as a pattern to follow.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from before.app.database import Base


class Traveler(Base):
    """God Class: ORM model + validation + persistence + email + JSON formatting.

    Responds to at least four different stakeholders:
    - DBA owns the schema (Column definitions)
    - Compliance owns `validate()`
    - SRE owns `send_welcome_email()` (SMTP config)
    - Frontend owns `to_dict()` (JSON shape)

    → SRP violated.
    """

    __tablename__ = "travelers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    document = Column(String, nullable=False)  # CPF, 11 digits
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    packages = relationship("TravelPackage", back_populates="traveler")

    # --- Validation (Compliance stakeholder) ---
    def validate(self) -> None:
        if not self.name or len(self.name) < 2:
            raise ValueError("name must have at least 2 characters")
        if "@" not in (self.email or ""):
            raise ValueError("invalid email")
        if not self.document or len(self.document) != 11 or not self.document.isdigit():
            raise ValueError("document must be an 11-digit CPF")

    # --- Persistence (DBA stakeholder — should be repository) ---
    def save(self, session) -> "Traveler":
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    # --- Notification (SRE / Marketing stakeholder — should be notifier service) ---
    def send_welcome_email(self) -> None:
        # Intentionally fake — we don't want to actually send email during the talk.
        print(f"[FAKE SMTP] Welcome email sent to {self.email}")

    # --- Presentation (Frontend stakeholder — should be schema / DTO) ---
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "document": self.document,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
```

- [ ] **Step 2: Commit**

```bash
git add before/app/models.py
git commit -m "feat(before): add Traveler as God Class (SRP violation)"
```

---

## Task 6: Adicionar `TravelPackage` + `NonRefundablePackage` (violação LSP)

**Files:**
- Modify: `before/app/models.py`

- [ ] **Step 1: Adicionar classes ao final de `before/app/models.py`**

Adicionar ao final do arquivo (após `class Traveler`):

```python


class TravelPackage(Base):
    """Base package class. Supports cancellation.

    Subclasses will break LSP by overriding `cancel()` to throw — see below.
    """

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    status = Column(String, default="active")  # active | cancelled
    cancelled_at = Column(DateTime, nullable=True)
    kind = Column(String, default="standard")  # discriminator: standard | non_refundable
    traveler_id = Column(Integer, ForeignKey("travelers.id"), nullable=True)

    traveler = relationship("Traveler", back_populates="packages")

    __mapper_args__ = {
        "polymorphic_on": kind,
        "polymorphic_identity": "standard",
    }

    def cancel(self) -> None:
        """Cancel the package — contract: always succeeds for a base TravelPackage."""
        self.status = "cancelled"
        self.cancelled_at = datetime.now(timezone.utc)


class NonRefundablePackage(TravelPackage):
    """LSP trap: overrides `cancel()` to throw.

    A naive `for p in packages: p.cancel()` loop will blow up mid-iteration
    when it hits an instance of this class — even though the static type is
    `TravelPackage` and "should" support cancellation.
    """

    __mapper_args__ = {
        "polymorphic_identity": "non_refundable",
    }

    def cancel(self) -> None:
        raise ValueError("Non-refundable packages cannot be cancelled")
```

- [ ] **Step 2: Commit**

```bash
git add before/app/models.py
git commit -m "feat(before): add TravelPackage + NonRefundablePackage (LSP violation)"
```

---

## Task 7: Criar schemas Pydantic com duplicação

**Files:**
- Create: `before/app/schemas.py`

- [ ] **Step 1: Criar `before/app/schemas.py`**

```python
"""Pydantic schemas for request/response.

Intentional duplication: we repeat fields instead of composing — part of the
SRP / DIP tangle we'll show on stage. Also, the schemas are used for both HTTP
input and output, which blurs boundaries.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class TravelerIn(BaseModel):
    name: str
    email: EmailStr
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
```

- [ ] **Step 2: Commit**

```bash
git add before/app/schemas.py
git commit -m "feat(before): add Pydantic schemas for travelers and packages"
```

---

## Task 8: Criar `package_service.py` com `if/elif` (OCP) e repositório gigante (ISP)

**Files:**
- Create: `before/app/services/package_service.py`

- [ ] **Step 1: Criar `before/app/services/package_service.py`**

```python
"""Package service.

Two intentional violations on display:

1. OCP: `calculate_price()` uses `if/elif` per discount type — every new discount
   forces editing this function, risking regression.

2. ISP: `PackageRepository` exposes 12 methods, while `CreatePackageHandler` only
   needs `add()`. Writing a fake for tests becomes a nightmare.
"""

from sqlalchemy.orm import Session

from before.app.models import TravelPackage


# --- OCP violation: discount selection via if/elif ---
def calculate_price(package: TravelPackage, discount_type: str) -> float:
    """Compute the final price of `package` for the given discount kind.

    Adding a new discount type means editing this function — the exact signature
    of OCP violation.
    """
    price = package.base_price

    if discount_type == "seasonal":
        price *= 0.85
    elif discount_type == "black_friday":
        price *= 0.70
    elif discount_type == "corporate":
        price = max(0.0, price - 200.0)
    elif discount_type == "cyber_monday":
        # Added last week; now we have four branches and counting.
        price *= 0.75 if package.base_price > 5000 else 0.90
    elif discount_type == "none":
        price = price
    else:
        raise ValueError(f"unknown discount_type: {discount_type}")

    return round(price, 2)


# --- ISP violation: fat repository interface ---
class PackageRepository:
    """A 12-method repository.

    The `CreatePackage` flow only needs `add()`, yet every test double has to
    implement — or raise NotImplementedError for — all 12 methods. That is ISP
    screaming for help.
    """

    def __init__(self, session: Session):
        self._session = session

    def add(self, package: TravelPackage) -> TravelPackage:
        self._session.add(package)
        self._session.commit()
        self._session.refresh(package)
        return package

    def by_id(self, package_id: int) -> TravelPackage | None:
        return self._session.get(TravelPackage, package_id)

    def list(self) -> list[TravelPackage]:
        return list(self._session.query(TravelPackage).all())

    def update(self, package: TravelPackage) -> TravelPackage:
        self._session.commit()
        return package

    def delete(self, package_id: int) -> None:
        pkg = self.by_id(package_id)
        if pkg is not None:
            self._session.delete(pkg)
            self._session.commit()

    def find_by_destination(self, destination: str) -> list[TravelPackage]:
        return list(
            self._session.query(TravelPackage).filter_by(destination=destination).all()
        )

    def find_by_price_range(self, lo: float, hi: float) -> list[TravelPackage]:
        return list(
            self._session.query(TravelPackage)
            .filter(TravelPackage.base_price >= lo)
            .filter(TravelPackage.base_price <= hi)
            .all()
        )

    def paginated(self, page: int, size: int = 10) -> list[TravelPackage]:
        return list(
            self._session.query(TravelPackage)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

    def count_by_traveler(self, traveler_id: int) -> int:
        return (
            self._session.query(TravelPackage)
            .filter_by(traveler_id=traveler_id)
            .count()
        )

    def upsert(self, package: TravelPackage) -> TravelPackage:
        self._session.merge(package)
        self._session.commit()
        return package

    def archive(self, package_id: int) -> None:
        pkg = self.by_id(package_id)
        if pkg is not None:
            pkg.status = "archived"
            self._session.commit()

    def bulk_insert(self, packages: list[TravelPackage]) -> None:
        self._session.add_all(packages)
        self._session.commit()
```

- [ ] **Step 2: Commit**

```bash
git add before/app/services/package_service.py
git commit -m "feat(before): add package service with OCP and ISP violations"
```

---

## Task 9: Criar `booking_service.py` com `cancel_all_of_traveler` (LSP trap)

**Files:**
- Create: `before/app/services/booking_service.py`

- [ ] **Step 1: Criar `before/app/services/booking_service.py`**

```python
"""Booking service — contains the `for package: package.cancel()` bomb.

This is the clearest LSP violation demo: iterating over `TravelPackage` and calling
`.cancel()` blows up mid-iteration when one of the items is a `NonRefundablePackage`.
"""

from sqlalchemy.orm import Session

from before.app.models import TravelPackage


def cancel_all_of_traveler(session: Session, traveler_id: int) -> int:
    """Cancel every package belonging to `traveler_id`.

    Returns the number of cancelled packages.

    LSP trap: raises ValueError mid-loop if the traveler has at least one
    `NonRefundablePackage`. Some packages may have been cancelled already when
    the exception is raised — this is exactly the "39 out of 40" partial failure
    scenario we use in the talk.
    """
    packages = session.query(TravelPackage).filter_by(traveler_id=traveler_id).all()

    cancelled = 0
    for package in packages:
        package.cancel()  # ← BOOM on NonRefundablePackage
        cancelled += 1

    session.commit()
    return cancelled
```

- [ ] **Step 2: Commit**

```bash
git add before/app/services/booking_service.py
git commit -m "feat(before): add booking service with LSP trap in cancel_all"
```

---

## Task 10: Criar router de Viajantes (DIP violation)

**Files:**
- Create: `before/app/routers/travelers.py`

- [ ] **Step 1: Criar `before/app/routers/travelers.py`**

```python
"""Traveler HTTP router.

DIP violation on display: the handler imports `SessionLocal` directly, constructs
a SQLAlchemy session inside the function body, and calls ORM methods. A unit test
for this handler would need a real database.
"""

from fastapi import APIRouter, HTTPException

from before.app.database import SessionLocal
from before.app.models import Traveler
from before.app.schemas import TravelerIn, TravelerOut

router = APIRouter(prefix="/travelers", tags=["travelers"])


@router.post("", response_model=TravelerOut, status_code=201)
def create_traveler(body: TravelerIn) -> TravelerOut:
    session = SessionLocal()  # ← DIP violation: handler owns infra
    try:
        traveler = Traveler(
            name=body.name,
            email=body.email,
            document=body.document,
        )
        traveler.validate()         # ← SRP violation leaks here
        traveler.save(session)      # ← SRP violation leaks here
        traveler.send_welcome_email()  # ← SRP violation leaks here
        return TravelerOut.model_validate(traveler)
    finally:
        session.close()


@router.get("", response_model=list[TravelerOut])
def list_travelers() -> list[TravelerOut]:
    session = SessionLocal()
    try:
        travelers = session.query(Traveler).all()
        return [TravelerOut.model_validate(t) for t in travelers]
    finally:
        session.close()


@router.get("/{traveler_id}", response_model=TravelerOut)
def get_traveler(traveler_id: int) -> TravelerOut:
    session = SessionLocal()
    try:
        traveler = session.get(Traveler, traveler_id)
        if traveler is None:
            raise HTTPException(status_code=404, detail="traveler not found")
        return TravelerOut.model_validate(traveler)
    finally:
        session.close()
```

- [ ] **Step 2: Commit**

```bash
git add before/app/routers/travelers.py
git commit -m "feat(before): add travelers router (DIP violation via SessionLocal)"
```

---

## Task 11: Criar router de Pacotes (inclui endpoint de LSP)

**Files:**
- Create: `before/app/routers/packages.py`

- [ ] **Step 1: Criar `before/app/routers/packages.py`**

```python
"""Package HTTP router.

Contains:
- DIP violation: same `SessionLocal` + ORM coupling as `travelers.py`.
- Inline price calculation call (OCP).
- `cancel_all_of_traveler` endpoint that triggers the LSP bomb on purpose.
"""

from fastapi import APIRouter, HTTPException

from before.app.database import SessionLocal
from before.app.models import NonRefundablePackage, TravelPackage
from before.app.schemas import PackageIn, PackageOut, PriceCalcIn, PriceCalcOut
from before.app.services.booking_service import cancel_all_of_traveler
from before.app.services.package_service import PackageRepository, calculate_price

router = APIRouter(tags=["packages"])


def _build_package(body: PackageIn) -> TravelPackage:
    """Pick the right subclass based on `kind` — fragile pattern we'll remove."""
    if body.kind == "non_refundable":
        return NonRefundablePackage(
            name=body.name,
            destination=body.destination,
            base_price=body.base_price,
            kind="non_refundable",
            traveler_id=body.traveler_id,
        )
    return TravelPackage(
        name=body.name,
        destination=body.destination,
        base_price=body.base_price,
        kind="standard",
        traveler_id=body.traveler_id,
    )


@router.post("/packages", response_model=PackageOut, status_code=201)
def create_package(body: PackageIn) -> PackageOut:
    session = SessionLocal()
    try:
        repo = PackageRepository(session)  # ← ISP: we only need `add`, repo has 12 methods
        package = _build_package(body)
        repo.add(package)
        return PackageOut.model_validate(package)
    finally:
        session.close()


@router.get("/packages", response_model=list[PackageOut])
def list_packages() -> list[PackageOut]:
    session = SessionLocal()
    try:
        packages = session.query(TravelPackage).all()
        return [PackageOut.model_validate(p) for p in packages]
    finally:
        session.close()


@router.post("/packages/{package_id}/price", response_model=PriceCalcOut)
def price_of_package(package_id: int, body: PriceCalcIn) -> PriceCalcOut:
    session = SessionLocal()
    try:
        package = session.get(TravelPackage, package_id)
        if package is None:
            raise HTTPException(status_code=404, detail="package not found")
        final = calculate_price(package, body.discount_type)  # ← OCP: see inside
        return PriceCalcOut(
            package_id=package.id,
            discount_type=body.discount_type,
            base_price=package.base_price,
            final_price=final,
        )
    finally:
        session.close()


@router.delete("/travelers/{traveler_id}/packages", status_code=200)
def cancel_all(traveler_id: int) -> dict:
    """Cancel ALL packages of a traveler — designed to trip the LSP bomb.

    If the traveler owns at least one NonRefundablePackage, this handler will
    return a 500 AFTER cancelling some of the packages. That partial failure IS
    the pedagogical moment we want during the talk.
    """
    session = SessionLocal()
    try:
        count = cancel_all_of_traveler(session, traveler_id)
        return {"cancelled": count}
    finally:
        session.close()
```

- [ ] **Step 2: Commit**

```bash
git add before/app/routers/packages.py
git commit -m "feat(before): add packages router with price and cancel-all endpoints"
```

---

## Task 12: Criar `main.py` e wiring da app

**Files:**
- Create: `before/app/main.py`

- [ ] **Step 1: Criar `before/app/main.py`**

```python
"""FastAPI entrypoint for the `before/` version.

Run:
    uv run uvicorn before.app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from before.app.database import Base, engine
from before.app.routers import packages, travelers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables at startup — good enough for the demo."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Just Travel — SOLID talk (BEFORE)",
    description=(
        "Versão ingênua do CRUD com violações SOLID curadas. "
        "Veja `after/` para a versão refatorada."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(travelers.router)
app.include_router(packages.router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "version": "before/0.1.0"}
```

- [ ] **Step 2: Rodar a app manualmente pra confirmar que sobe**

Run: `uv run uvicorn before.app.main:app --port 8000`
Expected: `Uvicorn running on http://0.0.0.0:8000` sem erros.

Parar com `Ctrl+C`.

- [ ] **Step 3: Commit**

```bash
git add before/app/main.py
git commit -m "feat(before): wire FastAPI app with lifespan + routers"
```

---

## Task 13: Criar `conftest.py` de testes com fixtures

**Files:**
- Create: `before/tests/conftest.py`

- [ ] **Step 1: Criar `before/tests/conftest.py`**

```python
"""Pytest fixtures for `before/` equivalence-contract tests.

These contracts MUST pass identically in both `before/` and `after/` (Plan B).
They describe observable behavior through the HTTP API — never internal structure.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from before.app.database import Base
from before.app.main import app as fastapi_app
from before.app import database as db_module


@pytest.fixture
def test_engine():
    """Per-test SQLite engine in-memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_engine, monkeypatch):
    """FastAPI TestClient wired to the in-memory test engine.

    Monkeypatches `SessionLocal` in `before.app.database` so that handlers
    importing it get the in-memory session. This is ugly — it IS the DIP
    violation we show on stage.
    """
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestSession)
    monkeypatch.setattr("before.app.routers.travelers.SessionLocal", TestSession)
    monkeypatch.setattr("before.app.routers.packages.SessionLocal", TestSession)

    with TestClient(fastapi_app) as c:
        yield c
```

- [ ] **Step 2: Commit**

```bash
git add before/tests/conftest.py
git commit -m "test(before): add pytest fixtures with in-memory sqlite"
```

---

## Task 14: Escrever testes de contrato — Viajantes (TDD)

**Files:**
- Create: `before/tests/test_equivalence_contracts.py` (primeira parte)

- [ ] **Step 1: Escrever testes de `POST /travelers` e `GET /travelers/{id}`**

Criar `before/tests/test_equivalence_contracts.py`:

```python
"""Equivalence contracts — behavior observable through the HTTP API.

These tests describe WHAT the system does, never HOW. They must pass identically
in `before/` (with its SOLID violations) and `after/` (after refactoring).
"""

from fastapi.testclient import TestClient


# ---------- Travelers ----------


def test_create_traveler_returns_201_and_persisted_shape(client: TestClient):
    response = client.post(
        "/travelers",
        json={
            "name": "Maria Silva",
            "email": "maria@example.com",
            "document": "12345678909",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Maria Silva"
    assert data["email"] == "maria@example.com"
    assert data["document"] == "12345678909"


def test_create_traveler_rejects_invalid_document(client: TestClient):
    response = client.post(
        "/travelers",
        json={
            "name": "Maria Silva",
            "email": "maria@example.com",
            "document": "123",  # too short
        },
    )

    assert response.status_code >= 400


def test_list_travelers_returns_created_items(client: TestClient):
    client.post(
        "/travelers",
        json={"name": "A", "email": "a@x.com", "document": "12345678901"},
    )
    client.post(
        "/travelers",
        json={"name": "B", "email": "b@x.com", "document": "12345678902"},
    )

    response = client.get("/travelers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {t["name"] for t in data} == {"A", "B"}


def test_get_traveler_returns_404_when_missing(client: TestClient):
    response = client.get("/travelers/9999")

    assert response.status_code == 404
```

- [ ] **Step 2: Rodar testes e observar resultado**

Run: `uv run pytest before/tests/test_equivalence_contracts.py -v`
Expected: 4 testes passando (a implementação já existe). Se algum falhar, é sinal de bug no handler — investigar.

Nota sobre `test_create_traveler_rejects_invalid_document`: atualmente o handler chama `traveler.validate()` que lança `ValueError` — o FastAPI transforma em 500. Isso já é `>= 400`, então passa. No `after/` (Plan B) isso virará 422 explícito, mas o contrato aqui (`>= 400`) é intencionalmente frouxo pra permitir as duas implementações.

- [ ] **Step 3: Commit**

```bash
git add before/tests/test_equivalence_contracts.py
git commit -m "test(before): add equivalence contracts for traveler endpoints"
```

---

## Task 15: Escrever testes de contrato — Pacotes + cálculo de preço

**Files:**
- Modify: `before/tests/test_equivalence_contracts.py` (append)

- [ ] **Step 1: Adicionar testes de pacote ao final de `before/tests/test_equivalence_contracts.py`**

Adicionar (após os testes de travelers):

```python


# ---------- Packages ----------


def _create_traveler(client: TestClient, email: str = "default@example.com") -> int:
    r = client.post(
        "/travelers",
        json={"name": "Default", "email": email, "document": "12345678909"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_create_package_returns_persisted(client: TestClient):
    traveler_id = _create_traveler(client)

    response = client.post(
        "/packages",
        json={
            "name": "Cancún 7 noites",
            "destination": "Cancún",
            "base_price": 5500.00,
            "kind": "standard",
            "traveler_id": traveler_id,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Cancún 7 noites"
    assert data["base_price"] == 5500.00
    assert data["status"] == "active"
    assert data["kind"] == "standard"


def test_list_packages_returns_created_items(client: TestClient):
    traveler_id = _create_traveler(client)
    for i in range(3):
        client.post(
            "/packages",
            json={
                "name": f"pkg-{i}",
                "destination": "X",
                "base_price": 1000.0,
                "kind": "standard",
                "traveler_id": traveler_id,
            },
        )

    response = client.get("/packages")

    assert response.status_code == 200
    assert len(response.json()) == 3
```

- [ ] **Step 2: Adicionar testes de cálculo de preço ao final do arquivo**

```python


# ---------- Price calculation ----------


def _create_package(client: TestClient, base_price: float) -> int:
    traveler_id = _create_traveler(client)
    r = client.post(
        "/packages",
        json={
            "name": "pkg",
            "destination": "X",
            "base_price": base_price,
            "kind": "standard",
            "traveler_id": traveler_id,
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_price_without_discount_equals_base(client: TestClient):
    pkg_id = _create_package(client, 1000.0)

    response = client.post(
        f"/packages/{pkg_id}/price",
        json={"discount_type": "none"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["base_price"] == 1000.0
    assert data["final_price"] == 1000.0


def test_price_with_seasonal_discount_is_15_percent_off(client: TestClient):
    pkg_id = _create_package(client, 1000.0)

    response = client.post(
        f"/packages/{pkg_id}/price",
        json={"discount_type": "seasonal"},
    )

    assert response.status_code == 200
    assert response.json()["final_price"] == 850.0


def test_price_with_black_friday_is_30_percent_off(client: TestClient):
    pkg_id = _create_package(client, 1000.0)

    response = client.post(
        f"/packages/{pkg_id}/price",
        json={"discount_type": "black_friday"},
    )

    assert response.status_code == 200
    assert response.json()["final_price"] == 700.0


def test_price_with_corporate_subtracts_200(client: TestClient):
    pkg_id = _create_package(client, 1000.0)

    response = client.post(
        f"/packages/{pkg_id}/price",
        json={"discount_type": "corporate"},
    )

    assert response.status_code == 200
    assert response.json()["final_price"] == 800.0


def test_price_with_cyber_monday_for_high_price_applies_25_percent(client: TestClient):
    pkg_id = _create_package(client, 6000.0)

    response = client.post(
        f"/packages/{pkg_id}/price",
        json={"discount_type": "cyber_monday"},
    )

    assert response.status_code == 200
    assert response.json()["final_price"] == 4500.0  # 6000 * 0.75


def test_price_with_cyber_monday_for_low_price_applies_10_percent(client: TestClient):
    pkg_id = _create_package(client, 2000.0)

    response = client.post(
        f"/packages/{pkg_id}/price",
        json={"discount_type": "cyber_monday"},
    )

    assert response.status_code == 200
    assert response.json()["final_price"] == 1800.0  # 2000 * 0.90
```

- [ ] **Step 3: Rodar toda a suíte**

Run: `uv run pytest before/tests/test_equivalence_contracts.py -v`
Expected: todos os testes passando (travelers + packages + price).

- [ ] **Step 4: Commit**

```bash
git add before/tests/test_equivalence_contracts.py
git commit -m "test(before): add equivalence contracts for packages and pricing"
```

---

## Task 16: Escrever testes de contrato — LSP trap de `cancel_all`

**Files:**
- Modify: `before/tests/test_equivalence_contracts.py` (append)

- [ ] **Step 1: Adicionar testes do endpoint de cancel-all**

```python


# ---------- Cancel-all (LSP trap) ----------


def test_cancel_all_cancels_standard_packages(client: TestClient):
    traveler_id = _create_traveler(client, email="owner@example.com")
    for i in range(3):
        client.post(
            "/packages",
            json={
                "name": f"std-{i}",
                "destination": "X",
                "base_price": 100.0,
                "kind": "standard",
                "traveler_id": traveler_id,
            },
        )

    response = client.delete(f"/travelers/{traveler_id}/packages")

    assert response.status_code == 200
    assert response.json()["cancelled"] == 3


def test_cancel_all_fails_when_any_package_is_non_refundable(client: TestClient):
    """THIS is the LSP trap contract.

    In `before/`, the loop blows up mid-iteration when it meets a NonRefundable
    package. We assert the PARTIAL FAILURE shape (5xx + some already cancelled).

    In `after/` (Plan B), the endpoint will return 200 with two lists
    (`cancelled` and `skipped`). The `after/` version will have its own test
    that describes the new behavior. This contract lives only here.
    """
    traveler_id = _create_traveler(client, email="mix@example.com")
    client.post(
        "/packages",
        json={
            "name": "std-1",
            "destination": "X",
            "base_price": 100.0,
            "kind": "standard",
            "traveler_id": traveler_id,
        },
    )
    client.post(
        "/packages",
        json={
            "name": "non-refundable-1",
            "destination": "X",
            "base_price": 100.0,
            "kind": "non_refundable",
            "traveler_id": traveler_id,
        },
    )

    response = client.delete(f"/travelers/{traveler_id}/packages")

    assert response.status_code >= 500  # LSP bomb exploded
```

- [ ] **Step 2: Rodar toda a suíte de testes**

Run: `uv run pytest before/tests -v`
Expected: todos os testes passam, incluindo os dois novos.

Nota: o comportamento "500 na metade do caminho" é exatamente o pedagogicamente interessante — vamos mostrar na palestra que alguns pacotes foram cancelados antes do 500 (partial failure). Se você quiser confirmar visualmente, subir a app, criar traveler+pacotes mistos e fazer `DELETE` via /docs.

- [ ] **Step 3: Commit**

```bash
git add before/tests/test_equivalence_contracts.py
git commit -m "test(before): add LSP trap contract for cancel-all endpoint"
```

---

## Task 17: Validação manual end-to-end

**Files:** nenhum (só validação)

- [ ] **Step 1: Subir a app**

Run (em um terminal): `uv run uvicorn before.app.main:app --reload --port 8000`
Expected: `Uvicorn running on http://0.0.0.0:8000`

- [ ] **Step 2: Smoke em `/health`**

Run (em outro terminal):
```bash
curl -s http://localhost:8000/health
```
Expected: `{"status":"ok","version":"before/0.1.0"}`

- [ ] **Step 3: Criar viajante via curl**

```bash
curl -s -X POST http://localhost:8000/travelers \
  -H "Content-Type: application/json" \
  -d '{"name":"Maria","email":"maria@example.com","document":"12345678909"}' | jq
```
Expected: JSON com `id`, `name`, `email`, `document`, `created_at`.

- [ ] **Step 4: Criar pacote e pedir preço com Black Friday**

```bash
# Criar pacote
curl -s -X POST http://localhost:8000/packages \
  -H "Content-Type: application/json" \
  -d '{"name":"Cancún","destination":"Cancún","base_price":5500,"kind":"standard","traveler_id":1}' | jq

# Calcular preço Black Friday (use o id retornado acima)
curl -s -X POST http://localhost:8000/packages/1/price \
  -H "Content-Type: application/json" \
  -d '{"discount_type":"black_friday"}' | jq
```
Expected: `final_price: 3850.0` (5500 × 0.70).

- [ ] **Step 5: Encerrar a app e apagar `before.db` (limpar estado da demo manual)**

Run:
```bash
# parar o uvicorn com Ctrl+C no outro terminal
rm -f before.db
```

- [ ] **Step 6: Rodar suíte de testes final**

Run: `uv run pytest before/tests -v`
Expected: 100% verde.

- [ ] **Step 7: Commit de checkpoint (se houver arquivos alterados)**

Se `git status` mostrar arquivos modificados, commit; caso contrário, pular.

```bash
git status
# se houver mudanças:
git add -A
git commit -m "chore(before): smoke-tested end-to-end"
```

---

## Task 18: Atualizar README raiz com status do Plan A

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Atualizar a seção "Estrutura" do `README.md` raiz**

Substituir a linha referente a `before/` (que tem o parêntese *(em construção)* ou não) e garantir que `before/` NÃO tem marcador de "em construção", enquanto `after/` e `slides/` mantêm:

```markdown
## Estrutura

- [`before/`](./before) — CRUD FastAPI realista-ingênuo, com violações curadas dos 5 princípios SOLID ✅
- [`after/`](./after) — mesmo CRUD refatorado com Clean Arch minimalista + SOLID aplicado *(Plan B — em construção)*
- [`slides/`](./slides) — deck Slidev da palestra *(Plan C — em construção)*
- [`docs/`](./docs) — specs e planos de implementação
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: mark Plan A (before/) as completed in root README"
```

---

## Self-Review

### 1. Spec coverage

Spec seção 4 (`before/` estrutura) → coberta nas Tasks 3-11.
Spec seção 5 (violações SOLID por princípio) → cada uma mapeada:
- **S** (Traveler God Class) → Task 5
- **O** (if/elif em `calculate_price`) → Task 8
- **L** (`NonRefundablePackage.cancel()` explode) → Task 6 (classe) + Task 9 (loop que explode) + Task 11 (endpoint) + Task 16 (teste)
- **I** (PackageRepository de 12 métodos) → Task 8
- **D** (handlers importando `SessionLocal`) → Tasks 10, 11

Spec seção 9 (não-objetivos) → respeitado: sem auth, sem testes de integração avançados, sem Docker, sem DDD.

**Item do spec que este plano NÃO cobre (por design):**
- Camada `after/` com Clean Arch → **Plan B**
- Deck Slidev → **Plan C**

### 2. Placeholder scan

Buscado por "TBD", "TODO", "implement later", "similar to" — nenhum encontrado. Todo código está completo dentro dos steps.

Uma decisão consciente: o comportamento do endpoint `/travelers` rejeitando document inválido retorna 500 no `before/` (porque `traveler.validate()` lança `ValueError` cru). O teste `test_create_traveler_rejects_invalid_document` usa `>= 400` propositalmente para permitir que `after/` retorne 422 sem quebrar o contrato. Documentado no Task 14 Step 2.

### 3. Type consistency

Revisado:
- `TravelerIn`, `TravelerOut`, `PackageIn`, `PackageOut`, `PriceCalcIn`, `PriceCalcOut` — definidos uma vez (Task 7) e usados consistentemente (Tasks 10, 11).
- `NonRefundablePackage` — nome usado em models (Task 6), router (Task 11) e testes (Task 16). Consistente.
- `calculate_price(package, discount_type)` — assinatura definida Task 8, chamada Task 11 com mesma ordem.
- `cancel_all_of_traveler(session, traveler_id)` — assinatura definida Task 9, chamada Task 11 com mesma ordem.
- `PackageRepository(session).add(package)` — interface definida Task 8, usada Task 11. Consistente.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-21-plan-a-setup-before.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Eu disparo um subagente fresco por task, reviso entre tasks, iteração rápida.

**2. Inline Execution** — Executo as tasks nesta sessão usando `executing-plans`, execução em lote com checkpoints de revisão.

**Which approach?**
