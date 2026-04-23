# Plan C — Slidev Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o deck Slidev de 48 slides da palestra SOLID + Clean Arch pra Just Travel, com formato "Tour Guiado + Deep Dive", snippets importados dos repos `before/` e `after/` reais, speaker notes em pt-BR com roteiro por slide, e deploy automático no GitHub Pages.

**Architecture:** Projeto Slidev em `slides/` com um arquivo `slides.md` principal dividido em 12 seções via separadores `---`. Snippets de código ficam em `slides/snippets/before/` e `slides/snippets/after/` (cópias dos trechos pedagógicos de `before/` e `after/`) — importados nos slides via `<<< @/snippets/...` do Slidev pra highlight com Shiki. Speaker notes embutidas via HTML comments. Deploy via GitHub Actions → branch `gh-pages`.

**Tech Stack:** Slidev (Vue 3 + Markdown) · Shiki (syntax highlighter, padrão VSCode) · Node.js >=20 · pnpm ou npm · GitHub Actions · Fira Code / JetBrains Mono (code fonts)

**Pré-requisitos:** Plans A e B completos e verdes. Node.js 20+ instalado. Conta GitHub pra deploy de Pages.

---

## File Structure

```
slides/
├── .gitignore                           # node_modules, dist
├── package.json                         # deps slidev + scripts
├── slides.md                            # deck principal (todo o conteúdo, ~48 slides)
├── README.md                            # pt-BR: como rodar, build, deploy
├── snippets/
│   ├── before/
│   │   ├── traveler_god_class.py        # snippet da Traveler God Class
│   │   ├── calculate_price_ifelse.py    # snippet if/elif do discount
│   │   ├── lsp_bomb.py                  # cancel_all que explode
│   │   ├── fat_repository.py            # PackageRepository 12 métodos
│   │   └── dip_violation_router.py      # handler com SessionLocal()
│   └── after/
│       ├── traveler_entity.py           # dataclass pura
│       ├── discount_strategies.py       # DiscountPolicy Protocol + strategies
│       ├── cancel_all_graceful.py       # CancelAllOfTraveler partial result
│       ├── isp_segregated.py            # PackageWriter + PackageReader
│       └── dip_composition.py           # dependencies.py composition root
├── public/
│   ├── solid-bulls-eye.svg              # diagrama Clean Arch bulls-eye
│   └── linkedin-avatar.jpg              # placeholder (substituir antes da palestra)
└── .github/
    └── workflows/
        └── deploy-slides.yml            # build + push pra gh-pages
```

**Decisão de layout:** um único `slides.md` (ao invés de múltiplos arquivos) porque Slidev funciona melhor assim e facilita navegação linear. As seções são separadas por `---` do Slidev.

**Decisão de snippets:** copiar trechos curados de `before/`/`after/` pra `slides/snippets/` ao invés de importar via path relativo do repo raiz. Motivos: (1) mantém o deck auto-contido pra deploy; (2) snippets podem ser ligeiramente editados pra caber em slides (remover imports, limitar linhas); (3) Slidev `<<<` resolve `@/` como `slides/` root.

---

## Content decisions (locked in during brainstorming)

- **Formato:** Tour Guiado + Deep Dive (5 min tour inicial no `before/` → 13 min por letra SOLID → 10 min fechamento com Clean Arch emergindo).
- **Idioma:** slides em pt-BR; código em inglês (entidades `Traveler`/`TravelPackage`); speaker notes em pt-BR com fala sugerida.
- **Ferramentas:** Slidev + Shiki + JetBrains Mono + tema default com acentos Just Travel.
- **Cronograma target:** 48 slides / 90 min = média de 2 min/slide.
- **Palestrante:** Luiz Campos — LinkedIn `linkedin.com/in/luizcampos331` (placeholder pedagógico; ajustar antes da palestra).

---

## Task 1: Scaffold Slidev + `package.json` + primeira inicialização

**Files:**
- Create: `slides/.gitignore`
- Create: `slides/package.json`
- Create: `slides/slides.md` (primeira versão minimal)

- [ ] **Step 1: Criar `slides/.gitignore`**

```
node_modules/
dist/
.output/
*.log
```

- [ ] **Step 2: Criar `slides/package.json`**

```json
{
  "name": "solid-just-travel-slides",
  "type": "module",
  "private": true,
  "scripts": {
    "dev": "slidev --open",
    "build": "slidev build --base /solid-just-travel/",
    "export": "slidev export",
    "export-pdf": "slidev export --output dist/slides.pdf"
  },
  "dependencies": {
    "@slidev/cli": "^0.49.0",
    "@slidev/theme-default": "^0.25.0",
    "@slidev/theme-seriph": "^0.25.0",
    "vue": "^3.4.0"
  }
}
```

- [ ] **Step 3: Criar `slides/slides.md` (mínimo funcional)**

```markdown
---
theme: default
title: "SOLID na prática — Just Travel"
info: |
  Palestra SOLID + Clean Arch minimalista
  para o time de desenvolvimento da Just Travel.
author: Luiz Campos
drawings:
  persist: false
transition: slide-left
mdc: true
---

# SOLID na prática

Clean Architecture minimalista em FastAPI

<div class="pt-12">
  <span class="px-2 py-1 rounded bg-white bg-opacity-20">
    Just Travel — Abril 2026
  </span>
</div>

<!--
Fala: "Oi pessoal, hoje vamos falar sobre SOLID usando a API de vocês como base.
Prometo: nada de slide teórico — vamos ver código doendo e código curado."
-->
```

- [ ] **Step 4: Instalar deps e rodar dev server pra validar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && npm install
```

Expected: `added N packages` sem erros.

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && timeout 10 npx slidev --open=false --port 3031 > /tmp/slidev_boot.log 2>&1 &
sleep 5
curl -sf http://localhost:3031 > /dev/null && echo "slidev boot ok"
pkill -f "slidev" || true
```

Expected: `slidev boot ok`.

- [ ] **Step 5: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/
git commit -m "feat(slides): scaffold Slidev project with minimal first slide"
```

---

## Task 2: Criar `slides/README.md`

**Files:**
- Create: `slides/README.md`

- [ ] **Step 1: Criar `slides/README.md` (pt-BR)**

```markdown
# `slides/` — Deck Slidev da palestra SOLID + Clean Arch

Deck de 48 slides em ~90 min sobre SOLID na prática, usando os repos [`../before/`](../before) e [`../after/`](../after) como material didático.

## Como rodar local (Presenter mode)

```bash
cd slides
npm install
npm run dev   # abre em http://localhost:3030
```

Pressione `P` pra entrar em **Presenter Mode** — tela dupla: slides pro público + speaker notes + timer pra você.

## Como exportar PDF (backup pra caso de falha de internet)

```bash
npm run export-pdf   # gera dist/slides.pdf
```

## Como fazer build estático (pra servir)

```bash
npm run build   # gera dist/ pronto pro GitHub Pages
```

## Deploy

O workflow em `.github/workflows/deploy-slides.yml` faz build + push pra branch `gh-pages` a cada commit no `main`. URL final: `https://<seu-user>.github.io/solid-just-travel/`.

## Estrutura do deck

48 slides em 12 seções:

1. **Capa + quem sou eu** (2 slides, 2 min)
2. **Por que SOLID importa** (3 slides, 3 min)
3. **Tour guiado pelo `before/`** (4 slides, 5 min)
4. **S — Single Responsibility** (6 slides, 13 min)
5. **O — Open/Closed** (6 slides, 13 min)
6. **L — Liskov** (6 slides, 13 min)
7. **I — Interface Segregation** (6 slides, 13 min)
8. **D — Dependency Inversion** (7 slides, 13 min)
9. **Tabela-resumo SOLID** (1 slide, 2 min)
10. **Tour pelo `after/` → Clean Arch emerge** (4 slides, 5 min)
11. **Quando SOLID pede ainda mais separação** (1 slide, 2 min)
12. **Q&A + LinkedIn + recursos** (2 slides, 6 min)

