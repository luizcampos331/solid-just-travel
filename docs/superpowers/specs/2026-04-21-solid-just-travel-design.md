# Palestra SOLID + Clean Arch — Just Travel

**Data do design:** 2026-04-21
**Autor:** Luiz Campos
**Status:** aprovado pelo autor, aguardando revisão final antes de partir pra plano de implementação

---

## 1. Contexto e Objetivos

Palestra técnica de **1h30** sobre SOLID + Clean Architecture minimalista, a ser ministrada por Luiz Campos ao time de desenvolvimento da **Just Travel** (operadora de turismo).

### Público-alvo

- **7 desenvolvedores** — 5 juniores + 2 estagiários
- **Conhecimento prévio:** superficial sobre SOLID e padrões de projeto
- **Perfil:** esforçados, ágeis, pegam conceitos rápido
- **Stack do dia-a-dia:** Python + FastAPI (mesmo stack do demo)

### Objetivos de aprendizagem

Ao fim da palestra, os devs saem capazes de:

1. **Reconhecer** no próprio código violações de cada um dos 5 princípios SOLID
2. **Aplicar** refatorações simples que movem código "ruim-realista" pra Clean Arch mínima
3. **Entender** que Clean Arch não é "outra arquitetura" — é o **resultado natural** de SOLID bem aplicado
4. **Ter um repositório de referência** que podem consultar depois e usar como base pra projetos novos

### Entregáveis

1. **Deck Slidev** no próprio repositório (disponível também via GitHub Pages)
2. **Repositório** com duas versões do mesmo CRUD: `before/` (ingênuo com violações) e `after/` (Clean Arch + SOLID aplicado)
3. **Testes unitários** na camada `application` do `after/` — argumento de venda pró-SOLID (testabilidade)
4. **README** em pt-BR com roteiro de como rodar ambos e mapa de violações por princípio

---

## 2. Formato da Palestra

### Approach escolhido: **Tour Guiado + Deep Dive**

**Abertura (10 min)** — introdução + **tour guiado pelo `before/`**: subir a aplicação, fazer 1 request, passear pelo código apontando *"tem coisa estranha aqui, aqui e aqui — guardem isso, a gente volta"*. O objetivo do tour é plantar sementes; os devs ficam no modo "caça ao tesouro" durante a palestra.

**Miolo (65 min)** — princípio por princípio (~13 min cada), todos seguindo a **mesma estrutura de 4 passos**:

1. Conceito em 1 slide com metáfora Just Travel (2 min)
2. *"Lembram da coisa estranha do tour? Era isso"* — volta ao `before/` (3 min)
3. Refatoração ao vivo ou side-by-side no `after/` (5 min)
4. *"Quanto custou: X linhas. Quanto ganhamos: Y testabilidade/flexibilidade"* (3 min)

**Fechamento (15 min)** — tour rápido pelo `after/` amarrando *"a estrutura que emergiu é Clean Arch"* + slide de "quando SOLID pede mais separação" + Q&A + recursos.

### Por que esse formato

- Combina **estrutura linear** (previsibilidade, importante pra júnior) com **narrativa** (engajamento)
- Tour inicial planta curiosidade → aulas de princípio respondem → fechamento integra
- "Código ruim → código bom" mantendo **mesmo comportamento observável** vende a mensagem: *SOLID não muda o que o software faz, muda o custo de mudá-lo depois*

---

## 3. Cronograma Detalhado

| Bloco | Tempo | Minuto | Conteúdo |
|---|---|---|---|
| Abertura | 5 min | 00:00 → 00:05 | Quem sou + "por que SOLID importa" + acordar a galera |
| Tour guiado pelo `before/` | 5 min | 00:05 → 00:10 | Subir app, 1 request, passear apontando estranhezas |
| **S** — Single Responsibility | 13 min | 00:10 → 00:23 | Conceito → dor → cura → balanço |
| **O** — Open/Closed | 13 min | 00:23 → 00:36 | Descontos de pacote como gancho |
| **L** — Liskov Substitution | 13 min | 00:36 → 00:49 | Cancelamento de pacote como gancho |
| **I** — Interface Segregation | 13 min | 00:49 → 01:02 | Repositório gigante + mock gigante como gancho |
| **D** — Dependency Inversion | 13 min | 01:02 → 01:15 | Ponto alto: liga tudo com `Depends()` do FastAPI |
| Tabela-resumo SOLID | 2 min | 01:15 → 01:17 | Slide de consolidação |
| Tour pelo `after/` → Clean Arch emerge | 5 min | 01:17 → 01:22 | Revelação pedagógica |
| "Quando SOLID pede mais separação" | 2 min | 01:22 → 01:24 | O slide de escala (routes × controllers etc.) |
| Q&A + fecho | 6 min | 01:24 → 01:30 | Perguntas + links de estudo + LinkedIn |

