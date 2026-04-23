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
