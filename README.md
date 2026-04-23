# Palestra SOLID + Clean Arch — Just Travel

Material da palestra "SOLID na prática com Clean Architecture minimalista" para o time de desenvolvimento da Just Travel.

## Estrutura

- [`before/`](./before) — CRUD FastAPI realista-ingênuo, com violações curadas dos 5 princípios SOLID ✅
- [`after/`](./after) — mesmo CRUD refatorado com Clean Arch minimalista + SOLID aplicado ✅
- [`slides/`](./slides) — deck Slidev da palestra *(Plan C — em construção)*
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