**Balanceamento do cronograma:** os 5 princípios têm o mesmo tempo (13 min) por uniformidade pedagógica, mesmo que DIP e OCP tenham "mais carne". O fechamento compensa: **tour do `after/` (5 min) + slide de escala (2 min)** dão espaço pra amarrações que dependem especialmente de DIP.

---

## 4. Arquitetura do Repositório

### Estrutura raiz

```
solid-just-travel/
├── README.md                    ← pt-BR: como rodar, como ler, mapa de violações
├── .gitignore
├── .python-version              ← 3.12
├── pyproject.toml               ← deps compartilhadas (FastAPI, SQLAlchemy, pytest)
│
├── before/                      ← realista-ingênuo com violações curadas
│   ├── app/
│   └── README.md
│
├── after/                       ← Clean Arch minimalista + SOLID aplicado
│   ├── app/
│   ├── tests/
│   └── README.md
│
└── slides/                      ← Slidev deck
    ├── slides.md
    ├── package.json
    ├── snippets/
    ├── public/
    └── components/
```

### `before/` — estrutura "realista-ingênua"

Parece tutorial FastAPI comum. Os devs reconhecem de cara.

```
before/app/
├── main.py                      ← FastAPI app + wiring direto
├── database.py                  ← SQLAlchemy engine + SessionLocal
├── models.py                    ← Traveler + TravelPackage como God Classes
├── schemas.py                   ← Pydantic com duplicação
├── routers/
│   ├── travelers.py             ← handlers gordos, regra no meio
│   └── packages.py              ← idem + cálculo de preço inline
└── services/
    └── package_service.py       ← classe com if/elif pra tipo de desconto
```

**Violações plantadas** (detalhadas na Seção 5):

- `models.Traveler` faz ORM + validação + email + formatação (SRP)
- `package_service.calculate_price` tem `if/elif` pra cada desconto (OCP)
- `NonRefundablePackage(TravelPackage)` sobrescreve `.cancel()` jogando exceção (LSP)
- `PackageRepository` com 12 métodos — testes precisam de mock de 12 métodos (ISP)
- Handlers importam `SessionLocal`, constroem SQLAlchemy session direto (DIP)

### `after/` — Clean Arch minimalista

```
after/app/
├── main.py                      ← composition root (Depends wirings)
│
├── domain/                      ← núcleo puro, zero dependência externa
│   ├── travelers/
│   │   ├── traveler.py          ← entidade (dataclass)
│   │   ├── document.py          ← Value Object com validação
│   │   └── traveler_repository.py  ← Protocol
│   └── packages/
│       ├── travel_package.py
│       ├── package_repository.py   ← Protocols segregados (writer/reader/finder)
│       ├── discount_policy.py      ← Protocol + strategies
│       └── cancellation_policy.py
│
├── application/                 ← use cases
│   ├── travelers/
│   │   ├── create_traveler.py
│   │   ├── list_travelers.py
│   │   └── ... (get / update / delete)
│   └── packages/
│       ├── create_package.py
│       ├── calculate_price.py
│       └── cancel_all_of_traveler.py
│
├── infra/                       ← adapters concretos
│   ├── database.py
│   ├── persistence/
│   │   ├── models/              ← SQLAlchemy models (separados do domain)
│   │   ├── sqlalchemy_traveler_repository.py
│   │   └── sqlalchemy_package_repository.py
│   └── notifications/
│       └── email_welcome_notifier.py
│
└── presentation/                ← HTTP (FastAPI)
    ├── dependencies.py          ← Depends() providers
    ├── schemas.py               ← Pydantic IO
    └── routers/
        ├── travelers.py         ← handlers finos de 3-5 linhas
        └── packages.py

after/tests/
├── application/
│   ├── travelers/
│   │   └── test_create_traveler.py
│   └── packages/
│       └── test_calculate_price.py
└── fakes/
    └── in_memory_repositories.py
```

