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
