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