### Princípios da arquitetura `after/`

1. **`domain/` não importa de lugar nenhum externo** — nem FastAPI, nem SQLAlchemy. Regra de ferro.
2. **`application/` só conhece o domain** — use cases recebem repositórios como `Protocol` no construtor. Um use case = uma classe = uma ação.
3. **`infra/` implementa os `Protocol`s do domain** — adapter pattern. Aqui entra SQLAlchemy.
4. **`presentation/` só orquestra** — valida entrada HTTP, chama use case, formata saída. Handlers de 3-5 linhas.
5. **Composition root em `main.py`** — único lugar que conhece todos. Wiring via `Depends()` do FastAPI.

### Decisões registradas

| Decisão | Motivo |
|---|---|
| Python 3.12 + FastAPI + SQLAlchemy + SQLite | Stack do time da Just Travel |
| Código em inglês (incluindo docstrings) | Preferência do autor |
| Slides/README/comentários explicativos em pt-BR | Idioma do público |
| Duas pastas (`before/` + `after/`) no mesmo repo | Facilita comparação lado-a-lado ao vivo |
| `typing.Protocol` em vez de `ABC` | Structural typing, menos cerimônia, Pythonic |
| SQLAlchemy models separados do domain | Didático — protege o domínio e ensina DIP |
| `Traveler` / `TravelPackage` como entidades | Sabor Just Travel cria identificação |
| CRUD via FastAPI routers (sem separar controllers) | Idiomático em FastAPI; handlers de 5 linhas não justificam separação |
| Testes unitários no `after/` com fakes in-memory | Vende testabilidade como ganho SOLID |

---

## 5. Desenho das Violações SOLID por Princípio

Cada princípio tem a mesma estrutura pedagógica: **metáfora → dor no `before/` → cura no `after/` → balanço**.

### 5.1 S — Single Responsibility Principle

**Definição acessível:** *"Uma classe deve ter apenas uma razão pra mudar"* — responde a **um único stakeholder**, não "faz só uma coisa".

**Metáfora Just Travel:** *"Um Traveler não deve ser também quem valida CPF, quem salva no banco, e quem envia email de boas-vindas. Cada um é um motivo diferente pra mudar. Se o Marketing mudar o email, você não quer mexer na entidade Traveler."*

**Violação no `before/`** (`models.py`): classe `Traveler` faz ORM (SQLAlchemy), validação (`validate()`), persistência (`save()`), notificação (`send_welcome_email()`), formatação (`to_dict()`). 4+ stakeholders diferentes.

**Cura no `after/`:**

- `domain/travelers/traveler.py` — entidade pura (dataclass), invariantes
- `domain/travelers/document.py` — Value Object de CPF
- `infra/persistence/sqlalchemy_traveler_repository.py` — persiste
- `infra/notifications/email_welcome_notifier.py` — notifica
- `presentation/schemas.py::TravelerOut` — formata JSON

**Balanço:** *"Trocamos 1 classe de 40 linhas por 5 classes de ~10 linhas. Não foi 'mais código' — foi código em lugares certos. Compliance pode mexer na validação sem olhar o banco."*

### 5.2 O — Open/Closed Principle

**Definição acessível:** *"Aberto pra extensão, fechado pra modificação"* — novo comportamento via nova classe, não alterando existente.

**Metáfora Just Travel:** *"Black Friday: desconto de 30%. Semana que vem Cyber Monday: desconto progressivo. Se toda regra nova te força a abrir o mesmo arquivo e adicionar um `elif`, seu código está fechado pra extensão e aberto pra modificação — o oposto."*

**Violação no `before/`** (`services/package_service.py`):

```python
def calculate_price(package, discount_type):
    if discount_type == "seasonal":   price *= 0.85
    elif discount_type == "black_friday": price *= 0.70
    elif discount_type == "corporate": price -= 200
    elif discount_type == "cyber_monday": ...
```

Cada novo desconto mexe em função existente — risco de regressão.

**Cura no `after/`** (Strategy via Protocol):

```python
class DiscountPolicy(Protocol):
    def apply(self, package: TravelPackage) -> Decimal: ...

class SeasonalDiscount:     def apply(self, p): return p.base_price * Decimal("0.85")
class BlackFridayDiscount:  def apply(self, p): return p.base_price * Decimal("0.70")

class CalculatePackagePrice:
    def __init__(self, policy: DiscountPolicy): self._policy = policy
    def execute(self, p): return self._policy.apply(p)
```

