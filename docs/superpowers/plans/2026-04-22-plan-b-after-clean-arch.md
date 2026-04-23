# Plan B — `after/` Clean Arch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar a versão `after/` do CRUD de Viajantes e Pacotes da palestra SOLID + Just Travel — Clean Arch minimalista com 4 camadas (domain / application / infra / presentation), dependências sempre apontando pro domain, cada violação SOLID do `before/` curada de forma visível, e 13 dos 14 testes de contrato de equivalência do `before/` passando sem modificação mais 1 teste novo que expressa o comportamento gracioso do `cancel-all` (substituindo a LSP bomb).

**Architecture:** Estrutura `after/app/` com 4 pastas — `domain/` (entidades puras e Protocols, zero dep externa), `application/` (use cases com construtor injetado via Protocols), `infra/` (SQLAlchemy models + repositories concretos + notifiers), `presentation/` (FastAPI routers finos + Pydantic schemas de IO). Wiring via `Depends()` nativo do FastAPI no composition root (`main.py` + `presentation/dependencies.py`). Testes unitários na camada `application/` com fakes in-memory (vendem testabilidade grátis); testes de equivalência HTTP espelham `before/tests/` e provam que comportamento observável não mudou.

**Tech Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.x · Pydantic 2.x · SQLite · pytest · httpx · `typing.Protocol` pra interfaces (structural typing, sem `ABC`).

**Pré-requisitos:** Plan A completo e verde (14 testes passando em `before/tests/`). Deps já instaladas via `uv sync`.

---

## File Structure

```
after/
├── README.md                                          # pt-BR, como rodar + mapa SOLID cura por cura
├── app/
│   ├── __init__.py
│   ├── main.py                                        # FastAPI app + lifespan + include_router
│   ├── domain/                                        # núcleo puro, zero dep externa
│   │   ├── __init__.py
│   │   ├── travelers/
│   │   │   ├── __init__.py
│   │   │   ├── traveler.py                            # dataclass Traveler
│   │   │   ├── document.py                            # VO Document (11 dígitos)
│   │   │   ├── email.py                               # VO Email (tem @)
│   │   │   ├── traveler_id.py                         # NewType / wrapper int
│   │   │   ├── traveler_repository.py                 # Protocol TravelerRepository
│   │   │   └── welcome_notifier.py                    # Protocol WelcomeNotifier
│   │   └── packages/
│   │       ├── __init__.py
│   │       ├── travel_package.py                      # dataclass TravelPackage com refundable:bool
│   │       ├── package_id.py
│   │       ├── package_status.py                      # Enum ACTIVE/CANCELLED
│   │       ├── package_repository.py                  # Protocols PackageWriter + PackageReader (ISP)
│   │       ├── discount_policy.py                     # Protocol + strategies
│   │       └── cancellation_policy.py                 # classe CancellationPolicy
│   ├── application/                                   # use cases
│   │   ├── __init__.py
│   │   ├── travelers/
│   │   │   ├── __init__.py
│   │   │   ├── create_traveler.py                     # CreateTraveler use case + InputDTO
│   │   │   ├── list_travelers.py
│   │   │   └── get_traveler.py
│   │   └── packages/
│   │       ├── __init__.py
│   │       ├── create_package.py
│   │       ├── list_packages.py
│   │       ├── calculate_price.py                     # CalculatePackagePrice (depende de DiscountPolicy)
│   │       └── cancel_all_of_traveler.py              # retorna CancelResult(cancelled=[], skipped=[])
│   ├── infra/                                         # adapters concretos
│   │   ├── __init__.py
│   │   ├── database.py                                # engine + SessionLocal + Base
│   │   ├── persistence/
│   │   │   ├── __init__.py
│   │   │   ├── models.py                              # SQLAlchemy TravelerModel + PackageModel
│   │   │   ├── sqlalchemy_traveler_repository.py
│   │   │   └── sqlalchemy_package_repository.py       # implementa PackageWriter + PackageReader
│   │   └── notifications/
│   │       ├── __init__.py
│   │       └── stdout_welcome_notifier.py             # implementa WelcomeNotifier
│   └── presentation/                                  # HTTP FastAPI
│       ├── __init__.py
│       ├── schemas.py                                 # Pydantic IO + `.to_input()` / `.from_domain()`
│       ├── dependencies.py                            # Depends() providers — composition root
│       └── routers/
│           ├── __init__.py
│           ├── travelers.py                           # handlers finos (3-5 linhas)
│           └── packages.py
└── tests/
    ├── __init__.py
    ├── conftest.py                                    # fixtures pra equivalence + unit tests
    ├── fakes/
    │   ├── __init__.py
    │   ├── in_memory_repositories.py                  # InMemoryTravelerRepo, InMemoryPackageRepo
    │   └── fake_notifier.py                           # RecordingWelcomeNotifier
    ├── application/
    │   ├── __init__.py
    │   ├── travelers/
    │   │   ├── __init__.py
    │   │   └── test_create_traveler.py
    │   └── packages/
    │       ├── __init__.py
    │       ├── test_calculate_price.py                # testa cada DiscountPolicy isolada (OCP payoff)
    │       └── test_cancel_all_of_traveler.py        # testa partial result (LSP cura)
    └── test_equivalence_contracts.py                  # 13 dos 14 testes do before/ + 1 novo
```

---

## SOLID cure map (referência rápida)

| Princípio | `before/` | `after/` |
|---|---|---|
| **SRP** | `Traveler` God Class com ORM+validate+save+email+to_dict | `domain.travelers.Traveler` dataclass pura + `Document`/`Email` VOs + `SqlAlchemyTravelerRepository` + `StdoutWelcomeNotifier` + `TravelerOut` Pydantic |
| **OCP** | `if/elif` em `calculate_price` | `DiscountPolicy` Protocol + 5 strategies (`NoDiscount`, `Seasonal`, `BlackFriday`, `Corporate`, `CyberMonday`) |
| **LSP** | `NonRefundablePackage(TravelPackage)` com `.cancel()` que lança | `TravelPackage` dataclass com `refundable: bool` + `CancellationPolicy` + `CancelAllOfTraveler` retorna `CancelResult(cancelled=[], skipped=[])` |
| **ISP** | `PackageRepository` com 12 métodos | `PackageWriter` Protocol (2 métodos) + `PackageReader` Protocol (2 métodos) — implementações concretas ainda podem unificar |
| **DIP** | Handlers importam `SessionLocal` direto | Handlers recebem use case via `Depends(get_create_traveler_uc)`, use cases recebem Protocols no construtor |

---

## Equivalence test mapping

Os 14 testes de `before/tests/test_equivalence_contracts.py` portam assim pro `after/tests/test_equivalence_contracts.py`:

| Teste (before) | Ação no after |
|---|---|
| `test_create_traveler_returns_201_and_persisted_shape` | Porta direto (mesmo contrato HTTP) |
| `test_create_traveler_rejects_invalid_document` | Porta direto; `after/` retorna 422 (Pydantic + VO raise) mas `>= 400` aceita ambos |
| `test_list_travelers_returns_created_items` | Porta direto |
| `test_get_traveler_returns_404_when_missing` | Porta direto |
| `test_create_package_returns_persisted` | Porta direto (assert `"kind"` sai — adicione `refundable: bool` na shape; ver Task 28 pra decisão) |
| `test_list_packages_returns_created_items` | Porta direto |
| Todos os 6 testes de preço | Porta direto — each discount strategy retorna mesmos valores |
| `test_cancel_all_cancels_standard_packages` | Porta direto (200 + `cancelled == 3`) |
| `test_cancel_all_fails_when_any_package_is_non_refundable` | **NÃO porta**: após refatoração LSP, não há 500. Substituído por teste novo `test_cancel_all_skips_non_refundable_and_reports_partial_result` |

Total após: **13 equivalentes + 1 novo = 14 testes** em `after/tests/test_equivalence_contracts.py`.

**Decisão de shape do PackageOut**: o `before/` expõe `kind` no response. No `after/`, a feature que `kind` representa (refundable vs não) vira um atributo `refundable: bool`. Pra manter equivalência HTTP **sem** quebrar contratos, `PackageOut` expõe AMBOS: `kind` (derivado: `"non_refundable" if not refundable else "standard"`) E `refundable` (novo). Testes do before passam com `kind`; testes do after podem usar `refundable`. Docstring da schema registra que `kind` é legacy.

---

## Task 1: Scaffold de pastas e README do `after/`

**Files:**
- Create: `after/README.md`
- Create: `after/app/__init__.py`
- Create: `after/app/domain/__init__.py`
- Create: `after/app/domain/travelers/__init__.py`
- Create: `after/app/domain/packages/__init__.py`
- Create: `after/app/application/__init__.py`
- Create: `after/app/application/travelers/__init__.py`
- Create: `after/app/application/packages/__init__.py`
- Create: `after/app/infra/__init__.py`
- Create: `after/app/infra/persistence/__init__.py`
- Create: `after/app/infra/notifications/__init__.py`
- Create: `after/app/presentation/__init__.py`
- Create: `after/app/presentation/routers/__init__.py`
- Create: `after/tests/__init__.py`
- Create: `after/tests/fakes/__init__.py`
- Create: `after/tests/application/__init__.py`
- Create: `after/tests/application/travelers/__init__.py`
- Create: `after/tests/application/packages/__init__.py`