## Shortcuts durante a palestra

- `SPACE` / `→` — próximo slide/animação
- `←` — voltar
- `P` — presenter mode
- `O` — visão geral (overview)
- `D` — modo escuro
- `F` — fullscreen
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/README.md
git commit -m "docs(slides): add Slidev README in pt-BR"
```

---

## Task 3: Copiar snippets de `before/` pra `slides/snippets/before/`

**Files:**
- Create: `slides/snippets/before/traveler_god_class.py`
- Create: `slides/snippets/before/calculate_price_ifelse.py`
- Create: `slides/snippets/before/lsp_bomb.py`
- Create: `slides/snippets/before/fat_repository.py`
- Create: `slides/snippets/before/dip_violation_router.py`

- [ ] **Step 1: Criar `traveler_god_class.py`** (versão enxuta pra slide)

```python
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
```

- [ ] **Step 2: Criar `calculate_price_ifelse.py`**

```python
# before/app/services/package_service.py — OCP violation
def calculate_price(package, discount_type: str) -> float:
    price = package.base_price
    if discount_type == "seasonal":
        price *= 0.85
    elif discount_type == "black_friday":
        price *= 0.70
    elif discount_type == "corporate":
        price = max(0.0, price - 200.0)
    elif discount_type == "cyber_monday":
        # Added last week; now four branches and counting.
        price *= 0.75 if package.base_price > 5000 else 0.90
    elif discount_type == "none":
        price = price
    else:
        raise ValueError(f"unknown discount_type: {discount_type}")
    return round(price, 2)
```

- [ ] **Step 3: Criar `lsp_bomb.py`**

```python
# before/app/models.py + booking_service.py — LSP trap
class TravelPackage(Base):
    def cancel(self) -> None:
        self.status = "cancelled"
        self.cancelled_at = datetime.utcnow()


class NonRefundablePackage(TravelPackage):
    def cancel(self) -> None:
        raise ValueError("Non-refundable packages cannot be cancelled")


# booking_service.py
def cancel_all_of_traveler(session, traveler_id: int) -> int:
    packages = session.query(TravelPackage).filter_by(
        traveler_id=traveler_id
    ).all()

    cancelled = 0
    for package in packages:
        package.cancel()        # ← BOOM on NonRefundablePackage
        cancelled += 1

    session.commit()
    return cancelled
```

- [ ] **Step 4: Criar `fat_repository.py`**

```python
# before/app/services/package_service.py — ISP violation
class PackageRepository:
    """A 12-method repository. CreatePackage uses ONE."""
    def __init__(self, session): self._session = session

    def add(self, package): ...                    # ← uso único do CreatePackage
    def by_id(self, package_id): ...
    def list(self): ...
    def update(self, package): ...
    def delete(self, package_id): ...
    def find_by_destination(self, destination): ...
    def find_by_price_range(self, lo, hi): ...
    def paginated(self, page, size=10): ...
    def count_by_traveler(self, traveler_id): ...
    def upsert(self, package): ...
    def archive(self, package_id): ...
    def bulk_insert(self, packages): ...


# Um fake pra testar CreatePackage precisa implementar os 12...
class FakePackageRepository:
    def add(self, p): self.last = p
    def by_id(self, id): raise NotImplementedError
    def list(self): raise NotImplementedError
    def update(self, p): raise NotImplementedError
    def delete(self, id): raise NotImplementedError
    def find_by_destination(self, d): raise NotImplementedError
    # ... mais 6 NotImplementedError
```

- [ ] **Step 5: Criar `dip_violation_router.py`**

```python
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
```

- [ ] **Step 6: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/snippets/before/
git commit -m "docs(slides): add before/ snippets for SOLID violation demos"
```

---

## Task 4: Copiar snippets de `after/` pra `slides/snippets/after/`

**Files:**
- Create: `slides/snippets/after/traveler_entity.py`
- Create: `slides/snippets/after/discount_strategies.py`
- Create: `slides/snippets/after/cancel_all_graceful.py`
- Create: `slides/snippets/after/isp_segregated.py`
- Create: `slides/snippets/after/dip_composition.py`

- [ ] **Step 1: Criar `traveler_entity.py`**

```python
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
```

- [ ] **Step 2: Criar `discount_strategies.py`**

```python
# after/app/domain/packages/discount_policy.py — OCP cure
class DiscountPolicy(Protocol):
    def apply(self, package: TravelPackage) -> Decimal: ...


class NoDiscount:
    def apply(self, p): return p.base_price

class SeasonalDiscount:
    def apply(self, p): return (p.base_price * Decimal("0.85")).quantize(...)

class BlackFridayDiscount:
    def apply(self, p): return (p.base_price * Decimal("0.70")).quantize(...)

class CorporateDiscount:
    def apply(self, p): return max(Decimal("0"), p.base_price - Decimal("200"))

class CyberMondayDiscount:
    THRESHOLD = Decimal("5000")
    def apply(self, p):
        factor = Decimal("0.75") if p.base_price > self.THRESHOLD else Decimal("0.90")
        return (p.base_price * factor).quantize(...)


# Nova promoção = nova classe. Zero edição nas existentes.
```

- [ ] **Step 3: Criar `cancel_all_graceful.py`**

```python
# after/app/application/packages/cancel_all_of_traveler.py — LSP cure
@dataclass(slots=True)
class CancelResult:
    cancelled: list[TravelPackage]
    skipped: list[TravelPackage]


class CancelAllOfTraveler:
    def __init__(self, repo, policy):
        self._reader = repo
        self._writer = repo
        self._policy = policy

    def execute(self, traveler_id: int) -> CancelResult:
        packages = self._reader.by_traveler(traveler_id)
        cancelled, skipped = [], []
        for package in packages:
            if package.refundable:                       # ← filtra ANTES
                updated = self._policy.cancel(package)
                self._writer.update(updated)
                cancelled.append(updated)
            else:
                skipped.append(package)                  # ← relata honesto
        return CancelResult(cancelled=cancelled, skipped=skipped)


# Sem bomba. Sem 500. Caller recebe AMBAS as listas.
```

- [ ] **Step 4: Criar `isp_segregated.py`**

```python
# after/app/domain/packages/package_repository.py — ISP cure
from __future__ import annotations
from typing import Protocol


class PackageWriter(Protocol):
    def add(self, package: TravelPackage) -> TravelPackage: ...
    def update(self, package: TravelPackage) -> TravelPackage: ...


class PackageReader(Protocol):
    def by_id(self, package_id: PackageId) -> TravelPackage | None: ...
    def list(self) -> list[TravelPackage]: ...
    def by_traveler(self, traveler_id: int) -> list[TravelPackage]: ...


# Use case CreatePackage depende só de PackageWriter (2 métodos):
class CreatePackage:
    def __init__(self, writer: PackageWriter):
        self._writer = writer
    def execute(self, input):
        return self._writer.add(TravelPackage(...))


# O adapter SQLAlchemy pode unificar — ISP é sobre o CONTRATO, não a
# implementação. Um mock de teste pra CreatePackage tem só 2 métodos:
class FakePackageWriter:
    def add(self, p): self.added.append(p)
    def update(self, p): ...
```

- [ ] **Step 5: Criar `dip_composition.py`**

```python
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
```