**Balanço:** *"Desconto novo = classe nova. Nunca mais quebra regra antiga mexendo em nova. Teste vira trivial."*

### 5.3 L — Liskov Substitution Principle

**Definição acessível:** *"Se função aceita `TravelPackage`, aceita qualquer subclasse sem explodir. Subclass não pode **mentir** sobre o contrato da classe-mãe."*

**Metáfora Just Travel:** *"`TravelPackage` tem `.cancel()`. Alguém criou `NonRefundablePackage(TravelPackage)` e sobrescreveu `.cancel()` lançando exceção. Tudo funcionava — até o dia que 'cancelar todos os pacotes do viajante' rodou em produção, iterou 40 pacotes, achou 1 não-reembolsável e explodiu no meio. 39 cancelados parcialmente. Caos."*

**Violação no `before/`:**

```python
class TravelPackage:
    def cancel(self): self.status = "cancelled"

class NonRefundablePackage(TravelPackage):
    def cancel(self):
        raise CannotCancelError("Non-refundable can't be cancelled")

# services/booking_service.py
for package in packages:   # ← inocente
    package.cancel()       # ← BOOM pros NonRefundable
```

**Cura no `after/`** (capability como dado, não como tipo):

```python
@dataclass
class TravelPackage:
    refundable: bool              # ← flag no dado
    ...

class CancellationPolicy:
    def cancel(self, package):
        if not package.refundable: raise CannotCancelError(...)
        return replace(package, status=PackageStatus.CANCELLED)

class CancelAllOfTraveler:
    def execute(self, traveler_id):
        packages = self._repo.by_traveler(traveler_id)
        cancelled, skipped = [], []
        for p in packages:
            if p.refundable: cancelled.append(self._policy.cancel(p))
            else: skipped.append(p)
        return CancelResult(cancelled=cancelled, skipped=skipped)
```

**Balanço:** *"Herança parece atalho — cada `override` que muda contrato é bomba-relógio pro `for` inocente. Composição + dados sobre herança. Aqui: trocamos subclasse por flag + policy. Menos código, contrato honesto."*

**Pergunta de plateia:** *"Quem já escreveu um for que funcionava nos testes e quebrou em produção quando entrou tipo diferente? Levante a mão."*

### 5.4 I — Interface Segregation Principle

**Definição acessível:** *"Interface pequena, cliente feliz. Nenhuma classe deve ser forçada a depender de métodos que não usa."*

**Metáfora Just Travel:** *"`PackageRepository` com 12 métodos. O use case `CreatePackage` usa **um: `add`**. Mas pra testar você precisa de um fake que implementa os 12."*

**Violação no `before/`:**

```python
class PackageRepository:
    def add(self, p): ...
    def by_id(self, id): ...
    def list(self): ...
    def update(self, p): ...
    def delete(self, id): ...
    def find_by_destination(self, d): ...
    def find_by_price_range(self, lo, hi): ...
    def paginated(self, page): ...
    def count_by_traveler(self, tid): ...
    def upsert(self, p): ...
    def archive(self, id): ...
    def bulk_insert(self, ps): ...

# tests — 20 linhas de NotImplementedError pra testar 3 linhas
class FakePackageRepository:
    def add(self, p): self.last = p
    def by_id(self, id): raise NotImplementedError
    # ... × 11
```

**Cura no `after/`** (Protocols segregados):

```python
class PackageWriter(Protocol):
    def add(self, p: TravelPackage) -> None: ...
    def update(self, p: TravelPackage) -> None: ...

class PackageReader(Protocol):
    def by_id(self, id: PackageId) -> TravelPackage | None: ...
    def list(self) -> list[TravelPackage]: ...

class PackageFinder(Protocol):
    def find_by_destination(self, d) -> list[TravelPackage]: ...
    def find_by_price_range(self, lo, hi) -> list[TravelPackage]: ...

class CreatePackage:
    def __init__(self, writer: PackageWriter): self._writer = writer
    # só precisa de Writer

# tests — fake cabe num post-it
class FakePackageWriter:
    def __init__(self): self.added = []
    def add(self, p): self.added.append(p)
    def update(self, p): ...
```