- [ ] **Step 1: Criar diretórios e `__init__.py` vazios**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel
mkdir -p after/app/domain/travelers after/app/domain/packages
mkdir -p after/app/application/travelers after/app/application/packages
mkdir -p after/app/infra/persistence after/app/infra/notifications
mkdir -p after/app/presentation/routers
mkdir -p after/tests/fakes after/tests/application/travelers after/tests/application/packages

touch after/app/__init__.py
touch after/app/domain/__init__.py after/app/domain/travelers/__init__.py after/app/domain/packages/__init__.py
touch after/app/application/__init__.py after/app/application/travelers/__init__.py after/app/application/packages/__init__.py
touch after/app/infra/__init__.py after/app/infra/persistence/__init__.py after/app/infra/notifications/__init__.py
touch after/app/presentation/__init__.py after/app/presentation/routers/__init__.py
touch after/tests/__init__.py after/tests/fakes/__init__.py
touch after/tests/application/__init__.py after/tests/application/travelers/__init__.py after/tests/application/packages/__init__.py
```

- [ ] **Step 2: Criar `after/README.md` (pt-BR)**

```markdown
# `after/` — CRUD com Clean Arch + SOLID aplicado

Esta é a versão "depois" da refatoração. As 5 violações SOLID do [`before/`](../before) foram curadas em camadas concêntricas (**domain → application → infra → presentation**) e o comportamento HTTP observável **continua idêntico** — os contratos de equivalência (`tests/test_equivalence_contracts.py`) provam isso.

## Cura por princípio

| Princípio | Onde doía no `before/` | Como foi curado no `after/` |
|---|---|---|
| **S** (SRP) | `Traveler` God Class | `domain/travelers/traveler.py` (dataclass) + VOs `Document`/`Email` + `SqlAlchemyTravelerRepository` + `StdoutWelcomeNotifier` + `TravelerOut` (Pydantic) |
| **O** (OCP) | `if/elif` em `calculate_price` | `DiscountPolicy` Protocol + 5 strategies em `domain/packages/discount_policy.py` |
| **L** (LSP) | `NonRefundablePackage.cancel()` lança exceção | `TravelPackage` com `refundable: bool` + `CancellationPolicy` + `CancelAllOfTraveler` retorna partial result |
| **I** (ISP) | `PackageRepository` com 12 métodos | `PackageWriter` + `PackageReader` Protocols segregados em `domain/packages/package_repository.py` |
| **D** (DIP) | Handlers importam `SessionLocal` direto | Use cases dependem de Protocols; `Depends()` do FastAPI wira implementações no `main.py`/`dependencies.py` |

## Como rodar

```bash
# Na raiz do repo
uv sync

# Subir a API (porta 8001 pra não conflitar com before/)
uv run uvicorn after.app.main:app --port 8001 --reload

# Docs OpenAPI
# http://localhost:8001/docs
```

## Como testar

```bash
# Rodar tudo do after/ (unit tests + equivalence contracts)
uv run pytest after/tests -v

# Só os testes unitários da camada application
uv run pytest after/tests/application -v

# Só os contratos de equivalência HTTP
uv run pytest after/tests/test_equivalence_contracts.py -v
```

## Endpoints

Os mesmos do `before/` — `/travelers`, `/packages`, `/packages/{id}/price`, `DELETE /travelers/{id}/packages`. Detalhe: o endpoint de cancel-all agora retorna `200 OK` com `{"cancelled": [...], "skipped": [...]}` — a LSP bomb foi desarmada.

## Argumento principal

Mesma funcionalidade, comportamento HTTP idêntico, **zero violação de SOLID**. A estrutura de 4 camadas emergiu naturalmente — não foi decidida antes.
```

- [ ] **Step 3: Commit**

```bash
git add after/
git commit -m "feat(after): scaffold Clean Arch directory structure and README"
```

---

## Task 2: Domain — Value Objects de `travelers/`

**Files:**
- Create: `after/app/domain/travelers/traveler_id.py`
- Create: `after/app/domain/travelers/document.py`
- Create: `after/app/domain/travelers/email.py`

- [ ] **Step 1: Criar `traveler_id.py`**

```python
"""TravelerId — typed wrapper over int to avoid primitive obsession.

Using a NewType makes `def by_id(id: TravelerId)` and `def by_id(id: int)`
distinct to type checkers, which prevents accidentally passing, say, a
package id where a traveler id is expected.
"""

from typing import NewType

TravelerId = NewType("TravelerId", int)
```

- [ ] **Step 2: Criar `document.py` (Value Object)**

```python
"""Document VO — CPF with 11 digits.

This is an SRP cure: the validation rule that lived inside the God Class
`Traveler.validate()` in `before/` is now a first-class domain concept. The
entity can assume its document is valid; validation happens at construction
of the VO.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) != 11 or not self.value.isdigit():
            raise ValueError("document must be an 11-digit CPF")

    def __str__(self) -> str:
        return self.value
```

- [ ] **Step 3: Criar `email.py` (Value Object)**

```python
"""Email VO — minimal structural check.

Intentionally simple: we check for `@` only. A production system would use
a full validator, but the talk's point is that **validation belongs in the
domain, not in the ORM**. Upgrading this to a real email parser is a
one-line change with zero ripple effect — that's the SRP payoff.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in (self.value or ""):
            raise ValueError("invalid email")

    def __str__(self) -> str:
        return self.value
```

- [ ] **Step 4: Verify imports**

Run:
```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.domain.travelers.document import Document
from after.app.domain.travelers.email import Email
d = Document('12345678909')
e = Email('a@b.c')
try:
    Document('123'); raise RuntimeError('should have raised')
except ValueError: pass
try:
    Email('no-at'); raise RuntimeError('should have raised')
except ValueError: pass
print('VOs ok:', d, e, TravelerId(1))
"
```
Expected: `VOs ok: 12345678909 a@b.c 1`.

- [ ] **Step 5: Commit**

```bash
git add after/app/domain/travelers/
git commit -m "feat(after): add traveler value objects (TravelerId, Document, Email)"
```

---

## Task 3: Domain — `Traveler` entity

**Files:**
- Create: `after/app/domain/travelers/traveler.py`

- [ ] **Step 1: Criar `traveler.py`**

```python
"""Traveler — pure domain entity.

SRP cure: this class answers to ONE stakeholder — the domain. It knows about
invariants between its own fields (via the VOs it holds). It does NOT know
about SQLAlchemy, FastAPI, SMTP, or JSON. Those concerns live in other
layers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from after.app.domain.travelers.document import Document
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.traveler_id import TravelerId


@dataclass(slots=True)
class Traveler:
    name: str
    email: Email
    document: Document
    id: TravelerId | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name or len(self.name) < 2:
            raise ValueError("name must have at least 2 characters")
```

- [ ] **Step 2: Verify import + invariant**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.document import Document

t = Traveler(name='Maria', email=Email('m@x.com'), document=Document('12345678909'))
print('traveler ok:', t.name, t.email, t.document, t.id)

try:
    Traveler(name='M', email=Email('m@x.com'), document=Document('12345678909'))
    raise RuntimeError('expected ValueError')
except ValueError as e:
    print('name invariant ok:', e)
"
```
Expected: `traveler ok: Maria m@x.com 12345678909 None` then `name invariant ok: name must have at least 2 characters`.

- [ ] **Step 3: Commit**

```bash
git add after/app/domain/travelers/traveler.py
git commit -m "feat(after): add Traveler domain entity (pure dataclass, no external deps)"
```

---

## Task 4: Domain — `TravelerRepository` + `WelcomeNotifier` Protocols

**Files:**
- Create: `after/app/domain/travelers/traveler_repository.py`
- Create: `after/app/domain/travelers/welcome_notifier.py`

- [ ] **Step 1: Criar `traveler_repository.py`**

```python
"""TravelerRepository — Protocol the domain owns.

DIP cure: the application layer depends on THIS abstraction, not on
SQLAlchemy. Infra implements it. If we switch from SQLite to Postgres
to MongoDB, only `infra/persistence/` changes.

ISP note: the repository is intentionally small (3 methods) — each use
case only needs a subset, but with 3 methods total it is not worth
splitting into reader/writer Protocols yet. Packages go the other way
(see `package_repository.py`) because that one reaches 12 methods in
`before/`.
"""

from typing import Protocol

from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId


class TravelerRepository(Protocol):
    def add(self, traveler: Traveler) -> Traveler: ...
    def by_id(self, traveler_id: TravelerId) -> Traveler | None: ...
    def list(self) -> list[Traveler]: ...
```

- [ ] **Step 2: Criar `welcome_notifier.py`**

```python
"""WelcomeNotifier — Protocol for post-create side effects.

SRP cure: welcoming a new traveler is a separate responsibility from
creating it. The use case `CreateTraveler` depends on this Protocol; the
actual implementation (`StdoutWelcomeNotifier` in infra, or `EmailNotifier`
in a production setup) is chosen in the composition root.
"""

from typing import Protocol

from after.app.domain.travelers.traveler import Traveler


class WelcomeNotifier(Protocol):
    def notify_welcome(self, traveler: Traveler) -> None: ...
```

- [ ] **Step 3: Verify imports**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.domain.travelers.traveler_repository import TravelerRepository
from after.app.domain.travelers.welcome_notifier import WelcomeNotifier
print('protocols ok:', TravelerRepository.__name__, WelcomeNotifier.__name__)
"
```
Expected: `protocols ok: TravelerRepository WelcomeNotifier`.

- [ ] **Step 4: Commit**

```bash
git add after/app/domain/travelers/traveler_repository.py after/app/domain/travelers/welcome_notifier.py
git commit -m "feat(after): add TravelerRepository and WelcomeNotifier Protocols (DIP)"
```

---

## Task 5: Domain — Package entity + id + status enum

**Files:**
- Create: `after/app/domain/packages/package_id.py`
- Create: `after/app/domain/packages/package_status.py`
- Create: `after/app/domain/packages/travel_package.py`

- [ ] **Step 1: Criar `package_id.py`**

```python
"""PackageId — typed wrapper over int."""

from typing import NewType

PackageId = NewType("PackageId", int)
```

- [ ] **Step 2: Criar `package_status.py`**

```python
"""PackageStatus — enum of valid package states.