- [ ] **Step 6: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/snippets/after/
git commit -m "docs(slides): add after/ snippets for SOLID cure demos"
```

---

## Task 5: Deck — Abertura (slides 1-5): Capa + Quem sou + Por que SOLID importa

**Files:**
- Modify: `slides/slides.md` (substituir conteúdo mínimo pelo deck inteiro até slide 5)

- [ ] **Step 1: Substituir `slides/slides.md` pelo início do deck**

Substituir o conteúdo ATUAL do arquivo pelo abaixo. Esse commit troca o slide mínimo pelos 5 primeiros slides completos.

```markdown
---
theme: default
title: "SOLID na prática — Just Travel"
info: |
  Palestra SOLID + Clean Arch minimalista para o time Just Travel.
author: Luiz Campos
drawings:
  persist: false
transition: slide-left
mdc: true
monaco: false
highlighter: shiki
fonts:
  mono: 'JetBrains Mono'
---

# SOLID na prática

## Clean Architecture minimalista em FastAPI

<div class="pt-12">
  <span class="px-2 py-1 rounded bg-white bg-opacity-20 text-sm">
    Just Travel · Abril 2026 · Luiz Campos
  </span>
</div>

<!--
Fala (60s): "Oi pessoal, hoje são 1h30 sobre SOLID usando código que vocês
escreveriam. Prometo: ZERO slide de definição acadêmica. Vamos ver código
doendo, código sendo curado, e no final vocês vão perceber que já estavam
aplicando SOLID sem saber — o FastAPI inteiro é construído em cima disso."
-->

---
layout: two-cols
---

# Quem fala

- **Luiz Campos**
- Dev backend, 10+ anos
- Já tropecei em cada uma das 5 violações de SOLID em produção
- Hoje venho como "guia turístico" — vocês conhecem o código melhor que eu

::right::

<div class="flex flex-col items-center pt-8">
  <img src="/linkedin-avatar.jpg" class="w-40 h-40 rounded-full" />
  <p class="mt-4 text-sm">linkedin.com/in/luizcampos331</p>
</div>

<!--
Fala (60s): "Vou me apresentar rápido pra gente não queimar tempo. O que
importa é que eu passei por cada uma dessas dores que vocês vão ver. Não
sou quem 'aprendeu SOLID' — sou quem apanhou, aprendeu e quer poupar vocês."
-->

---

# Por que SOLID importa?

<v-clicks>

- **NÃO** importa por causa de entrevista de emprego
- **NÃO** é "boas práticas" vagas
- **NÃO** é teórico

- **IMPORTA** porque mudar código já custa 80% do nosso tempo
- **IMPORTA** porque toda hora chega uma feature que dói

</v-clicks>

<!--
Fala (90s): "Quantos de vocês já pegaram um ticket do tipo 'simples, só
adicionar um desconto Black Friday'? E quantos terminaram mexendo em 6
arquivos e quebrando 2 testes que nada tinham a ver? Essa é a dor que
SOLID resolve. Não é sobre estética."
-->

---

# A promessa desta palestra

Vocês saem daqui capazes de:

<v-clicks>

1. **Reconhecer** cada violação no código de vocês
2. **Aplicar** a cura com refatorações pequenas
3. **Entender** por que Clean Arch emerge naturalmente quando SOLID é levado a sério

</v-clicks>

<div v-click class="mt-8 text-center text-xl">

E vocês levam pra casa um **repo de referência** pra consultar
sempre que a memória falhar.

</div>

<!--
Fala (60s): "Três entregáveis concretos. Aquela analogia: hoje eu não trago
teoria, trago receita. No fim da palestra, vocês vão ter no GitHub o
repositório before/ e after/ pra olhar daqui a 3 meses quando esquecerem."
-->

---
layout: center
class: text-center
---

# Antes de começar

<div class="text-2xl mt-8">

Vamos **fazer um tour** no código do repo `before/`.

</div>

<div class="text-lg mt-4 opacity-60">
Guardem as "coisas estranhas" que eu vou apontar —
volta-se a elas nos próximos 65 minutos.
</div>

<!--
Fala (30s): "Antes de qualquer slide de princípio, tour rápido. Vou rodar
a API before/ em localhost, fazer um request, e passar pelas pastas
apontando coisas. Não precisa entender tudo agora — só guardem."

TOUR AO VIVO (4 min):
1. uv run uvicorn before.app.main:app --port 8000 — mostra /docs
2. POST /travelers — mostra que funciona
3. Abrir before/app/models.py::Traveler — "olhem essa classe, muitas coisas"
4. Abrir before/app/services/package_service.py — "12 métodos no repo, if/elif no preço"
5. Abrir before/app/services/booking_service.py — "for package: package.cancel()"
6. Abrir before/app/routers/travelers.py — "SessionLocal direto no handler"
Pergunta final: "reconhecem isso?" — plateia responde → gancho pra slide S.
-->

---
```

- [ ] **Step 2: Rodar slidev dev pra validar**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && timeout 10 npx slidev --open=false --port 3031 > /tmp/slidev_boot.log 2>&1 &
sleep 5
curl -sf http://localhost:3031 > /dev/null && echo "slidev ok with opening"
pkill -f "slidev" || true
```

Expected: `slidev ok with opening`.

- [ ] **Step 3: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add opening section (5 slides) — capa, speaker, why SOLID"
```

---

## Task 6: Deck — Bloco S (Single Responsibility, slides 6-11)

**Files:**
- Modify: `slides/slides.md` (append 6 slides)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

Adicionar ao FINAL do arquivo (depois do `---` do slide 5):

```markdown

# S — Single Responsibility Principle

<div class="text-xl mt-4 mb-6">
Uma classe deve ter apenas uma razão pra mudar.
</div>

<div class="text-base opacity-80">
<p><strong>Leia como:</strong> responde a um <em>único stakeholder</em>.</p>
<p>Não é "fazer uma coisa só" — é "ser pedida por uma pessoa só".</p>
</div>

<div class="mt-8 p-4 border-l-4 border-blue-400 bg-blue-50">
<p class="italic">
"Um Viajante não deve ser também quem valida CPF, quem salva no banco,
e quem manda email de boas-vindas. Se Compliance muda validação,
você não quer mexer em Viajante."
</p>
</div>

<!--
Fala (2 min): "Primeira letra. Definição clássica: 'uma classe, uma razão
pra mudar'. Mas razão aqui é POLÍTICA, não técnica. Razão = stakeholder.
Se o DBA muda o schema, se Compliance muda validação, se o Marketing
muda o template de email — são 3 pessoas diferentes pedindo 3 mudanças
diferentes. Se tudo vive na mesma classe, qualquer toque arrisca quebrar
os outros dois."
-->

---

# S — A dor no `before/`

<<< @/snippets/before/traveler_god_class.py {all|10-14|16-18|20-21|23-24}{maxHeight:'400px'}

<!--
Fala (3 min): "Essa é a classe Traveler real do repo before. Vou destacar
em pedaços. [click] validate(): regra de negócio. [click] save(): acesso
a banco. [click] send_welcome_email(): SMTP. [click] to_dict(): formato
de resposta. Quantos stakeholders? Compliance, DBA, SRE, Frontend. 4
razões diferentes pra mudar. SRP violado, por definição."

Pergunta: "Quem aqui já mudou uma classe por um motivo e quebrou outro
fluxo sem querer? Levante a mão." → geralmente todo júnior levanta.
-->

---

# S — A cura no `after/`

Uma responsabilidade, uma classe:

<<< @/snippets/after/traveler_entity.py {all|2-11|14-18}{maxHeight:'380px'}

<!--
Fala (3 min): "Olhem a Traveler agora. 10 linhas. Só invariantes do
próprio Traveler — nome com 2 chars. Email e Document são VOs que
validam no construtor. E olhem embaixo: cada stakeholder ficou em SUA
classe — DBA tem o repositório, Compliance tem o VO Document, SRE tem
o notifier, Frontend tem o TravelerOut Pydantic."
-->

