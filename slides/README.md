# `slides/` — Deck Slidev da palestra SOLID + Clean Arch

Deck Slidev sobre SOLID na prática, usando os repos [`../before/`](../before) e [`../after/`](../after) como material didático. **Roda 100% local** — não há deploy público.

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

## Como fazer build estático (opcional)

```bash
npm run build   # gera dist/ servível por qualquer http server estático
```

## Estrutura do deck

Seções (ordem na apresentação):

1. **Capa + quem sou eu**
2. **Por que SOLID importa + a promessa**
3. **Estrutura do `before/`** — árvore de pastas, "cada arquivo esconde uma violação"
4. **S — Single Responsibility** (definição → dor → cura → comparação → ganhos)
5. **O — Open/Closed** (mesma estrutura)
6. **L — Liskov**
7. **I — Interface Segregation**
8. **D — Dependency Inversion**
9. **Estrutura do `after/`** — árvore que emergiu
10. **Cada princípio mora em camadas** + diagrama Clean Arch
11. **Regras de ouro + quando 4 layers não bastam**
12. **O que fazer segunda-feira de manhã**
13. **Me segue lá + livros + repo + Q&A**

## Shortcuts durante a palestra

- `SPACE` / `→` — próximo slide/animação
- `←` — voltar
- `P` — presenter mode
- `O` — visão geral (overview)
- `D` — modo escuro
- `F` — fullscreen