Uma classe `SqlAlchemyPackageRepository` **implementa os três Protocols** — a implementação concreta não fragmenta, só o **contrato** que cada cliente vê.

**Balanço:** *"Interface grande é dívida técnica fantasiada de conveniência. Mocks triviais, testes rápidos."*

**Pergunta de plateia:** *"Levante a mão quem já escreveu um mock enorme pra testar um service que usa 2 métodos."*

### 5.5 D — Dependency Inversion Principle

**Definição acessível:** *"Dependa de abstrações, não de implementações. Alto nível e baixo nível dependem de abstração."*

**Metáfora Just Travel:** *"A regra 'Traveler menor de idade precisa de autorização' é decisão de negócio. Ela não pode depender de SQLAlchemy, FastAPI, PostgreSQL. Se amanhã migrarmos pra MongoDB, a regra é a mesma. O detalhe muda — a política, não."*

**Violação no `before/`:**

```python
def create_traveler(body):
    session = SessionLocal()       # depende de infra
    traveler = Traveler(**body.dict())
    session.add(traveler)           # depende de SQLAlchemy
    session.commit()
    send_email(traveler.email, ...) # depende de SMTP concreto
    return traveler
```

**Cura no `after/`:**

```python
class TravelerRepository(Protocol):
    def add(self, t: Traveler) -> None: ...
    def by_id(self, id: TravelerId) -> Traveler | None: ...

class CreateTraveler:
    def __init__(self, repo: TravelerRepository, notifier: WelcomeNotifier):
        self._repo = repo
        self._notifier = notifier
    def execute(self, input):
        t = Traveler.new(input)
        self._repo.add(t)
        self._notifier.notify_welcome(t)
        return t

# presentation
def create(body, uc: CreateTraveler = Depends(get_create_traveler)):
    return uc.execute(body.to_input())

# main.py composition root
def get_create_traveler():
    return CreateTraveler(
        repo=SqlAlchemyTravelerRepository(session),
        notifier=EmailWelcomeNotifier(smtp_config),
    )
```

**Setas de dependência** apontam todas pro domain. Infra conhece domain; domain não conhece infra.

**Balanço (slide final do SOLID):** *"`Depends()` do FastAPI que vocês já usam = DIP. Vocês não precisam adotar framework de DI — o FastAPI entrega pronto. Agora é só apontar pra `Protocol` em vez de classe concreta."*

### 5.6 Tabela-resumo (slide 42)

| Princípio | Dor | Cura | Onde mora no Clean Arch |
|---|---|---|---|
| **S** | Classe responde a muitos chefes | Separe por quem pediu a mudança | `domain` + `infra` + `presentation` |
| **O** | Novo comportamento edita o mesmo arquivo | Strategy/Policy | `domain/*/policy.py` |
| **L** | Subclasse mente sobre contrato | Composição sobre herança | `domain` (entidades planas + policies) |
| **I** | Interface fat acopla cliente a métodos não-usados | Interfaces pequenas e focadas | `domain/*/protocol.py` |
| **D** | Alto nível depende de baixo nível | Ambos dependem de abstração | `domain` central, `infra` implementa |

---

## 6. Arquitetura do Deck Slidev

### Stack e convenções

- **Slidev** com tema padrão customizado (cores Just Travel + tema escuro)
- **Fonte de código:** Fira Code ou JetBrains Mono (ligatures)
- **Syntax highlight:** Shiki (paleta VSCode — familiar)
- **Transições:** `slide-left` global, `fade` entre blocos de princípio
- **Speaker Mode:** `slidev --presenter` — tela pública + tela privada com notas + timer

### Estrutura de arquivos

```
slides/
├── slides.md                    ← deck completo (seções via ---)
├── package.json
├── snippets/
│   ├── before/ (.py)            ← imports reais de código
│   └── after/ (.py)
├── components/
│   ├── BeforeAfter.vue          ← layout side-by-side
│   └── SolidBadge.vue           ← badge visual S/O/L/I/D
└── public/
    ├── diagrams/
    └── logo-just-travel.svg
```

**Decisão-chave:** código importado via `<<< @/snippets/...` em vez de inline. Benefício: deck sempre sincronizado com código real do `before/`/`after/`.

### Seções do deck