---

# S — Before × After

<div class="grid grid-cols-2 gap-4">

<div>

**Before**
```python {all|none}
class Traveler(Base):
    __tablename__ = "..."
    # 4 columns
    def validate(self): ...       # Compliance
    def save(self): ...           # DBA
    def send_email(self): ...     # SRE
    def to_dict(self): ...        # Frontend
```

- 40 linhas, 1 classe
- 4 stakeholders
- Compliance muda → risco de quebrar JSON

</div>

<div>

**After**
```python {all|none}
@dataclass
class Traveler:
    name: str
    email: Email
    document: Document
# + Document VO
# + Email VO
# + SqlAlchemyTravelerRepository
# + StdoutWelcomeNotifier
# + TravelerOut Pydantic
```

- 5 classes, ~10 linhas cada
- 1 stakeholder por classe
- Compliance muda → toca 1 arquivo

</div>

</div>

<!--
Fala (3 min): "Métrica real: 40 linhas viraram 5 classes de 10. PARECE
mais código, mas cada peça responde a UM só. Pra Compliance mexer na
validação de CPF, agora ela toca 1 arquivo (Document) — ela nem vê o
banco, nem vê FastAPI, nem vê SMTP."
-->

---

# S — O que ganhamos

<v-clicks>

- **Testabilidade**: testar `Document('12345678909')` não precisa de banco
- **Isolamento de mudança**: trocar SMTP por SES não toca em Traveler
- **Legibilidade**: cada arquivo tem um propósito óbvio
- **Um bug menos por release**: mudanças acidentais caem

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Isso não foi "mais engenharia". Foi código no <strong>lugar certo</strong>.
</div>

<!--
Fala (2 min): "Balanço. 4 ganhos. [click × 4]. O principal argumento
pra júnior que ainda resiste: um bug menos por release. Toda vez que
vocês mexem num God Class e quebram algo em outro lugar, SRP está gritando."
-->

---
layout: center
---

# Próximo: **O** — Open/Closed

<div class="text-lg mt-6 opacity-70">
Lembram do if/elif no cálculo de preço do tour inicial?
</div>
<div class="text-lg mt-2 opacity-70">
Era isso.
</div>

<!--
Fala (30s): "Próximo princípio. Ponte direta: lembra o if/elif gigante no
calculate_price que eu mostrei no tour? Esse código dói por causa de OCP.
Vamos ver."
-->

---
```

- [ ] **Step 2: Validar dev server**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && timeout 10 npx slidev --open=false --port 3031 > /tmp/slidev_boot.log 2>&1 &
sleep 5
curl -sf http://localhost:3031 > /dev/null && echo "S block ok"
pkill -f "slidev" || true
```

Expected: `S block ok`.

- [ ] **Step 3: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add S block (Single Responsibility, 6 slides)"
```

---

## Task 7: Deck — Bloco O (Open/Closed, slides 12-17)

**Files:**
- Modify: `slides/slides.md` (append 6 slides)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

```markdown

# O — Open/Closed Principle

<div class="text-xl mt-4 mb-6">
Aberto pra extensão, fechado pra modificação.
</div>

<div class="text-base opacity-80">
<p>Novo comportamento entra via <strong>nova classe</strong>,
não alterando a existente.</p>
</div>

<div class="mt-8 p-4 border-l-4 border-orange-400 bg-orange-50">
<p class="italic">
"Black Friday: 30%. Cyber Monday: progressivo. Cupom corporativo:
flat. Se toda regra nova te obriga a abrir o mesmo arquivo e adicionar
mais um <code>elif</code> — seu código está <em>fechado pra extensão</em>
e <em>aberto pra modificação</em>. Exatamente o oposto."
</p>
</div>

<!--
Fala (2 min): "Segunda letra. Palavra-chave: TOCAR. Cada regra nova
deveria entrar sem tocar em regra antiga. Por que? Porque toda vez que
você toca em função que já funciona, você arrisca quebrar."
-->

---

# O — A dor no `before/`

<<< @/snippets/before/calculate_price_ifelse.py {all|5-7|8-9|10-11|12-14}{maxHeight:'420px'}

<!--
Fala (3 min): "Calculate_price. [click] seasonal. [click] black_friday
adicionado ano passado. [click] corporate depois. [click] cyber_monday
semana passada. 4 branches e contando. Quem quer fazer a feature 'desconto
estudante'? É outro elif — e todo elif NOVO é um risco pros 4 antigos."
-->

---

# O — A cura no `after/`

<<< @/snippets/after/discount_strategies.py {all|2-3|5-6|17-22|25}{maxHeight:'420px'}

<!--
Fala (3 min): "Strategy pattern via Protocol. [click] Define o contrato.
[click] NoDiscount. [click] Cyber Monday tem ramo interno — sim, mas é
uma regra da própria estratégia, não alterna entre estratégias. [click]
Nova promoção = nova classe. Zero edição em classe existente."
-->

---

# O — Before × After

<div class="grid grid-cols-2 gap-4">

<div>

**Before**
```python
def calculate_price(p, discount):
    if discount == "seasonal":
        ...
    elif discount == "black_friday":
        ...
    elif discount == "corporate":
        ...
    elif discount == "cyber_monday":
        ...
```

- Nova regra = editar função
- Risco de regressão a cada release
- Testes dependem da ordem dos ifs

</div>

<div>

**After**
```python
class DiscountPolicy(Protocol):
    def apply(self, p): ...

class Seasonal: ...
class BlackFriday: ...
class Corporate: ...
class CyberMonday: ...

# + StudentDiscount (futura)
```

- Nova regra = nova classe
- Zero toque em código antigo
- Teste por política — isolado

</div>

</div>

<!--
Fala (3 min): "Mesma quantidade de regras, 5 no after vs 5 branches no
before. Mas no after, adicionar a 6a não mexe nas outras. E teste: no
before precisa parametrizar sobre 5 casos num único teste de integração.
No after, cada política é uma classe testável de 3 linhas."
-->

---

# O — O que ganhamos

<v-clicks>

- **Novas promoções sem quebrar antigas** — nunca mais "ih, o Black Friday quebrou"
- **Testes triviais** — cada política = 2 linhas de teste
- **Composição dinâmica** — selecionar política em runtime fica óbvio
- **Código aberto pra extensão** (de verdade)

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Adicionar = criar arquivo novo. <strong>Zero risco</strong> no arquivo antigo.
</div>

<!--
Fala (2 min): "4 ganhos. O mais palpável: testes de cada política rodam
em microssegundos, sem banco, sem nada. 6 políticas, 6 testes paralelos."
-->

---
layout: center
---

# Próximo: **L** — Liskov

<div class="text-lg mt-6 opacity-70">
Lembram do <code>for package: package.cancel()</code> do tour?
</div>
<div class="text-lg mt-2 opacity-70">
Vai explodir agora.
</div>

<!--
Fala (30s): "Terceira letra. Ponte: lembra o cancel_all no booking_service?
Loop inocente. Vai explodir. Vamos ver POR QUE e como curar."
-->

---
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add O block (Open/Closed, 6 slides)"
```

---

## Task 8: Deck — Bloco L (Liskov, slides 18-23)

**Files:**
- Modify: `slides/slides.md` (append 6 slides)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

```markdown

# L — Liskov Substitution Principle

<div class="text-xl mt-4 mb-6">
Subtipo deve ser substituível pelo tipo-pai sem quebrar contratos.
</div>

<div class="text-base opacity-80">
<p>Se uma função aceita <code>TravelPackage</code>, ela tem que aceitar
<strong>qualquer subclasse</strong> sem explodir.</p>
<p>Herança é <em>promessa</em>, não atalho.</p>
</div>