Replaces the loose string column (`"active" | "cancelled"`) in `before/`.
"""

from enum import Enum


class PackageStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
```

- [ ] **Step 3: Criar `travel_package.py`**

```python
"""TravelPackage — pure domain entity.

LSP cure: the `before/` version had a `NonRefundablePackage(TravelPackage)`
subclass that overrode `.cancel()` to raise — breaking substitutability. The
capability "refundable" is now data on the base class, not a new type. Any
function accepting `TravelPackage` can iterate without fear of mid-loop
exceptions.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.package_status import PackageStatus


@dataclass(slots=True)
class TravelPackage:
    name: str
    destination: str
    base_price: Decimal
    refundable: bool
    status: PackageStatus = PackageStatus.ACTIVE
    cancelled_at: datetime | None = None
    traveler_id: int | None = None  # int, not TravelerId, to ease serialization
    id: PackageId | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if self.base_price < 0:
            raise ValueError("base_price cannot be negative")
```

- [ ] **Step 4: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from decimal import Decimal
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.packages.package_status import PackageStatus

p = TravelPackage(name='Cancun', destination='MX', base_price=Decimal('5500'), refundable=True)
assert p.status == PackageStatus.ACTIVE
assert p.refundable is True
print('package ok:', p.name, p.base_price, p.status.value)
"
```
Expected: `package ok: Cancun 5500 active`.

- [ ] **Step 5: Commit**

```bash
git add after/app/domain/packages/package_id.py after/app/domain/packages/package_status.py after/app/domain/packages/travel_package.py
git commit -m "feat(after): add TravelPackage domain entity with refundable flag (LSP cure)"
```

---

## Task 6: Domain — Package repository Protocols (ISP)

**Files:**
- Create: `after/app/domain/packages/package_repository.py`

- [ ] **Step 1: Criar `package_repository.py`**

```python
"""Package repository Protocols, segregated per role (ISP cure).

The `before/` version had a single `PackageRepository` with 12 methods.
Tests and use cases had to depend on the whole fat interface. Here we
split into two small Protocols:

- `PackageWriter` — use cases that add/update
- `PackageReader` — use cases that read/filter/list

The concrete SQLAlchemy adapter (in `infra/`) implements BOTH. Only the
CONTRACT surface that each client depends on is small.
"""

from typing import Protocol

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.travel_package import TravelPackage


class PackageWriter(Protocol):
    def add(self, package: TravelPackage) -> TravelPackage: ...
    def update(self, package: TravelPackage) -> TravelPackage: ...


class PackageReader(Protocol):
    def by_id(self, package_id: PackageId) -> TravelPackage | None: ...
    def list(self) -> list[TravelPackage]: ...
    def by_traveler(self, traveler_id: int) -> list[TravelPackage]: ...
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.domain.packages.package_repository import PackageWriter, PackageReader
print('protocols ok:', PackageWriter.__name__, PackageReader.__name__)
"
```
Expected: `protocols ok: PackageWriter PackageReader`.

- [ ] **Step 3: Commit**

```bash
git add after/app/domain/packages/package_repository.py
git commit -m "feat(after): segregate PackageWriter and PackageReader Protocols (ISP cure)"
```

---

## Task 7: Domain — `DiscountPolicy` Protocol + strategies (OCP)

**Files:**
- Create: `after/app/domain/packages/discount_policy.py`

- [ ] **Step 1: Criar `discount_policy.py`**

```python
"""DiscountPolicy — Protocol + strategies.

OCP cure: in `before/`, adding a new discount type meant editing
`calculate_price`'s `if/elif` chain. Here, a new discount is a new class
that implements `DiscountPolicy` — zero edit to existing code.

The strategies match the 5 discount types from `before/` exactly, so
equivalence contracts pass without change:

- seasonal: 15% off
- black_friday: 30% off
- corporate: flat -200 (floored at 0)
- cyber_monday: 25% off if base > 5000, else 10%
- none: unchanged
"""

from decimal import Decimal
from typing import Protocol

from after.app.domain.packages.travel_package import TravelPackage


class DiscountPolicy(Protocol):
    def apply(self, package: TravelPackage) -> Decimal: ...


class NoDiscount:
    def apply(self, package: TravelPackage) -> Decimal:
        return package.base_price


class SeasonalDiscount:
    def apply(self, package: TravelPackage) -> Decimal:
        return (package.base_price * Decimal("0.85")).quantize(Decimal("0.01"))


class BlackFridayDiscount:
    def apply(self, package: TravelPackage) -> Decimal:
        return (package.base_price * Decimal("0.70")).quantize(Decimal("0.01"))


class CorporateDiscount:
    FLAT_OFF = Decimal("200.00")

    def apply(self, package: TravelPackage) -> Decimal:
        return max(Decimal("0"), package.base_price - self.FLAT_OFF)


class CyberMondayDiscount:
    THRESHOLD = Decimal("5000")

    def apply(self, package: TravelPackage) -> Decimal:
        factor = Decimal("0.75") if package.base_price > self.THRESHOLD else Decimal("0.90")
        return (package.base_price * factor).quantize(Decimal("0.01"))
```

- [ ] **Step 2: Verify (all 5 strategies)**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from decimal import Decimal
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.packages.discount_policy import (
    NoDiscount, SeasonalDiscount, BlackFridayDiscount, CorporateDiscount, CyberMondayDiscount
)

p1000 = TravelPackage(name='p', destination='x', base_price=Decimal('1000'), refundable=True)
p6000 = TravelPackage(name='p', destination='x', base_price=Decimal('6000'), refundable=True)
p2000 = TravelPackage(name='p', destination='x', base_price=Decimal('2000'), refundable=True)

assert NoDiscount().apply(p1000) == Decimal('1000')
assert SeasonalDiscount().apply(p1000) == Decimal('850.00')
assert BlackFridayDiscount().apply(p1000) == Decimal('700.00')
assert CorporateDiscount().apply(p1000) == Decimal('800.00')
assert CyberMondayDiscount().apply(p6000) == Decimal('4500.00')
assert CyberMondayDiscount().apply(p2000) == Decimal('1800.00')
print('strategies ok')
"
```
Expected: `strategies ok`.

- [ ] **Step 3: Commit**

```bash
git add after/app/domain/packages/discount_policy.py
git commit -m "feat(after): add DiscountPolicy Protocol and 5 strategies (OCP cure)"
```

---

## Task 8: Domain — `CancellationPolicy`

**Files:**
- Create: `after/app/domain/packages/cancellation_policy.py`

- [ ] **Step 1: Criar `cancellation_policy.py`**

```python
"""CancellationPolicy — explicit policy for cancelling packages.

LSP cure (part 2): with `refundable: bool` on `TravelPackage`, this policy
decides whether a cancellation is allowed and mutates state consistently.
No subclass lies about `.cancel()` anymore.
"""

from dataclasses import replace
from datetime import datetime, timezone

from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.travel_package import TravelPackage


class CannotCancelError(Exception):
    """Raised when a non-refundable package is asked to cancel."""


class CancellationPolicy:
    def cancel(self, package: TravelPackage) -> TravelPackage:
        """Return a cancelled COPY of the package.

        Raises `CannotCancelError` for non-refundable packages. Callers that
        iterate over mixed packages should check `package.refundable` BEFORE
        calling — the use case `CancelAllOfTraveler` does exactly that and
        skips non-refundables into a separate list instead of raising.
        """
        if not package.refundable:
            raise CannotCancelError(
                f"package {package.id} is non-refundable and cannot be cancelled"
            )
        return replace(
            package,
            status=PackageStatus.CANCELLED,
            cancelled_at=datetime.now(timezone.utc),
        )
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from decimal import Decimal
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.cancellation_policy import CancellationPolicy, CannotCancelError

p = TravelPackage(name='p', destination='x', base_price=Decimal('100'), refundable=True)
q = CancellationPolicy().cancel(p)
assert q.status == PackageStatus.CANCELLED
assert q.cancelled_at is not None
assert p.status == PackageStatus.ACTIVE, 'original must not be mutated'

nr = TravelPackage(name='p', destination='x', base_price=Decimal('100'), refundable=False)
try:
    CancellationPolicy().cancel(nr)
    raise RuntimeError('expected error')
except CannotCancelError as e:
    print('policy ok:', e)
"
```
Expected: `policy ok: package None is non-refundable and cannot be cancelled`.

- [ ] **Step 3: Commit**

```bash
git add after/app/domain/packages/cancellation_policy.py
git commit -m "feat(after): add CancellationPolicy with honest contract (LSP cure part 2)"
```

---

## Task 9: Test fakes — in-memory repositories + notifier

**Files:**
- Create: `after/tests/fakes/in_memory_repositories.py`
- Create: `after/tests/fakes/fake_notifier.py`

- [ ] **Step 1: Criar `in_memory_repositories.py`**

```python
"""In-memory fakes for unit tests — tiny and obvious.

A fake per Protocol. Each fake implements the whole Protocol surface AND
NOTHING ELSE — contrast with the `before/` fake that had to raise
NotImplementedError for 11 of 12 methods.
"""

