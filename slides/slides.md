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