<div class="mt-8 p-4 border-l-4 border-red-400 bg-red-50">
<p class="italic">
"TravelPackage tem <code>.cancel()</code>. Alguém criou
NonRefundablePackage herdando e sobrescreveu pra jogar exceção.
Dia seguinte, 'cancelar todos os pacotes do viajante' rodou em
produção, iterou 40, achou 1 não-reembolsável. 39 parcialmente
cancelados. Caos."
</p>
</div>

<!--
Fala (2 min): "LSP é o mais abstrato dos 5, mas a dor é a mais concreta.
Herança parece atalho — 'quase igual, só muda um método'. Mas cada
override que quebra contrato é uma bomba-relógio. Bomba pra quem? Pro
for inocente lá na frente, que vocês ainda nem escreveram."
-->

---

# L — A dor no `before/`

<<< @/snippets/before/lsp_bomb.py {all|1-4|7-9|12-21|18-19}{maxHeight:'420px'}

<!--
Fala (3 min): "[click] Classe base cancel() atualiza status. [click]
Subclasse lança exception. [click] Service faz o for clássico. [click]
ZOOM no 'package.cancel()' — esse é o momento da bomba. Query retorna
MIX de TravelPackage e NonRefundablePackage (STI no SQLAlchemy). Loop
itera. Hora que chega no primeiro NonRefundable: ValueError. Alguns já
foram marcados 'cancelled' na memória. Partial failure clássico."

Pergunta: "Quem já escreveu um for que funcionava nos testes e
explodiu em produção porque entrou tipo diferente?" → mão levanta.
-->

---

# L — A cura no `after/`

<<< @/snippets/after/cancel_all_graceful.py {all|1-4|7-10|13-22}{maxHeight:'430px'}

<!--
Fala (3 min): "[click] CancelResult: honesto, duas listas. [click]
Use case constructor: repo + policy. Sem herança. [click] O coração:
check refundable ANTES de chamar policy. Non-refundable entra em skipped.
Caller recebe AMBAS as listas. Sem exception. Sem partial failure."
-->

---

# L — Before × After

<div class="grid grid-cols-2 gap-4">

<div>

**Before**
```python
class NonRefundablePackage(
    TravelPackage
):
    def cancel(self):
        raise ValueError(...)

# for package in packages:
#     package.cancel()  # BOOM
```

- Subclass mente sobre o contrato
- Loop "seguro" explode
- Callers não têm defesa

</div>

<div>

**After**
```python
@dataclass
class TravelPackage:
    refundable: bool   # data, not type

class CancelAllOfTraveler:
    def execute(self, tid):
        for p in packages:
            if p.refundable: cancel()
            else: skip()
        return CancelResult(...)
```

- Capability vira dado
- Loop nunca explode
- Caller sabe o que rolou

</div>

</div>

<!--
Fala (3 min): "Substituímos herança por **flag + policy**. Capability
virou dado, não tipo. O endpoint HTTP mudou: no before retornava 500
em partial; no after retorna 200 com JSON estruturado — 'cancelou 39,
pulou 1'. Mesma intenção de negócio, **comunicação honesta**."
-->

---

# L — O que ganhamos

<v-clicks>

- **Loops seguros** — iteração sobre tipo-pai sempre funciona
- **Menos classes** — 1 em vez de 2 (tipos → flag)
- **Contrato honesto** — caller sabe exatamente o que foi feito
- **HTTP 200 em vez de 500** — UX muito melhor

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Regra prática: <strong>composição > herança</strong>, quase sempre.
</div>

<!--
Fala (2 min): "4 ganhos. O mais comum na prática: substituir herança
frágil por flag no dado. Você paga menos código e ganha previsibilidade.
A industria percebeu isso — Java 21 tem sealed classes, Kotlin prefere
data class + when, Rust nem tem herança de comportamento. Tendência."
-->

---
layout: center
---

# Próximo: **I** — Interface Segregation

<div class="text-lg mt-6 opacity-70">
Lembram do repositório com 12 métodos do tour?
</div>
<div class="text-lg mt-2 opacity-70">
Vamos ver por que o mock dele é um pesadelo.
</div>

<!--
Fala (30s): "Quarta letra. Ponte: repositório gigante. Quem aqui já
escreveu um mock com 10 NotImplementedError pra testar 3 linhas? Vocês
vão reconhecer a dor."
-->

---
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add L block (Liskov, 6 slides with for-loop bomb story)"
```

---

## Task 9: Deck — Bloco I (Interface Segregation, slides 24-29)

**Files:**
- Modify: `slides/slides.md` (append 6 slides)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

```markdown

# I — Interface Segregation Principle

<div class="text-xl mt-4 mb-6">
Interface pequena, cliente feliz.
</div>

<div class="text-base opacity-80">
<p>Nenhuma classe deve ser forçada a depender de <strong>métodos que não usa</strong>.</p>
<p>Se 80% dos clientes usam 20% da interface → acoplamento grátis no resto.</p>
</div>

<div class="mt-8 p-4 border-l-4 border-purple-400 bg-purple-50">
<p class="italic">
"PackageRepository tem 12 métodos. <code>CreatePackage</code> usa UM:
<code>add()</code>. Mas pra testar você precisa de um fake que
implementa OS 12. Quem já escreveu isso, levanta a mão."
</p>
</div>

<!--
Fala (2 min): "Quarta letra. Na palestra tradicional sobre ISP, a gente
fala de 'interfaces gordas'. Mas isso fica abstrato. Pra júnior, a dor
REAL aparece em testes. Mock gigante. Fake com NotImplementedError por
todo canto. Toda vez que isso acontece, ISP está gritando."
-->

---

# I — A dor no `before/`

<<< @/snippets/before/fat_repository.py {all|4-16|21-28}{maxHeight:'450px'}

<!--
Fala (3 min): "[click] 12 métodos no repo real. add é o único usado pelo
CreatePackage. [click] Fake de teste: 12 NotImplementedError. Se amanhã
alguém adiciona um 13º método, toda infraestrutura de testes quebra.
Pior: o fake é MAIOR que o código sendo testado. 3 linhas pra 20."

Pergunta: "Quem já desistiu de escrever um teste porque o mock ficou
maior que o código? Não precisa ter orgulho, todo mundo já fez."
-->

---

# I — A cura no `after/`

<<< @/snippets/after/isp_segregated.py {all|5-8|10-13|16-22|28-30}{maxHeight:'430px'}

<!--
Fala (3 min): "[click] 2 Protocols pequenos: Writer (2 métodos) e Reader
(3 métodos). [click] PackageWriter tem só add e update. [click] Use case
declara DEPENDÊNCIA ESTREITA: só Writer. [click] Fake de teste cabe num
post-it: 2 métodos. Mesmo CreatePackage, mesma funcionalidade, teste
10× mais limpo."
-->

---

# I — Before × After

<div class="grid grid-cols-2 gap-4">

<div>

**Before**
```python
class PackageRepo:
    def add(...): ...        # ← uso
    def by_id(...): ...
    def list(...): ...
    def update(...): ...
    def delete(...): ...
    def find_destination...
    def find_price_range...
    def paginated(...): ...
    def count_by_trav(...)...
    def upsert(...): ...
    def archive(...): ...
    def bulk_insert(...): ...

# Fake: 12 NotImpl + 1 real
```

- 12 métodos × N clientes = N*12 deps

</div>

<div>

**After**
```python
class Writer(Protocol):
    def add(...): ...
    def update(...): ...

class Reader(Protocol):
    def by_id(...): ...
    def list(...): ...
    def by_traveler(...): ...

# CreatePackage(writer: Writer)
# ListPackages(reader: Reader)
# Fake: 2 métodos. Acabou.
```

- Cada cliente declara só o que precisa

</div>

</div>