from dataclasses import replace

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId


class InMemoryTravelerRepository:
    def __init__(self) -> None:
        self._rows: dict[int, Traveler] = {}
        self._next_id = 1

    def add(self, traveler: Traveler) -> Traveler:
        saved = replace(traveler, id=TravelerId(self._next_id))
        self._rows[self._next_id] = saved
        self._next_id += 1
        return saved

    def by_id(self, traveler_id: TravelerId) -> Traveler | None:
        return self._rows.get(int(traveler_id))

    def list(self) -> list[Traveler]:
        return list(self._rows.values())


class InMemoryPackageRepository:
    def __init__(self) -> None:
        self._rows: dict[int, TravelPackage] = {}
        self._next_id = 1

    # --- PackageWriter ---
    def add(self, package: TravelPackage) -> TravelPackage:
        saved = replace(package, id=PackageId(self._next_id))
        self._rows[self._next_id] = saved
        self._next_id += 1
        return saved

    def update(self, package: TravelPackage) -> TravelPackage:
        assert package.id is not None, "update requires persisted package"
        self._rows[int(package.id)] = package
        return package

    # --- PackageReader ---
    def by_id(self, package_id: PackageId) -> TravelPackage | None:
        return self._rows.get(int(package_id))

    def list(self) -> list[TravelPackage]:
        return list(self._rows.values())

    def by_traveler(self, traveler_id: int) -> list[TravelPackage]:
        return [p for p in self._rows.values() if p.traveler_id == traveler_id]
```

- [ ] **Step 2: Criar `fake_notifier.py`**

```python
"""RecordingWelcomeNotifier — captures notifications for assertion."""

from after.app.domain.travelers.traveler import Traveler


class RecordingWelcomeNotifier:
    def __init__(self) -> None:
        self.notified: list[Traveler] = []

    def notify_welcome(self, traveler: Traveler) -> None:
        self.notified.append(traveler)
```

- [ ] **Step 3: Verify imports**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.tests.fakes.in_memory_repositories import InMemoryTravelerRepository, InMemoryPackageRepository
from after.tests.fakes.fake_notifier import RecordingWelcomeNotifier
print('fakes ok')
"
```
Expected: `fakes ok`.

- [ ] **Step 4: Commit**

```bash
git add after/tests/fakes/
git commit -m "test(after): add in-memory repository fakes and recording notifier"
```

---

## Task 10: Application — `CreateTraveler` use case (TDD)

**Files:**
- Create: `after/tests/application/travelers/test_create_traveler.py`
- Create: `after/app/application/travelers/create_traveler.py`

- [ ] **Step 1: Escrever teste falhando**

Criar `after/tests/application/travelers/test_create_traveler.py`:

```python
"""Unit tests for CreateTraveler use case.

These tests run in milliseconds against fakes — no database, no HTTP. That
is the testability payoff of applying DIP: the use case depends on
Protocols, so tests inject fakes.
"""

import pytest

from after.app.application.travelers.create_traveler import (
    CreateTraveler,
    CreateTravelerInput,
)
from after.tests.fakes.fake_notifier import RecordingWelcomeNotifier
from after.tests.fakes.in_memory_repositories import InMemoryTravelerRepository


def test_creates_persists_and_notifies():
    repo = InMemoryTravelerRepository()
    notifier = RecordingWelcomeNotifier()
    use_case = CreateTraveler(repo=repo, notifier=notifier)

    traveler = use_case.execute(
        CreateTravelerInput(
            name="Maria Silva", email="maria@example.com", document="12345678909"
        )
    )

    assert traveler.id is not None
    assert traveler.name == "Maria Silva"
    assert repo.list() == [traveler]
    assert notifier.notified == [traveler]


def test_rejects_invalid_document():
    repo = InMemoryTravelerRepository()
    notifier = RecordingWelcomeNotifier()
    use_case = CreateTraveler(repo=repo, notifier=notifier)

    with pytest.raises(ValueError, match="11-digit"):
        use_case.execute(
            CreateTravelerInput(name="Maria", email="m@x.com", document="123")
        )

    assert repo.list() == []
    assert notifier.notified == []


def test_rejects_short_name():
    repo = InMemoryTravelerRepository()
    notifier = RecordingWelcomeNotifier()
    use_case = CreateTraveler(repo=repo, notifier=notifier)

    with pytest.raises(ValueError, match="at least 2"):
        use_case.execute(
            CreateTravelerInput(name="M", email="m@x.com", document="12345678909")
        )

    assert repo.list() == []
    assert notifier.notified == []
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/application/travelers/test_create_traveler.py -v
```
Expected: ImportError / ModuleNotFoundError — the module `create_traveler` doesn't exist yet.

- [ ] **Step 3: Criar `create_traveler.py`**

```python
"""CreateTraveler use case.

Single responsibility: take validated input, build a domain entity, persist,
notify. Dependencies are Protocols — no SQLAlchemy, no FastAPI.
"""

from dataclasses import dataclass

from after.app.domain.travelers.document import Document
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_repository import TravelerRepository
from after.app.domain.travelers.welcome_notifier import WelcomeNotifier


@dataclass(slots=True)
class CreateTravelerInput:
    name: str
    email: str
    document: str


class CreateTraveler:
    def __init__(self, repo: TravelerRepository, notifier: WelcomeNotifier):
        self._repo = repo
        self._notifier = notifier

    def execute(self, input: CreateTravelerInput) -> Traveler:
        traveler = Traveler(
            name=input.name,
            email=Email(input.email),
            document=Document(input.document),
        )
        saved = self._repo.add(traveler)
        self._notifier.notify_welcome(saved)
        return saved
```

- [ ] **Step 4: Rodar testes e ver passar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/application/travelers/test_create_traveler.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add after/tests/application/travelers/test_create_traveler.py after/app/application/travelers/create_traveler.py
git commit -m "feat(after): add CreateTraveler use case with unit tests"
```

---

## Task 11: Application — `ListTravelers` + `GetTraveler` use cases

**Files:**
- Create: `after/app/application/travelers/list_travelers.py`
- Create: `after/app/application/travelers/get_traveler.py`

- [ ] **Step 1: Criar `list_travelers.py`**

```python
"""ListTravelers use case — thin wrapper around the repository."""

from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_repository import TravelerRepository


class ListTravelers:
    def __init__(self, repo: TravelerRepository):
        self._repo = repo

    def execute(self) -> list[Traveler]:
        return self._repo.list()
```

- [ ] **Step 2: Criar `get_traveler.py`**

```python
"""GetTraveler use case."""

from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.domain.travelers.traveler_repository import TravelerRepository


class TravelerNotFound(Exception):
    """Raised when a traveler lookup misses."""


class GetTraveler:
    def __init__(self, repo: TravelerRepository):
        self._repo = repo

    def execute(self, traveler_id: TravelerId) -> Traveler:
        found = self._repo.by_id(traveler_id)
        if found is None:
            raise TravelerNotFound(f"traveler {traveler_id} not found")
        return found
```

- [ ] **Step 3: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.application.travelers.list_travelers import ListTravelers
from after.app.application.travelers.get_traveler import GetTraveler, TravelerNotFound
from after.app.domain.travelers.traveler_id import TravelerId
from after.tests.fakes.in_memory_repositories import InMemoryTravelerRepository

repo = InMemoryTravelerRepository()
assert ListTravelers(repo).execute() == []

try:
    GetTraveler(repo).execute(TravelerId(1))
    raise RuntimeError('expected error')
except TravelerNotFound:
    pass
print('list + get ok')
"
```
Expected: `list + get ok`.

- [ ] **Step 4: Commit**

```bash
git add after/app/application/travelers/list_travelers.py after/app/application/travelers/get_traveler.py
git commit -m "feat(after): add ListTravelers and GetTraveler use cases"
```

---

## Task 12: Application — `CreatePackage` + `ListPackages`

**Files:**
- Create: `after/app/application/packages/create_package.py`
- Create: `after/app/application/packages/list_packages.py`

- [ ] **Step 1: Criar `create_package.py`**

```python
"""CreatePackage use case.

Note: depends ONLY on `PackageWriter`, not the full repo. Even if a future
refactor adds 10 reader methods, this use case — and its fake in tests —
does not grow.
"""

from dataclasses import dataclass
from decimal import Decimal

from after.app.domain.packages.package_repository import PackageWriter
from after.app.domain.packages.travel_package import TravelPackage


@dataclass(slots=True)
class CreatePackageInput:
    name: str
    destination: str
    base_price: Decimal
    refundable: bool
    traveler_id: int | None = None


class CreatePackage:
    def __init__(self, writer: PackageWriter):
        self._writer = writer

    def execute(self, input: CreatePackageInput) -> TravelPackage:
        package = TravelPackage(
            name=input.name,
            destination=input.destination,
            base_price=input.base_price,
            refundable=input.refundable,
            traveler_id=input.traveler_id,
        )
        return self._writer.add(package)
```

- [ ] **Step 2: Criar `list_packages.py`**

```python
"""ListPackages use case — depends only on PackageReader."""

from after.app.domain.packages.package_repository import PackageReader
from after.app.domain.packages.travel_package import TravelPackage


class ListPackages:
    def __init__(self, reader: PackageReader):
        self._reader = reader

    def execute(self) -> list[TravelPackage]:
        return self._reader.list()
```

