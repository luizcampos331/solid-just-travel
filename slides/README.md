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