| # | Seção | Slides | Tempo |
|---|---|---|---|
| 1 | Capa + quem sou eu | 2 | 2 min |
| 2 | Por que SOLID importa | 3 | 3 min |
| 3 | Tour guiado pelo `before/` | 4 | 5 min |
| 4 | **S** — Single Responsibility | 6 | 13 min |
| 5 | **O** — Open/Closed | 6 | 13 min |
| 6 | **L** — Liskov | 6 | 13 min |
| 7 | **I** — Interface Segregation | 6 | 13 min |
| 8 | **D** — Dependency Inversion | 7 | 13 min |
| 9 | Tabela-resumo SOLID | 1 | 2 min |
| 10 | Tour pelo `after/` → Clean Arch emerge | 4 | 5 min |
| 11 | "Quando SOLID pede ainda mais separação" | 1 | 2 min |
| 12 | Q&A + LinkedIn + recursos | 2 | 6 min |

**Total: ~48 slides, 90 min** (~2 min/slide — confortável pra público júnior).

### Template padrão de cada bloco de princípio (6 slides)

```
Slide N.1 — Título e definição compacta + metáfora Just Travel
Slide N.2 — A dor (código before/ com highlights em vermelho)
Slide N.3 — Ressonância ("vocês já escreveram isso?")
Slide N.4 — A cura (código after/ com highlights em verde)
Slide N.5 — Before × After lado a lado (com métricas)
Slide N.6 — Balanço + ponte pro próximo
```

### Recursos Slidev explorados

1. **Code snippets com highlights em etapas** — `<<< @/snippets/before/traveler.py {3-8|all}`
2. **Fragments (`<v-clicks>`)** — revelação progressiva de bullets
3. **Layout `two-cols`** — side-by-side before/after com Tailwind
4. **Speaker notes** (`<!-- ... -->`) — em **todos** os slides com: tempo alvo, fala sugerida, pergunta pra plateia, próximo passo
5. **Presenter Mode** — tela dupla

### Deploy

- **GitHub Pages** via GitHub Action (`slidev build` → branch `gh-pages`)
- **Link curto** pra projeção e acesso dos devs no celular durante a palestra
- **PDF backup** (`slidev export`) no repo — fallback se wifi cair

---

## 7. Amarração Final: Clean Arch Emergindo de SOLID

### Missão do fechamento (10 min)

Revelar que, ao aplicar SOLID em cada pedaço, surgiu **sem querer** uma arquitetura — Clean Arch. Essa inversão muda a relação deles com arquitetura pra sempre: de *"mais uma coisa pra decorar"* pra *"forma natural de código SOLID"*.

### Slides 43-46

**Slide 43 — "Olhem de novo pro `after/`":** árvore do diretório do `after/app/` + fala *"esse desenho não foi decidido antes — ele **emergiu**"*.

**Slide 44 — Mapa: cada princípio mora em camada(s):** diagrama bulls-eye do Uncle Bob adaptado:

- `presentation` — ISP, SRP
- `application` — SRP
- `domain` — LSP, OCP
- `infra` — DIP
- Setas de dependência apontam todas pro `domain`

**Slide 45 — Regras de ouro emergentes** (fragments):

1. `domain/` puro (consequência de DIP)
2. Use cases orquestram regra (consequência de SRP)
3. `infra/` plugável (consequência de DIP + OCP)
4. `presentation/` fino (consequência de ISP + SRP)

**Slide 46 — "Quando SOLID pede ainda mais"** (sinais de escala):

- Handler > 15 linhas → extraia controller
- Mesma ação em HTTP + CLI + worker → controller centraliza
- API com 80+ endpoints → separação de routes/controllers ajuda o "mapa do site"
- Regra de ouro: *SOLID responde a dor. Enquanto não dói, handler de 5 linhas é o design correto.*

### Slide 47 — "O que fazer segunda-feira de manhã"

Chamada pra ação concreta pros juniores:

1. Escolher 1 arquivo que incomoda
2. Identificar qual letra dói mais ali (tabela-resumo)
3. Refatorar 1 princípio por vez
4. Escrever teste antes da refatoração
5. Mandar PR pro code review pedindo feedback no princípio aplicado

### Slide 48 — LinkedIn + Recursos

**Esquerda:** Card do palestrante
- Avatar + **Luiz Campos** + nickname LinkedIn
- URL do LinkedIn
- (Infos a capturar na implementação)