- [ ] **Step 3: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from decimal import Decimal
from after.app.application.packages.create_package import CreatePackage, CreatePackageInput
from after.app.application.packages.list_packages import ListPackages
from after.tests.fakes.in_memory_repositories import InMemoryPackageRepository

repo = InMemoryPackageRepository()
pkg = CreatePackage(repo).execute(CreatePackageInput(name='Cancun', destination='MX', base_price=Decimal('5500'), refundable=True))
assert pkg.id is not None
assert ListPackages(repo).execute() == [pkg]
print('create/list package ok')
"
```
Expected: `create/list package ok`.

- [ ] **Step 4: Commit**

```bash
git add after/app/application/packages/create_package.py after/app/application/packages/list_packages.py
git commit -m "feat(after): add CreatePackage and ListPackages use cases (ISP on reader/writer)"
```

---

## Task 13: Application — `CalculatePackagePrice` (TDD)

**Files:**
- Create: `after/tests/application/packages/test_calculate_price.py`
- Create: `after/app/application/packages/calculate_price.py`

- [ ] **Step 1: Escrever testes falhando**

Criar `after/tests/application/packages/test_calculate_price.py`:

```python
"""Unit tests for CalculatePackagePrice — each strategy isolated.

This is the OCP payoff: 6 test cases, each exercising a different policy
with ZERO setup — the use case composes policies without a banco.
"""

from decimal import Decimal

import pytest

from after.app.application.packages.calculate_price import CalculatePackagePrice
from after.app.domain.packages.discount_policy import (
    BlackFridayDiscount,
    CorporateDiscount,
    CyberMondayDiscount,
    NoDiscount,
    SeasonalDiscount,
)
from after.app.domain.packages.travel_package import TravelPackage


def _pkg(price: str) -> TravelPackage:
    return TravelPackage(
        name="p", destination="x", base_price=Decimal(price), refundable=True
    )


@pytest.mark.parametrize(
    "policy, base, expected",
    [
        (NoDiscount(),           "1000", "1000"),
        (SeasonalDiscount(),     "1000",  "850.00"),
        (BlackFridayDiscount(),  "1000",  "700.00"),
        (CorporateDiscount(),    "1000",  "800.00"),
        (CyberMondayDiscount(),  "6000", "4500.00"),
        (CyberMondayDiscount(),  "2000", "1800.00"),
    ],
)
def test_price_per_policy(policy, base, expected):
    result = CalculatePackagePrice(policy).execute(_pkg(base))
    assert result == Decimal(expected)


def test_corporate_does_not_go_negative():
    result = CalculatePackagePrice(CorporateDiscount()).execute(_pkg("100"))
    assert result == Decimal("0")
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/application/packages/test_calculate_price.py -v
```
Expected: ImportError on `calculate_price`.

- [ ] **Step 3: Criar `calculate_price.py`**

```python
"""CalculatePackagePrice use case.

Composes with a DiscountPolicy. A new discount type is a new policy class
— the use case itself never changes. That is OCP.
"""

from decimal import Decimal

from after.app.domain.packages.discount_policy import DiscountPolicy
from after.app.domain.packages.travel_package import TravelPackage


class CalculatePackagePrice:
    def __init__(self, policy: DiscountPolicy):
        self._policy = policy

    def execute(self, package: TravelPackage) -> Decimal:
        return self._policy.apply(package)
```

- [ ] **Step 4: Rodar e ver passar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/application/packages/test_calculate_price.py -v
```
Expected: 7 passed (6 parametrized + 1 corporate floor).

- [ ] **Step 5: Commit**

```bash
git add after/tests/application/packages/test_calculate_price.py after/app/application/packages/calculate_price.py
git commit -m "feat(after): add CalculatePackagePrice use case with per-policy unit tests"
```

---

## Task 14: Application — `CancelAllOfTraveler` (TDD, LSP cure)

**Files:**
- Create: `after/tests/application/packages/test_cancel_all_of_traveler.py`
- Create: `after/app/application/packages/cancel_all_of_traveler.py`

- [ ] **Step 1: Escrever testes falhando**

Criar `after/tests/application/packages/test_cancel_all_of_traveler.py`:

```python
"""Unit tests for CancelAllOfTraveler — the LSP cure use case.

The `before/` version raised mid-loop on NonRefundablePackage. The `after/`
version returns a partial result: cancelled + skipped. Callers KNOW what
they got.
"""

from dataclasses import replace
from decimal import Decimal

from after.app.application.packages.cancel_all_of_traveler import (
    CancelAllOfTraveler,
    CancelResult,
)
from after.app.domain.packages.cancellation_policy import CancellationPolicy
from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.travel_package import TravelPackage
from after.tests.fakes.in_memory_repositories import InMemoryPackageRepository


def _seed(repo: InMemoryPackageRepository, traveler_id: int, refundable_flags: list[bool]) -> None:
    for i, r in enumerate(refundable_flags):
        repo.add(
            TravelPackage(
                name=f"p-{i}",
                destination="X",
                base_price=Decimal("100"),
                refundable=r,
                traveler_id=traveler_id,
            )
        )


def test_cancels_every_refundable_package():
    repo = InMemoryPackageRepository()
    _seed(repo, traveler_id=1, refundable_flags=[True, True, True])
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    result = use_case.execute(traveler_id=1)

    assert isinstance(result, CancelResult)
    assert len(result.cancelled) == 3
    assert len(result.skipped) == 0
    assert all(p.status == PackageStatus.CANCELLED for p in result.cancelled)


def test_skips_non_refundable_and_reports():
    repo = InMemoryPackageRepository()
    _seed(repo, traveler_id=1, refundable_flags=[True, False, True])
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    result = use_case.execute(traveler_id=1)

    assert len(result.cancelled) == 2
    assert len(result.skipped) == 1
    assert all(p.refundable is False for p in result.skipped)


def test_empty_traveler_returns_empty_result():
    repo = InMemoryPackageRepository()
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    result = use_case.execute(traveler_id=999)

    assert result.cancelled == []
    assert result.skipped == []


def test_cancelled_packages_are_persisted_via_update():
    repo = InMemoryPackageRepository()
    _seed(repo, traveler_id=1, refundable_flags=[True])
    use_case = CancelAllOfTraveler(repo=repo, policy=CancellationPolicy())

    use_case.execute(traveler_id=1)

    persisted = repo.by_traveler(1)
    assert len(persisted) == 1
    assert persisted[0].status == PackageStatus.CANCELLED
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/application/packages/test_cancel_all_of_traveler.py -v
```
Expected: ImportError.

- [ ] **Step 3: Criar `cancel_all_of_traveler.py`**

```python
"""CancelAllOfTraveler — honest partial-result use case.

The LSP cure in action: no `for p in packages: p.cancel()` bomb. We ask
the policy whether each package is cancellable, and return both lists.
"""

from dataclasses import dataclass

from after.app.domain.packages.cancellation_policy import CancellationPolicy
from after.app.domain.packages.package_repository import PackageReader, PackageWriter
from after.app.domain.packages.travel_package import TravelPackage


@dataclass(slots=True)
class CancelResult:
    cancelled: list[TravelPackage]
    skipped: list[TravelPackage]


class CancelAllOfTraveler:
    def __init__(
        self,
        repo: PackageReader,
        policy: CancellationPolicy,
        writer: PackageWriter | None = None,
    ):
        # We accept a single repo for both read + write when the concrete
        # implementation satisfies both Protocols (SQLAlchemy adapter does).
        # `writer` overrides if different bindings are needed in tests.
        self._reader = repo
        self._writer: PackageWriter = writer if writer is not None else repo  # type: ignore[assignment]
        self._policy = policy

    def execute(self, traveler_id: int) -> CancelResult:
        packages = self._reader.by_traveler(traveler_id)
        cancelled: list[TravelPackage] = []
        skipped: list[TravelPackage] = []
        for package in packages:
            if package.refundable:
                updated = self._policy.cancel(package)
                self._writer.update(updated)
                cancelled.append(updated)
            else:
                skipped.append(package)
        return CancelResult(cancelled=cancelled, skipped=skipped)
```

- [ ] **Step 4: Rodar e ver passar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/application/packages/test_cancel_all_of_traveler.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add after/tests/application/packages/test_cancel_all_of_traveler.py after/app/application/packages/cancel_all_of_traveler.py
git commit -m "feat(after): add CancelAllOfTraveler with partial-result contract (LSP cure)"
```

---

## Task 15: Infra — database + SQLAlchemy models

**Files:**
- Create: `after/app/infra/database.py`
- Create: `after/app/infra/persistence/models.py`

- [ ] **Step 1: Criar `infra/database.py`**

```python
"""SQLAlchemy engine + session factory for the `after/` version.

Exposes `engine`, `SessionLocal`, and `Base`. Consumed ONLY by `infra/`
modules. The domain doesn't know this file exists.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./after.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for infra ORM models — separate from domain."""
    pass