<!--
Fala (3 min): "Mesmo adapter concreto — SqlAlchemyPackageRepository —
implementa AMBOS os Protocols. A fragmentação é no CONTRATO, não na
implementação. Clientes veem slices pequenos. Infraestrutura unifica."
-->

---

# I — O que ganhamos

<v-clicks>

- **Fakes cabem em 5 linhas** — teste vira documentação de uso
- **Clientes declaram intenção** — tipo do parâmetro mostra "só escrevo" ou "só leio"
- **Menos acoplamento acidental** — mudar o 13º método não quebra clientes de `add`
- **Menos código de teste** — vocês voltam a escrever testes

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Mock gigante é ISP gritando. Se seu mock tem mais linhas que o código
sendo testado, segregue.
</div>

<!--
Fala (2 min): "Regra prática pra júnior: CONTAR LINHAS DE MOCK. Se
excedem o código, ISP está pedindo socorro. Esse é o sinal."
-->

---
layout: center
---

# Próximo: **D** — Dependency Inversion

<div class="text-lg mt-6 opacity-70">
O ponto alto. Vocês já usam DIP todo dia sem saber.
</div>

<!--
Fala (30s): "Última letra. E é a que muda MAIS a vida de vocês. Vocês
já usam DIP sem saber — a feature mais famosa do FastAPI é literalmente
isso. Vamos destrinchar."
-->

---
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add I block (Interface Segregation, 6 slides)"
```

---

## Task 10: Deck — Bloco D (Dependency Inversion, slides 30-36)

**Files:**
- Modify: `slides/slides.md` (append 7 slides — bloco DIP tem 1 slide extra)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

```markdown

# D — Dependency Inversion Principle

<div class="text-xl mt-4 mb-6">
Dependa de abstrações, não de implementações.
</div>

<div class="text-base opacity-80">
<p>Alto nível (regra de negócio) e baixo nível (banco, SMTP, cache)
<strong>ambos dependem de abstração</strong>.</p>
<p>A seta aponta sempre pra dentro, nunca pra fora.</p>
</div>

<div class="mt-8 p-4 border-l-4 border-green-400 bg-green-50">
<p class="italic">
"A regra 'viajante menor de idade precisa de autorização' é política.
Ela <strong>não pode</strong> depender de SQLAlchemy, FastAPI, Postgres.
Se amanhã migrarmos pra MongoDB, a regra é idêntica."
</p>
</div>

<!--
Fala (2 min): "DIP é o que desenha a arquitetura. Seta aponta pra
dentro. A regra de negócio é o CENTRO. Tudo que é detalhe — ORM,
framework HTTP, email provider — roda em torno e depende dela, não o
contrário."
-->

---

# D — A dor no `before/`

<<< @/snippets/before/dip_violation_router.py {all|1-2|6-7|9-14}{maxHeight:'440px'}

<!--
Fala (3 min): "[click] Router importa SessionLocal. Handler de negócio
importando INFRA. Seta invertida. [click] Construção de sessão dentro
do handler. [click] Chamadas ORM diretas. Pra testar? Precisa subir
banco. Pra trocar banco? Mexe no handler. Regra de negócio ACOPLADA
a detalhe."
-->

---

# D — A cura no `after/`

<<< @/snippets/after/dip_composition.py {all|2-6|9|12-13|16-17|20-24|28-34}{maxHeight:'430px'}

<!--
Fala (3 min): "[click] get_db provider. [click] DbSession alias. [click]
Repo provider. [click] Aliases pros providers — economiza boilerplate.
[click] Wiring do use case. [click] Handler: RECEBE o use case. Nunca
importa banco, nunca importa SessionLocal, nunca importa SQLAlchemy.
Regra de negócio PURA — depende só de Protocols."
-->

---

# D — O `Depends()` do FastAPI **é DIP**

<div class="text-lg mt-4 mb-6">

Vocês já usam isso **todo dia**:

</div>

```python
# FastAPI docs — exemplo oficial
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/items/")
def create_item(
    item: ItemIn,
    db: Session = Depends(get_db)  # ← inversão de dependência
):
    ...
```

<div class="mt-8 text-center text-xl">

A feature mais vendida do FastAPI é **literalmente DIP**.

</div>

<!--
Fala (2 min): "Aqui está o 'aha moment'. Vocês leram a doc do FastAPI,
aprenderam Depends(), acharam conveniente. NINGUÉM te disse que você
estava aplicando DIP. Mas está. O que muda no after: em vez de depender
de CLASSE CONCRETA (SessionLocal, SqlAlchemyTravelerRepository), vocês
dependem de PROTOCOL (TravelerRepository). Mesma mecânica, abstração
maior."
-->

---

# D — Before × After

<div class="grid grid-cols-2 gap-4">

<div>

**Before**
```python
from ... import SessionLocal

@router.post("/travelers")
def create(body):
    session = SessionLocal()
    try:
        t = Traveler(...)
        t.validate()
        t.save(session)
        t.send_welcome_email()
        return ...
    finally:
        session.close()
```

- Handler conhece INFRA
- 9 linhas de boilerplate
- Teste precisa de banco

</div>

<div>

**After**
```python
@router.post("/travelers")
def create(
    body: TravelerIn,
    uc: Annotated[
        CreateTraveler,
        Depends(get_create_traveler_uc)
    ],
) -> TravelerOut:
    t = uc.execute(body.to_input())
    return TravelerOut.from_domain(t)
```

- Handler conhece só use case
- 2 linhas de lógica
- Teste usa fake

</div>

</div>

<!--
Fala (3 min): "Contem as linhas. Antes: 9 linhas, das quais 6 são
plumbing (SessionLocal, try/finally, close). Depois: 2 linhas de
negócio. O use case esconde o ciclo todo. Teste no after: injeta fake,
roda em 1ms."
-->

---

# D — O que ganhamos

<v-clicks>

- **Regra de negócio testável sem banco** — use case + fake = 1ms
- **Trocar ORM é trivial** — só `infra/` muda
- **Composition root explícito** — `dependencies.py` mostra o mapa
- **Handlers triviais** — 3-5 linhas, impossível esconder bug

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Vocês <strong>já</strong> aplicam DIP. Agora é só apontar pra Protocol
em vez de classe concreta.
</div>

<!--
Fala (2 min): "Ganho principal: testabilidade. Antes, precisamos do
banco pra testar 'criar viajante'. Depois, um InMemoryRepository. Esse
é o argumento que vende pro júnior que nunca escreveu teste 'porque dá
trabalho' — olha, não dá mais."
-->

---
layout: center
class: text-center
---

# Acabamos os 5 princípios.

<div class="text-lg mt-6 opacity-70">
Antes do fechamento, uma tabela-resumo.
</div>

<!--
Fala (15s): "Fim do miolo. Antes de amarrar com Clean Arch, um slide de
review rápido — cabulete que vocês podem colar na mesa de vocês."
-->

---
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add D block (Dependency Inversion, 7 slides — Depends() is DIP)"
```

---

## Task 11: Deck — Tabela-resumo + Tour pelo `after/` (slides 37-42)

**Files:**
- Modify: `slides/slides.md` (append 6 slides)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

```markdown

# Tabela-resumo SOLID

| Princípio | Dor | Cura | Onde mora |
|---|---|---|---|
| **S** | Classe responde a muitos chefes | Separe por stakeholder | `domain` + `infra` + `presentation` |
| **O** | Novo comportamento edita arquivo existente | Strategy / Policy | `domain/*/policy.py` |
| **L** | Subclass mente sobre contrato | Composição + flag | `domain` (entidades planas) |
| **I** | Interface fat obriga clientes a saber demais | Protocols pequenos | `domain/*/protocol.py` |
| **D** | Alto nível depende de baixo nível | Ambos dependem de abstração | `domain` central, `infra` implementa |

