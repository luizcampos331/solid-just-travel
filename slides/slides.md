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