```

- [ ] **Step 2: Criar `infra/persistence/models.py`**

```python
"""SQLAlchemy models — INFRA, not domain.

Keeping these separate from domain entities is the DIP insight: the shape
of persistence (columns, indexes, relationships) is a detail. The domain
dataclasses live in `domain/` and know nothing about this file.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from after.app.infra.database import Base


class TravelerModel(Base):
    __tablename__ = "travelers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    document = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    packages = relationship("PackageModel", back_populates="traveler")


class PackageModel(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    base_price = Column(Numeric(12, 2), nullable=False)
    refundable = Column(Boolean, nullable=False, default=True)
    status = Column(String, nullable=False, default="active")
    cancelled_at = Column(DateTime, nullable=True)
    traveler_id = Column(Integer, ForeignKey("travelers.id"), nullable=True)

    traveler = relationship("TravelerModel", back_populates="packages")
```

- [ ] **Step 3: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.infra.database import engine, SessionLocal, Base
from after.app.infra.persistence.models import TravelerModel, PackageModel
Base.metadata.create_all(bind=engine)
print('infra models ok, tables:', list(Base.metadata.tables.keys()))
import os
if os.path.exists('after.db'): os.remove('after.db')
"
```
Expected: `infra models ok, tables: ['travelers', 'packages']`.

- [ ] **Step 4: Commit**

```bash
git add after/app/infra/database.py after/app/infra/persistence/models.py
git commit -m "feat(after): add infra database setup and SQLAlchemy models"
```

---

## Task 16: Infra — SQLAlchemy traveler repository

**Files:**
- Create: `after/app/infra/persistence/sqlalchemy_traveler_repository.py`

- [ ] **Step 1: Criar o adapter**

```python
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
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.infra.database import Base, SessionLocal, engine
from after.app.infra.persistence.sqlalchemy_traveler_repository import SqlAlchemyTravelerRepository
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.document import Document
from after.app.domain.travelers.traveler_id import TravelerId

Base.metadata.create_all(bind=engine)
session = SessionLocal()
repo = SqlAlchemyTravelerRepository(session)
t = Traveler(name='Maria', email=Email('m@x.com'), document=Document('12345678909'))
saved = repo.add(t)
assert saved.id is not None
again = repo.by_id(TravelerId(int(saved.id)))
assert again is not None and again.name == 'Maria'
assert len(repo.list()) == 1
session.close()
import os
if os.path.exists('after.db'): os.remove('after.db')
print('sqlalchemy traveler repo ok')
"
```
Expected: `sqlalchemy traveler repo ok`.

- [ ] **Step 3: Commit**

```bash
git add after/app/infra/persistence/sqlalchemy_traveler_repository.py
git commit -m "feat(after): add SqlAlchemyTravelerRepository adapter"
```

---

## Task 17: Infra — SQLAlchemy package repository (implements both Protocols)

**Files:**
- Create: `after/app/infra/persistence/sqlalchemy_package_repository.py`

- [ ] **Step 1: Criar o adapter**

```python
"""SqlAlchemyPackageRepository — satisfies BOTH PackageWriter and PackageReader.

The ISP cure at the domain level: clients see segregated interfaces. The
concrete adapter can still unify implementation — separation of concern
was about the CONTRACT surface, not the implementation.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from after.app.domain.packages.package_id import PackageId
from after.app.domain.packages.package_status import PackageStatus
from after.app.domain.packages.travel_package import TravelPackage
from after.app.infra.persistence.models import PackageModel


def _to_domain(row: PackageModel) -> TravelPackage:
    return TravelPackage(
        name=row.name,
        destination=row.destination,
        base_price=Decimal(str(row.base_price)),
        refundable=bool(row.refundable),
        status=PackageStatus(row.status),
        cancelled_at=row.cancelled_at,
        traveler_id=row.traveler_id,
        id=PackageId(row.id),
    )


def _to_row(p: TravelPackage) -> PackageModel:
    return PackageModel(
        name=p.name,
        destination=p.destination,
        base_price=p.base_price,
        refundable=p.refundable,
        status=p.status.value,
        cancelled_at=p.cancelled_at,
        traveler_id=p.traveler_id,
    )


class SqlAlchemyPackageRepository:
    def __init__(self, session: Session):
        self._session = session

    # --- PackageWriter ---
    def add(self, package: TravelPackage) -> TravelPackage:
        row = _to_row(package)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return _to_domain(row)

    def update(self, package: TravelPackage) -> TravelPackage:
        assert package.id is not None, "update requires persisted package"
        row = self._session.get(PackageModel, int(package.id))
        if row is None:
            raise LookupError(f"package {package.id} not found")
        row.name = package.name
        row.destination = package.destination
        row.base_price = package.base_price
        row.refundable = package.refundable
        row.status = package.status.value
        row.cancelled_at = package.cancelled_at
        row.traveler_id = package.traveler_id
        self._session.commit()
        self._session.refresh(row)
        return _to_domain(row)

    # --- PackageReader ---
    def by_id(self, package_id: PackageId) -> TravelPackage | None:
        row = self._session.get(PackageModel, int(package_id))
        return _to_domain(row) if row is not None else None

    def list(self) -> list[TravelPackage]:
        rows = self._session.query(PackageModel).all()
        return [_to_domain(r) for r in rows]

    def by_traveler(self, traveler_id: int) -> list[TravelPackage]:
        rows = (
            self._session.query(PackageModel)
            .filter(PackageModel.traveler_id == traveler_id)
            .all()
        )
        return [_to_domain(r) for r in rows]
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from decimal import Decimal
from after.app.infra.database import Base, SessionLocal, engine
from after.app.infra.persistence.sqlalchemy_package_repository import SqlAlchemyPackageRepository
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.packages.package_status import PackageStatus

Base.metadata.create_all(bind=engine)
session = SessionLocal()
repo = SqlAlchemyPackageRepository(session)
p = TravelPackage(name='P', destination='X', base_price=Decimal('1000'), refundable=True)
saved = repo.add(p)
assert saved.id is not None
updated = repo.update(saved.__class__(name='P', destination='X', base_price=Decimal('1000'), refundable=True, status=PackageStatus.CANCELLED, id=saved.id))
assert updated.status == PackageStatus.CANCELLED
assert len(repo.list()) == 1
session.close()
import os
if os.path.exists('after.db'): os.remove('after.db')
print('sqlalchemy package repo ok')
"
```
Expected: `sqlalchemy package repo ok`.

- [ ] **Step 3: Commit**

```bash
git add after/app/infra/persistence/sqlalchemy_package_repository.py
git commit -m "feat(after): add SqlAlchemyPackageRepository (satisfies Writer and Reader)"
```

---

## Task 18: Infra — `StdoutWelcomeNotifier`

**Files:**
- Create: `after/app/infra/notifications/stdout_welcome_notifier.py`

- [ ] **Step 1: Criar**

```python
"""StdoutWelcomeNotifier — prints to stdout, fake-SMTP style.

Real systems would swap this for an email service adapter that implements
the same `WelcomeNotifier` Protocol. That is the DIP payoff: one config
line in the composition root, no code change anywhere else.
"""

from after.app.domain.travelers.traveler import Traveler


class StdoutWelcomeNotifier:
    def notify_welcome(self, traveler: Traveler) -> None:
        print(f"[FAKE SMTP] Welcome email sent to {traveler.email}")
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.document import Document
from after.app.infra.notifications.stdout_welcome_notifier import StdoutWelcomeNotifier

t = Traveler(name='X', email=Email('m@x.com'), document=Document('12345678909'))
StdoutWelcomeNotifier().notify_welcome(t)
print('notifier ok')
"
```
Expected: `[FAKE SMTP] Welcome email sent to m@x.com` then `notifier ok`.

- [ ] **Step 3: Commit**

```bash
git add after/app/infra/notifications/stdout_welcome_notifier.py
git commit -m "feat(after): add StdoutWelcomeNotifier infra adapter"
```

---

## Task 19: Presentation — Pydantic schemas

**Files:**
- Create: `after/app/presentation/schemas.py`

- [ ] **Step 1: Criar schemas**

```python
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
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from decimal import Decimal
from after.app.presentation.schemas import TravelerIn, TravelerOut, PackageIn, PackageOut, PriceCalcIn, PriceCalcOut, CancelResultOut
from after.app.domain.travelers.traveler import Traveler
from after.app.domain.travelers.email import Email
from after.app.domain.travelers.document import Document
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.domain.packages.travel_package import TravelPackage
from after.app.domain.packages.package_id import PackageId

t = Traveler(name='Maria', email=Email('m@x.com'), document=Document('12345678909'), id=TravelerId(1))
out = TravelerOut.from_domain(t)
assert out.id == 1

p = TravelPackage(name='P', destination='X', base_price=Decimal('100'), refundable=False, id=PackageId(1))
po = PackageOut.from_domain(p)
assert po.kind == 'non_refundable'
assert po.refundable is False

print('schemas ok', out.model_dump(), po.model_dump())
"
```
Expected: prints schema dumps, no errors.

- [ ] **Step 3: Commit**

```bash
git add after/app/presentation/schemas.py
git commit -m "feat(after): add Pydantic presentation schemas with kind legacy + refundable"
```

---

## Task 20: Presentation — `dependencies.py` (composition root)

**Files:**
- Create: `after/app/presentation/dependencies.py`

- [ ] **Step 1: Criar dependencies**

```python
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
```

- [ ] **Step 2: Verify**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run python -c "
from after.app.presentation.dependencies import (
    get_db, get_create_traveler_uc, get_list_travelers_uc, get_get_traveler_uc,
    get_create_package_uc, get_list_packages_uc, calculate_price_uc_for, get_cancel_all_uc,
    _pick_discount_policy,
)
from after.app.domain.packages.discount_policy import BlackFridayDiscount
assert isinstance(_pick_discount_policy('black_friday'), BlackFridayDiscount)
print('dependencies ok')
"
```
Expected: `dependencies ok`.