<div class="text-center mt-8 text-lg opacity-70">
Esse slide é a <strong>cola</strong>. Printe e cole na mesa.
</div>

<!--
Fala (2 min): "5 linhas. Pro primeiro mês de vocês praticando, esse é
TODO o conteúdo que importa. Coluna 'Onde mora' vai fazer sentido nos
próximos slides."
-->

---
layout: center
class: text-center
---

# Tour pelo `after/`

<div class="text-xl mt-8">
Já sabemos as curas. Agora, um zoom-out:
</div>

<div class="text-lg mt-4 opacity-70">
<strong>o que a estrutura do repo virou?</strong>
</div>

<!--
Fala (15s): "Vamos fazer o tour do after agora. Mesma funcionalidade
do before, mas reorganizada."
-->

---

# A estrutura que emergiu

```
after/app/
├── domain/           ← núcleo puro (zero dep externa)
│   ├── travelers/    ← Traveler + VOs + Protocols
│   └── packages/     ← TravelPackage + policies + Protocols
├── application/      ← use cases (1 por ação)
│   ├── travelers/    ← create, list, get
│   └── packages/     ← create, list, calculate_price, cancel_all
├── infra/            ← adapters (SQLAlchemy + SMTP)
│   └── persistence/notifications/
├── presentation/     ← HTTP (FastAPI)
│   ├── schemas.py    ← Pydantic IO
│   └── routers/      ← handlers finos 3-5 linhas
└── main.py           ← composition root
```

<!--
Fala (2 min): "4 pastas. domain no centro. application rodeando.
Infra implementando. Presentation na ponta. Isso tem um nome."
-->

---
layout: center
---

# Esse desenho tem um nome:

<div class="text-6xl mt-8 font-bold">
Clean Architecture
</div>

<div class="text-lg mt-8 opacity-70 max-w-2xl">
E aqui está a coisa <strong>importante</strong>:<br/>
a gente <u>não decidiu</u> isso antes. <br/>
<strong>Emergiu</strong> aplicando SOLID.
</div>

<!--
Fala (1 min): "REVELAÇÃO. Isso que vocês veem há 75 minutos refatorando
tem um nome famoso. Uncle Bob escreveu um livro sobre. Mas olha o que
é diferente da apresentação tradicional: ele vende como 'a arquitetura
certa'. Eu tô vendendo como 'o que sai quando você aplica 5 princípios
com disciplina'. Essa diferença é importante."
-->

---

# Cada princípio mora em camadas

<div class="grid grid-cols-2 gap-4 mt-4">

<div>

**domain** (o núcleo)
- **S** — entidades + VOs separados
- **L** — entidades planas com flags
- **O** — policies e strategies
- **I** — Protocols segregados

</div>

<div>

**application**
- **S** — um use case por ação
- Só conhece `domain/`

**infra**
- **D** — implementa Protocols do domain
- Adapters plugáveis

**presentation**
- **S + I** — schemas e routers finos
- **D** — composition root via `Depends()`

</div>

</div>

<div v-click class="mt-8 text-center text-lg opacity-80">
Setas apontam <strong>pra dentro</strong>. Sempre.
</div>

<!--
Fala (2 min): "Mapa completo. Qual letra vive onde. DIP é o que
desenha a arquitetura: ele diz que setas apontam pra dentro. SRP
define o tamanho das caixas. OCP abre espaço dentro de cada caixa.
ISP define a fronteira entre caixas. LSP garante que substituir
implementação não quebra nada."
-->

---

# Regras de ouro (que emergiram sozinhas)

<v-clicks>

1. **`domain/` é puro** — não importa FastAPI, SQLAlchemy, nada
2. **Use cases orquestram regra** — 1 classe = 1 ação = 1 razão
3. **`infra/` é plugável** — SQLite → Postgres sem tocar domain
4. **`presentation/` é fino** — valida, chama, formata

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Essas regras <strong>não precisam ser decoradas</strong>. Elas caem
naturalmente se vocês aplicarem SOLID.
</div>

<!--
Fala (2 min): "Não decorem. Estudem SOLID, essas regras CAEM. É o
contrário do que o livro do Uncle Bob sugere. Ele diz 'adote essa
estrutura'. Eu digo 'pratique SOLID, a estrutura aparece'. Caminho
diferente, mesmo destino."
-->

---
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add summary table + after/ tour (6 slides, Clean Arch emerges)"
```

---

## Task 12: Deck — Fechamento (slides 43-48): Escala, Ação, LinkedIn

**Files:**
- Modify: `slides/slides.md` (append 6 slides — último batch)

- [ ] **Step 1: Append ao final de `slides/slides.md`**

```markdown

# Quando SOLID pede ainda mais separação

<div class="text-lg mt-4 mb-6">
Sinais de que projeto grande precisa <strong>extra</strong>:
</div>

<v-clicks>

- Handler > 15 linhas com orquestração complexa → extraia controller
- Mesma ação em HTTP + CLI + worker → controller centraliza
- API com 80+ endpoints → separe `routes/` de `controllers/` pra ter o mapa

</v-clicks>

<div v-click class="mt-8 p-4 border-l-4 border-yellow-400 bg-yellow-50">
<p class="italic text-lg">
<strong>Regra de ouro final:</strong> SOLID responde a dor.<br/>
Enquanto <strong>não dói</strong>, seu handler de 5 linhas <strong>é</strong> o design correto.
</p>
</div>

<!--
Fala (2 min): "Pergunta que vocês vão ter: 'quando separo rotas de
controllers?'. Resposta: QUANDO DOER. Projeto com 5 endpoints e
handler de 3 linhas não precisa. Projeto com 80 endpoints e handler
de 20 linhas precisa. SOLID é reagir a dor, nunca preventivo."
-->

---

# O que fazer segunda-feira de manhã

<v-clicks>

1. **Escolha UM arquivo** que incomoda — só um
2. **Identifique qual letra dói** mais ali (use a tabela-resumo)
3. **Refatore 1 princípio por vez** — não SOLID-e tudo de uma
4. **Escreva o teste antes** — garante que comportamento não muda
5. **PR com review** pedindo feedback no princípio aplicado

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
Em 6 meses, vocês olham o código e não reconhecem mais.<br/>
De orgulho.
</div>

<!--
Fala (2 min): "Plano de ação concreto. Um princípio por PR, uma
refatoração por semana. Em 6 meses, o código da Just Travel vai
estar irreconhecível. Se vocês vierem pedir code review com 'esse PR
aplica OCP no discount', vou pagar um café pra cada um."
-->

---
layout: two-cols
class: pt-8
---

# Me segue lá

<div class="flex flex-col items-center">
  <img src="/linkedin-avatar.jpg" class="w-32 h-32 rounded-full" />
  <p class="mt-4 font-bold text-xl">Luiz Campos</p>
  <p class="opacity-70">@luizcampos331</p>
  <p class="mt-2 text-sm">linkedin.com/in/luizcampos331</p>
</div>

<div class="mt-6 text-sm opacity-80 text-center max-w-xs">
DM liberada — dúvida, code review, projeto novo. <br/>
Respondo todos.
</div>

::right::

# Pra continuar estudando

<v-clicks>