**Direita:** Recursos
- *Clean Architecture* (Robert C. Martin)
- *A Philosophy of Software Design* (John Ousterhout)
- refactoring.guru
- Este repo: `github.com/<user>/solid-just-travel`

---

## 8. Considerações Transversais

### Antecipação de perguntas da plateia

| Pergunta | Resposta curta |
|---|---|
| Por que não Django? | FastAPI tem `Depends()` nativo que materializa DIP. Stack da casa. |
| Por que 2 `models` (domain puro + SQLAlchemy em `infra/`)? | Modelo de negócio ≠ modelo de persistência. Protege o domínio, ensina DIP. |
| Por que `Protocol` e não `ABC`? | Structural typing, menos cerimônia, duck-typed, Pythonic. |
| Por que não `services/` separada? | `application/` já é isso. Evita camadas redundantes. |
| Por que não separar `routes/` de `controllers/`? | Handler de 5 linhas não justifica. Ver Slide 46 pra quando vale. |

### Pontos de tensão pedagógica

1. **DIP é o mais difícil conceitualmente** — mas é o ponto alto da palestra porque se conecta ao `Depends()` que eles já usam. Tempo extra de preparação na demo aqui compensa.
2. **LSP precisa do exemplo do `for` que explode** — qualquer outra formulação fica abstrata demais pra júnior.
3. **ISP fica palpável via fake gigante em teste** — não tente vender ISP por "código limpo"; vende por "menos mock".
4. **O tour inicial precisa plantar sementes específicas** — cada "estranheza" apontada vai ser resgatada no bloco do princípio correspondente. Preparar script do tour com cuidado.

### Risco e mitigação

| Risco | Mitigação |
|---|---|
| Wifi cair durante demo | PDF do deck no repo como fallback |
| Demo ao vivo dá erro | `before/` e `after/` com smoke tests verde antes da palestra |
| Tempo estourar em princípio inicial | Cronometrar ensaio; SRP e OCP têm "gordura" se precisar cortar |
| Palestrante se perder | Speaker notes em todos os slides com roteiro explícito |
| Público mais frio do que esperado | Perguntas plantadas no material (LSP, ISP) forçam interação |

---

## 9. Não-Objetivos (fora de escopo)

Deixar explícito o que **não** é alvo desta palestra:

- **Não** ensinamos autenticação — nenhuma camada de auth no CRUD
- **Não** ensinamos testes de integração (`TestClient` do FastAPI) — só unitários no `application/`
- **Não** cobrimos DDD avançado, Agregates, Event Sourcing — Clean Arch minimalista apenas
- **Não** discutimos padrões Repository complexos (Unit of Work, Specification) — Repository básico com Protocol
- **Não** fazemos deploy produção, Docker, CI — só roda local
- **Não** entramos em debates sobre "Clean Arch é melhor que arch X" — foco é SOLID, Clean Arch emerge como consequência

---

## 10. Metadados

- **Palestrante:** Luiz Campos (avatar, nome e nickname LinkedIn a preencher na implementação do deck)
- **Empresa destino:** Just Travel ([justtravelv2.justtraveltour.com](https://justtravelv2.justtraveltour.com))
- **Duração:** 1h30
- **Modalidade:** presencial ou remota síncrona (formato flexível; deck + repo servem ambos)
- **Data de execução:** a definir

---

## Self-Review (inline)

Conferido contra critérios de qualidade:

- **Placeholders:** 2 placeholders intencionais, ambos documentados como "a preencher na implementação":
  1. URL/avatar/nickname do LinkedIn do palestrante (Seção 7, Slide 48; Seção 10)
  2. URL do repo GitHub final (Seção 7, Slide 48)
- **Contradições internas:** nenhuma detectada. Cronograma (Seção 3), seções do deck (Seção 6) e amarração final (Seção 7) batem em tempos e numeração de slides.
- **Ambiguidade:** resolvida — idioma (código: en / slides+README: pt-BR), estrutura (duas pastas no mesmo repo), abstração (`typing.Protocol`), persistência (SQLAlchemy + SQLite).
- **Escopo:** focado num único artefato coerente (palestra + repo + deck). Não-objetivos explícitos na Seção 9.
- **Pronto para implementação:** sim — próximo passo é invocar writing-plans pra quebrar em tasks executáveis.