- [ ] **Step 3: Commit**

```bash
git add after/app/presentation/dependencies.py
git commit -m "feat(after): add composition root with Depends providers"
```

---

## Task 21: Presentation — traveler router (thin handlers)

**Files:**
- Create: `after/app/presentation/routers/travelers.py`

- [ ] **Step 1: Criar router**

```python
"""Traveler HTTP router — thin handlers, DIP-clean.

Each handler is 3-5 lines: parse input, call use case, format output. No
SQLAlchemy import, no business rules, no inline validation.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from after.app.application.travelers.create_traveler import CreateTraveler
from after.app.application.travelers.get_traveler import GetTraveler, TravelerNotFound
from after.app.application.travelers.list_travelers import ListTravelers
from after.app.domain.travelers.traveler_id import TravelerId
from after.app.presentation.dependencies import (
    get_create_traveler_uc,
    get_get_traveler_uc,
    get_list_travelers_uc,
)
from after.app.presentation.schemas import TravelerIn, TravelerOut

router = APIRouter(prefix="/travelers", tags=["travelers"])


@router.post("", response_model=TravelerOut, status_code=201)
def create_traveler(
    body: TravelerIn,
    use_case: Annotated[CreateTraveler, Depends(get_create_traveler_uc)],
) -> TravelerOut:
    try:
        traveler = use_case.execute(body.to_input())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return TravelerOut.from_domain(traveler)


@router.get("", response_model=list[TravelerOut])
def list_travelers(
    use_case: Annotated[ListTravelers, Depends(get_list_travelers_uc)],
) -> list[TravelerOut]:
    return [TravelerOut.from_domain(t) for t in use_case.execute()]


@router.get("/{traveler_id}", response_model=TravelerOut)
def get_traveler(
    traveler_id: int,
    use_case: Annotated[GetTraveler, Depends(get_get_traveler_uc)],
) -> TravelerOut:
    try:
        traveler = use_case.execute(TravelerId(traveler_id))
    except TravelerNotFound:
        raise HTTPException(status_code=404, detail="traveler not found")
    return TravelerOut.from_domain(traveler)
```

- [ ] **Step 2: Commit**

```bash
git add after/app/presentation/routers/travelers.py
git commit -m "feat(after): add thin traveler router (handlers 3-5 lines)"
```

---

## Task 22: Presentation — package router

**Files:**
- Create: `after/app/presentation/routers/packages.py`

- [ ] **Step 1: Criar router**

```python
"""Package HTTP router.

Owns /packages* plus the DELETE /travelers/{id}/packages endpoint. The
cancel-all endpoint now returns 200 + partial-result JSON — the LSP bomb
is gone.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from after.app.application.packages.calculate_price import CalculatePackagePrice
from after.app.application.packages.cancel_all_of_traveler import CancelAllOfTraveler
from after.app.application.packages.create_package import CreatePackage
from after.app.application.packages.list_packages import ListPackages
from after.app.domain.packages.package_id import PackageId
from after.app.presentation.dependencies import (
    calculate_price_uc_for,
    get_cancel_all_uc,
    get_create_package_uc,
    get_list_packages_uc,
    get_package_repo,
)
from after.app.presentation.schemas import (
    CancelResultOut,
    PackageIn,
    PackageOut,
    PriceCalcIn,
    PriceCalcOut,
)

router = APIRouter(tags=["packages"])


@router.post("/packages", response_model=PackageOut, status_code=201)
def create_package(
    body: PackageIn,
    use_case: Annotated[CreatePackage, Depends(get_create_package_uc)],
) -> PackageOut:
    return PackageOut.from_domain(use_case.execute(body.to_input()))


@router.get("/packages", response_model=list[PackageOut])
def list_packages(
    use_case: Annotated[ListPackages, Depends(get_list_packages_uc)],
) -> list[PackageOut]:
    return [PackageOut.from_domain(p) for p in use_case.execute()]


@router.post("/packages/{package_id}/price", response_model=PriceCalcOut)
def price_of_package(
    package_id: int,
    body: PriceCalcIn,
    repo: Annotated[
        "SqlAlchemyPackageRepository",  # noqa: F821 — string avoids circular
        Depends(get_package_repo),
    ],
) -> PriceCalcOut:
    package = repo.by_id(PackageId(package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="package not found")
    try:
        use_case = calculate_price_uc_for(body.discount_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    final = use_case.execute(package)
    return PriceCalcOut(
        package_id=int(package.id) if package.id is not None else 0,
        discount_type=body.discount_type,
        base_price=float(package.base_price),
        final_price=float(final),
    )


@router.delete("/travelers/{traveler_id}/packages", response_model=CancelResultOut)
def cancel_all(
    traveler_id: int,
    use_case: Annotated[CancelAllOfTraveler, Depends(get_cancel_all_uc)],
) -> CancelResultOut:
    result = use_case.execute(traveler_id=traveler_id)
    return CancelResultOut(
        cancelled=len(result.cancelled),
        cancelled_ids=[int(p.id) for p in result.cancelled if p.id is not None],
        skipped_ids=[int(p.id) for p in result.skipped if p.id is not None],
    )
```

- [ ] **Step 2: Commit**

```bash
git add after/app/presentation/routers/packages.py
git commit -m "feat(after): add package router with 200-graceful cancel-all"
```

---

## Task 23: Composition — `main.py`

**Files:**
- Create: `after/app/main.py`

- [ ] **Step 1: Criar main**

```python
"""FastAPI entrypoint for the `after/` version.

Run:
    uv run uvicorn after.app.main:app --port 8001 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from after.app.infra.database import Base, engine
from after.app.infra.persistence import models  # noqa: F401 — register on Base.metadata
from after.app.presentation.routers import packages, travelers


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Just Travel — SOLID talk (AFTER)",
    description=(
        "Versão refatorada do CRUD com Clean Arch minimalista e SOLID aplicado. "
        "Comportamento HTTP idêntico ao `before/` — veja tests/test_equivalence_contracts.py."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(travelers.router)
app.include_router(packages.router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "version": f"after/{app.version}"}
```

- [ ] **Step 2: Smoke test**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && rm -f after.db && uv run python -c "
from fastapi.testclient import TestClient
from after.app.main import app

with TestClient(app) as c:
    assert c.get('/health').json() == {'status':'ok','version':'after/0.1.0'}
    r = c.post('/travelers', json={'name':'Maria','email':'m@x.com','document':'12345678909'})
    assert r.status_code == 201, r.text
    tid = r.json()['id']
    r = c.post('/packages', json={'name':'Cancun','destination':'MX','base_price':5500,'kind':'standard','traveler_id':tid})
    assert r.status_code == 201, r.text
    pkg_id = r.json()['id']
    r = c.post(f'/packages/{pkg_id}/price', json={'discount_type':'black_friday'})
    assert r.status_code == 200 and r.json()['final_price'] == 3850.0
    # Cancel-all with a non-refundable: should return 200 now
    r = c.post('/packages', json={'name':'NR','destination':'Y','base_price':100,'kind':'non_refundable','traveler_id':tid})
    assert r.status_code == 201, r.text
    r = c.delete(f'/travelers/{tid}/packages')
    assert r.status_code == 200, r.text
    data = r.json()
    assert data['cancelled'] == 1
    assert len(data['skipped_ids']) == 1
    print('after/ wired end-to-end ok:', data)
import os
if os.path.exists('after.db'): os.remove('after.db')
"
```
Expected: `after/ wired end-to-end ok: {...}`.

- [ ] **Step 3: Commit**

```bash
git add after/app/main.py
git commit -m "feat(after): wire FastAPI composition root with lifespan + health"
```

---

## Task 24: Tests — `conftest.py` for `after/`

**Files:**
- Create: `after/tests/conftest.py`

- [ ] **Step 1: Criar conftest**

```python
"""Pytest fixtures for `after/` tests.

Compared to `before/tests/conftest.py`, this is dramatically simpler. DIP
cure in action: we override ONE dependency (`get_db`) instead of
monkeypatching SessionLocal in three module-level locations. The
application remains strictly strict about errors — no `raise_server_exceptions=False`
needed for equivalence tests because the LSP bomb no longer exists.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from after.app.infra.database import Base
from after.app.infra.persistence import models  # noqa: F401
from after.app.main import app as fastapi_app
from after.app.presentation.dependencies import get_db


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_engine):
    """Strict TestClient with a dependency override for the DB session.

    ONE override replaces all three `SessionLocal` monkeypatches from
    `before/`. That single line IS the DIP payoff.
    """
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()
```

- [ ] **Step 2: Collect-only smoke**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests --collect-only -q
```
Expected: no collection errors (there should be tests in `after/tests/application/` from earlier tasks).

- [ ] **Step 3: Commit**

```bash
git add after/tests/conftest.py
git commit -m "test(after): add conftest with single dependency_override (DIP payoff visible)"
```

---

## Task 25: Tests — equivalence contracts (the big one)

**Files:**
- Create: `after/tests/test_equivalence_contracts.py`

- [ ] **Step 1: Criar os 14 testes de equivalência**

```python
"""Equivalence contracts for `after/` — the same 13 HTTP tests from `before/`
plus 1 new test that describes the graceful cancel-all behavior.

These tests exist in two places (before/ and after/) on purpose: they are
the formal proof that the SOLID refactoring did NOT change observable
behavior. The only test that CHANGES between before/ and after/ is the
LSP-trap one: before/ asserts 5xx; after/ asserts the partial-result
payload.
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
            "document": "123",
        },
    )
    assert response.status_code >= 400