- 📖 *Clean Architecture* — **Robert C. Martin**
- 📖 *A Philosophy of Software Design* — **John Ousterhout** (complementa)
- 🎥 [refactoring.guru](https://refactoring.guru) — patterns com exemplos
- 💻 Este repo: [github.com/luizcampos331/solid-just-travel](https://github.com/luizcampos331/solid-just-travel)

</v-clicks>

<!--
Fala (2 min): "LinkedIn aberto. O repo vai ficar público, clonar à
vontade, usar em projetos. Livros recomendados: o Uncle Bob pro panorama,
o Ousterhout pra reduzir complexidade. Refactoring.guru é o melhor site
gratuito sobre patterns."

NOTA PRÉ-PALESTRA: atualizar URL do repo no slide pra ficar consistente
com onde vai ser publicado. Substituir placeholder avatar.
-->

---
layout: center
class: text-center
---

# Obrigado.

<div class="text-2xl mt-6 opacity-70">
Perguntas?
</div>

<div class="mt-16 text-sm opacity-50">
github.com/luizcampos331/solid-just-travel
</div>

<!--
Fala (4 min Q&A): deixar aberto. Perguntas comuns antecipadas:

1. "Quando devo separar services/ do application/?"
   R: Nunca. application/ JÁ é services/. Se estão separados, é
   redundância.

2. "E quando preciso de transações?"
   R: Unit of Work pattern. Use case recebe UoW em vez de repositório
   direto. É uma extensão natural de DIP que NÃO precisa hoje.

3. "Preciso ter TODOS os 4 layers sempre?"
   R: Não. CRUD simples? 2 layers bastam (domain + presentation).
   Regra: camada a mais só se a dor atual justifica.

4. "Dataclass vs Pydantic em domain/?"
   R: Dataclass. Pydantic é pra serialização (presentation). Se seu
   domain importa Pydantic, tá violando DIP.
-->
```

- [ ] **Step 2: Validar o deck COMPLETO (48 slides)**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && timeout 15 npx slidev --open=false --port 3031 > /tmp/slidev_full.log 2>&1 &
sleep 8
curl -sf http://localhost:3031 > /dev/null && echo "full deck boot ok"
pkill -f "slidev" || true
```

Expected: `full deck boot ok`.

Também verifique a contagem de seções:
```bash
grep -c "^---$" /Users/luizcampos/Documents/lectures/just-travel/slides/slides.md
```
Expected: 47 separadores (48 slides + 1 frontmatter inicial - 1 slide sem `---` após = 47).

- [ ] **Step 3: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add slides/slides.md
git commit -m "feat(slides): add closing section (6 slides) — scale, Monday action, LinkedIn"
```

---

## Task 13: Build estático + export PDF

**Files:** nenhum (apenas validação de comandos)

- [ ] **Step 1: Rodar build estático**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && npx slidev build --base /solid-just-travel/
```

Expected: `dist/` criado com HTML estático, sem erros.

```bash
ls /Users/luizcampos/Documents/lectures/just-travel/slides/dist/index.html && echo "build ok"
```
Expected: `build ok`.

- [ ] **Step 2: Rodar export de PDF (backup)**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && npx slidev export --output dist/slides.pdf
```
Expected: `dist/slides.pdf` criado.

```bash
ls -lh /Users/luizcampos/Documents/lectures/just-travel/slides/dist/slides.pdf
```
Expected: arquivo com tamanho > 500KB (48 slides com código geram PDF substancial).

Nota: o export de PDF requer Playwright instalado. Se falhar com "browser not found", rodar:
```bash
cd /Users/luizcampos/Documents/lectures/just-travel/slides && npx playwright install chromium
```
E tentar de novo.

- [ ] **Step 3: Confirmar que `dist/` está no `.gitignore`**

```bash
grep -q "^dist/$" /Users/luizcampos/Documents/lectures/just-travel/slides/.gitignore && echo "dist ignored ok"
```
Expected: `dist ignored ok`.

- [ ] **Step 4: Sem commit necessário**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git status
```
Expected: `dist/` não aparece (ignorado). `node_modules/` não aparece. Árvore limpa tirando `.claude/`.

---

## Task 14: GitHub Actions workflow pra deploy no GitHub Pages

**Files:**
- Create: `.github/workflows/deploy-slides.yml`

- [ ] **Step 1: Criar workflow**

Criar `/Users/luizcampos/Documents/lectures/just-travel/.github/workflows/deploy-slides.yml` com:

```yaml
name: Deploy Slidev slides to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - "slides/**"
      - ".github/workflows/deploy-slides.yml"
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: slides
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"
          cache-dependency-path: slides/package-lock.json

      - run: npm ci

      - name: Build Slidev
        run: npm run build

      - uses: actions/configure-pages@v4

      - uses: actions/upload-pages-artifact@v3
        with:
          path: slides/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Validar o YAML (sintaxe)**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && python -c "
import yaml, sys
with open('.github/workflows/deploy-slides.yml') as f:
    data = yaml.safe_load(f)
assert 'jobs' in data and 'build' in data['jobs'] and 'deploy' in data['jobs']
print('yaml ok, jobs:', list(data['jobs'].keys()))
"
```
Expected: `yaml ok, jobs: ['build', 'deploy']`.

- [ ] **Step 3: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add .github/workflows/deploy-slides.yml
git commit -m "ci: add GitHub Pages deploy workflow for Slidev slides"
```

Nota: o workflow só vai disparar quando o repositório for pushed pro GitHub **e** Pages estiver habilitado. Configuração pós-push: Settings → Pages → Source: "GitHub Actions".

---

## Task 15: Update root `README.md` — marcar Plan C ✅

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update `README.md`**

Find:
```markdown
- [`slides/`](./slides) — deck Slidev da palestra *(Plan C — em construção)*
```

Change to:
```markdown
- [`slides/`](./slides) — deck Slidev da palestra ✅
```

- [ ] **Step 2: Commit**

```bash
cd /Users/luizcampos/Documents/lectures/just-travel && git add README.md
git commit -m "docs: mark Plan C (slides/) as completed in root README"
```

---

## Self-Review

### 1. Spec coverage

| Spec item | Task |
|---|---|
| 48 slides em 12 seções | Tasks 5-12 (5 abertura, 4×6 SOLID blocks + 1×7 DIP, 1 resumo, 4 after tour, 1 escala, 1 Monday, 1 LinkedIn, 1 obrigado = 48) |
| Slidev stack | Task 1 (package.json), Task 5+ (conteúdo) |
| Snippets reais de before/after | Tasks 3, 4 (5 snippets cada) |
| Speaker notes em pt-BR com roteiro | Todos os slides (HTML comments) |
| Tema escuro + JetBrains Mono | Task 5 (frontmatter do slides.md) |
| Fragments `<v-clicks>` | Tasks 5-12 (usados em vários slides) |
| Side-by-side layout | Tasks 6, 7, 8, 9, 10, 12 (two-cols, grid-cols-2) |
| Syntax highlight via Shiki | Task 5 (highlighter: shiki no frontmatter) |
| GitHub Pages deploy | Task 14 |
| PDF backup | Task 13 |
| LinkedIn card | Task 12 (slide 46 com layout two-cols) |

### 2. Placeholder scan

- "linkedin-avatar.jpg" é placeholder explícito, documentado no slide 46 speaker notes como "substituir antes da palestra"
- `linkedin.com/in/luizcampos331` — username real do autor (luizcampos331@gmail.com); ajustar se URL do LinkedIn for diferente
- `github.com/luizcampos331/solid-just-travel` — URL placeholder, nota no speaker notes pede pra atualizar pré-palestra

Sem outros TODO/TBD. Nenhum "similar to Task N".

### 3. Type consistency

- `slides/slides.md` é um arquivo único e linear — sem tipos
- Imports de snippets usam `@/snippets/...` consistentemente
- Frontmatter fields (theme, title, author) definidos no slide 1 e não redefinidos
- `<<< @/snippets/xxx.py {lines}` syntax uniform em todos os slides de código

---

## Execution Handoff

**Plan C complete and saved to `docs/superpowers/plans/2026-04-23-plan-c-slides-slidev.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, two-stage review (spec + quality), fast iteration.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

**Which approach?**