def test_list_travelers_returns_created_items(client: TestClient):
    client.post(
        "/travelers",
        json={"name": "Ana", "email": "a@x.com", "document": "12345678901"},
    )
    client.post(
        "/travelers",
        json={"name": "Bob", "email": "b@x.com", "document": "12345678902"},
    )

    response = client.get("/travelers")

    assert response.status_code == 200
    data = response.json()
    names = {t["name"] for t in data}
    assert {"Ana", "Bob"} <= names


def test_get_traveler_returns_404_when_missing(client: TestClient):
    response = client.get("/travelers/9999")
    assert response.status_code == 404


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
    names = {p["name"] for p in response.json()}
    assert {"pkg-0", "pkg-1", "pkg-2"} <= names


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
        f"/packages/{pkg_id}/price", json={"discount_type": "none"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["base_price"] == 1000.0
    assert data["final_price"] == 1000.0


def test_price_with_seasonal_discount_is_15_percent_off(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "seasonal"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 850.0


def test_price_with_black_friday_is_30_percent_off(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "black_friday"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 700.0


def test_price_with_corporate_subtracts_200(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "corporate"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 800.0


def test_price_with_cyber_monday_for_high_price_applies_25_percent(client: TestClient):
    pkg_id = _create_package(client, 6000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "cyber_monday"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 4500.0


def test_price_with_cyber_monday_for_low_price_applies_10_percent(client: TestClient):
    pkg_id = _create_package(client, 2000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "cyber_monday"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 1800.0


# ---------- Cancel-all (LSP cure) ----------


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
    data = response.json()
    assert data["cancelled"] == 3
    assert data["skipped_ids"] == []


def test_cancel_all_skips_non_refundable_and_reports_partial_result(client: TestClient):
    """LSP cure contract — after/ ONLY.

    Replaces `test_cancel_all_fails_when_any_package_is_non_refundable` from
    `before/`. The 500 is gone; we get a 200 with structured cancelled/skipped
    info. That is the whole point of the LSP refactor.
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

    assert response.status_code == 200
    data = response.json()
    assert data["cancelled"] == 1
    assert len(data["skipped_ids"]) == 1
```

- [ ] **Step 2: Rodar os 14 equivalence tests**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests/test_equivalence_contracts.py -v
```
Expected: 14 passed.

- [ ] **Step 3: Rodar a suíte INTEIRA (unit + equivalence)**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest after/tests -v
```
Expected: all application unit tests + 14 equivalence contracts all pass.

- [ ] **Step 4: Commit**

```bash
git add after/tests/test_equivalence_contracts.py
git commit -m "test(after): add equivalence contracts (13 mirror + 1 LSP-cure)"
```

---

## Task 26: Manual end-to-end smoke of `after/`

**Files:** none (manual validation only)

- [ ] **Step 1: Start server**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && rm -f after.db
cd /Users/luizcampos/Documents/lectures/just-travel && uv run uvicorn after.app.main:app --port 8001 > /tmp/uvicorn_after.log 2>&1 &
```

Wait for it to boot:
```bash
for i in 1 2 3 4 5; do
  curl -sf http://localhost:8001/health && break
  sleep 1
done
```
Expected: `{"status":"ok","version":"after/0.1.0"}`.

- [ ] **Step 2: Create a traveler + package + calculate black-friday price**

```bash
curl -s -X POST http://localhost:8001/travelers \
  -H "Content-Type: application/json" \
  -d '{"name":"Maria","email":"maria@example.com","document":"12345678909"}'
curl -s -X POST http://localhost:8001/packages \
  -H "Content-Type: application/json" \
  -d '{"name":"Cancun","destination":"Cancun","base_price":5500,"kind":"standard","traveler_id":1}'
curl -s -X POST http://localhost:8001/packages/1/price \
  -H "Content-Type: application/json" \
  -d '{"discount_type":"black_friday"}'
```
Expected: `final_price: 3850.0`.

- [ ] **Step 3: Create a non-refundable and exercise graceful cancel-all**

```bash
curl -s -X POST http://localhost:8001/packages \
  -H "Content-Type: application/json" \
  -d '{"name":"NR","destination":"Z","base_price":100,"kind":"non_refundable","traveler_id":1}'
curl -s -X DELETE http://localhost:8001/travelers/1/packages
```
Expected: JSON like `{"cancelled":1,"cancelled_ids":[1],"skipped_ids":[2]}` and status 200 (no 500 — LSP bomb gone).

- [ ] **Step 4: Stop + cleanup**

```bash
pkill -f "uvicorn after.app.main:app" || true
sleep 1
rm -f after.db
```

- [ ] **Step 5: Run both suites to confirm no regression**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && uv run pytest before/tests after/tests -v
```
Expected: all before/ tests still green + all after/ tests green.

- [ ] **Step 6: Commit only if anything changed (should not)**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git status
```
If clean, skip.

---

## Task 27: Update root README — mark Plan B complete

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update `README.md`**

Find:
```markdown
- [`after/`](./after) — mesmo CRUD refatorado com Clean Arch minimalista + SOLID aplicado *(Plan B — em construção)*
```

Change to:
```markdown
- [`after/`](./after) — mesmo CRUD refatorado com Clean Arch minimalista + SOLID aplicado ✅
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: mark Plan B (after/) as completed in root README"
```

---

## Self-Review

### 1. Spec coverage

| Spec section | Task(s) |
|---|---|
| `after/` arquitetura 4 camadas | Tasks 1, 3-8 (domain), 10-14 (application), 15-18 (infra), 19-22 (presentation) |
| `domain/` puro sem deps externas | Tasks 2-8 (todas usando só stdlib + domínios próprios) |
| `application/` use cases (1 por ação) | Tasks 10-14 (CreateTraveler, List, Get, CreatePackage, List, CalculatePrice, CancelAll) |
| `infra/` implementa Protocols | Tasks 15-18 (database, models, 2 repos, notifier) |
| `presentation/` fino | Tasks 19-22 (schemas, dependencies, 2 routers) |
| Composition root | Tasks 20 (dependencies) + 23 (main) |
| Testes unitários na application | Tasks 10, 13, 14 (TDD); Tasks 11, 12 sem teste unitário explícito porque são envelopes triviais sobre repos já testados via equivalence |
| 13 testes de equivalência copiados | Task 25 |
| 1 teste novo pra cancel-all gracioso | Task 25 |
| DIP em `Depends()` nativo | Tasks 20, 24 (override único) |
| OCP via 5 DiscountPolicy strategies | Task 7 |
| ISP via PackageWriter + PackageReader | Task 6 |
| LSP via refundable bool + CancellationPolicy | Tasks 5, 8, 14 |
| SRP via separação Traveler/VO/Repo/Notifier/Pydantic | Tasks 2-4, 15-18, 19 |

### 2. Placeholder scan

Scanned for "TBD", "TODO", "implement later", "similar to Task N", "add appropriate...". None found. Every code step has complete code; every verify step has exact command + expected output.

One intentional loose bit: in Task 22 I used `"SqlAlchemyPackageRepository"` as a **forward-referenced string type hint** with `noqa: F821` to avoid a circular import at module load — this is idiomatic and not a placeholder. The import itself happens via `Depends(get_package_repo)` at call time.

### 3. Type consistency

- `TravelerId = NewType("TravelerId", int)` (Task 2) — used consistently in Tasks 4, 11, 16, 21.
- `PackageId = NewType("PackageId", int)` (Task 5) — used in Tasks 6, 9, 14, 17, 22.
- `TravelerRepository` Protocol signature `add(traveler) -> Traveler` (Task 4) → implemented as such in Task 9 fake and Task 16 real adapter.
- `PackageWriter.add(package) -> TravelPackage`, `PackageWriter.update(package) -> TravelPackage` (Task 6) → match fake (Task 9) and concrete (Task 17).
- `PackageReader.by_id`, `list`, `by_traveler` (Task 6) → match Task 9 fake and Task 17 adapter.
- `DiscountPolicy.apply(package) -> Decimal` (Task 7) → used in Task 13 tests and Task 22 route.
- `CancellationPolicy.cancel(package) -> TravelPackage` (Task 8) → used in Task 14 use case.
- `CreateTraveler(repo, notifier)` (Task 10) → matches `get_create_traveler_uc` provider in Task 20.
- `CreatePackage(writer)` (Task 12) → matches provider.
- `CancelAllOfTraveler(repo, policy, writer=None)` (Task 14) → matches `get_cancel_all_uc` provider (Task 20) passing only `repo + policy` since concrete repo implements both Writer+Reader.
- `CancelResult(cancelled, skipped)` (Task 14) → consumed in Task 22 route.
- `TravelerIn.to_input()` + `TravelerOut.from_domain()` (Task 19) → match `CreateTravelerInput` shape (Task 10) and `Traveler` entity (Task 3).
- `PackageIn.to_input()` maps `kind` to `refundable` (Task 19) → `CreatePackage` uses `refundable` bool (Task 12). Consistent.
- `PackageOut.from_domain()` emits BOTH `kind` and `refundable` (Task 19) — equivalence contracts use `kind` (Task 25 line `assert data["kind"] == "standard"`).

Everything checks out.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-22-plan-b-after-clean-arch.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, two-stage review (spec + quality), fast iteration. Same workflow that delivered Plan A.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints for review.

**Which approach?**
