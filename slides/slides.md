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
- Staff engineer, 10+ anos de experiencia em tecnologia
- Já sofri na pele a dor das violações de SOLID em produção
- Hoje venho como "guia turístico" — vocês conhecem a linguagem melhor que eu

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

# Estrutura do `before/`

```
before/app/
├── database.py        ← engine + SessionLocal
├── main.py            ← FastAPI app
├── models.py          ← entidades ORM (+ validação + email + JSON)
├── routers/           ← handlers HTTP
│   ├── packages.py
│   └── travelers.py
├── schemas.py         ← Pydantic IO
└── services/          ← lógica + repository
    ├── booking_service.py
    └── package_service.py
```

<div class="text-center mt-6 text-base opacity-70">
Parece um FastAPI normal. <strong>Cada arquivo esconde uma das 5 violações.</strong>
</div>

<!--
Fala (90s): "Antes de mergulhar nas letras, olhem a estrutura do before.
Pasta routers/, services/, models/, schemas/ — tutorial clássico de
FastAPI. Nada óbvio de errado à primeira vista. É justamente isso que
torna SOLID interessante: o código DOENDO geralmente parece organizado.
Cada um desses arquivos esconde uma das 5 violações que vamos abrir
nos próximos 70 minutos. Guardem essa árvore — vamos voltar nela no
final pra comparar com o que emergiu do after/."
-->

---

# S — Single Responsibility Principle

<div class="text-xl mt-4 mb-6">
Uma classe deve ter apenas uma razão para mudar.
</div>

<div class="text-base opacity-80">
<p><strong>Ou seja:</strong> responde a um <em>único stakeholder</em>.</p>
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

<<< @/snippets/before/traveler_god_class.py {all|10-16|18-21|24-25|28-30}{maxHeight:'400px'}

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

<<< @/snippets/before/calculate_price_ifelse.py {all|4-5|6-7|8-9|10-12}{maxHeight:'420px'}

<!--
Fala (3 min): "Calculate_price. [click] seasonal. [click] black_friday
adicionado ano passado. [click] corporate depois. [click] cyber_monday
semana passada. 4 branches e contando. Quem quer fazer a feature 'desconto
estudante'? É outro elif — e todo elif NOVO é um risco pros 4 antigos."
-->

---

# O — A cura no `after/`

<<< @/snippets/after/discount_strategies.py {all|2-3|6-7|17-22|25}{maxHeight:'420px'}

<!--
Fala (3 min): "Strategy pattern via Protocol. [click] Define o contrato.
[click] NoDiscount. [click] Cyber Monday tem ramo interno — sim, mas é
uma regra da própria estratégia, não alterna entre estratégias. [click]
Nova promoção = nova classe. Zero edição em classe existente."

Pergunta antecipada: "o que é esse Protocol?"

Resposta de bolso: "Protocol é o jeito moderno de Python dizer 'qualquer
classe com esse método serve aqui'. Tipo interface do TypeScript. Não
precisa herdar nada — se tem apply(), é um DiscountPolicy. O ganho: a
classe que implementa não precisa nem importar a Protocol."

Pergunta antecipada: "mas o _pick_discount_policy em dependencies.py
tem um match/case mapeando string → policy. Isso não é OCP de novo?"

Resposta de bolso: "Esse match é o tradutor entre HTTP e domínio. Ele
CONHECE todas as policies de propósito — alguém precisa. O ganho do OCP
foi tirar isso de dentro do CÁLCULO. O cálculo continua intocado quando
entra promoção nova."
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
Adicionar = nova classe. <strong>Zero edição</strong> nas que já funcionam.
</div>

<!--
Fala (2 min): "4 ganhos. O mais palpável: testes de cada política rodam
em microssegundos, sem banco, sem nada. 6 políticas, 6 testes paralelos."
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

<<< @/snippets/before/lsp_bomb.py {all|2-5|8-10|14-25|20-21}{maxHeight:'420px'}

<!--
Fala (3min30s): "[click] Classe base cancel() atualiza status. [click]
Subclasse lança exception. [click] Service faz o for clássico. [click]
ZOOM no 'package.cancel()' — esse é o momento da bomba. Query retorna
MIX de TravelPackage e NonRefundablePackage (STI no SQLAlchemy). Loop
itera. Hora que chega no primeiro NonRefundable: ValueError. Alguns já
foram marcados 'cancelled' na memória. Partial failure clássico.
Pausa pra digerir — Liskov é o mais abstrato dos 5, vale repetir
o caminho da bomba devagar."

Pergunta: "Quem já escreveu um for que funcionava nos testes e
explodiu em produção porque entrou tipo diferente?" → mão levanta.
-->

---

# L — A cura no `after/`

<<< @/snippets/after/cancel_all_graceful.py {all|2-5|9-12|14-24}{maxHeight:'430px'}

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

Frases-âncora pra usar ao explicar cada bullet:

Sobre "Menos classes":
"Toda vez que você cria uma subclasse só pra mudar o comportamento de UM
método, pergunte: 'isso é um tipo diferente, ou é o mesmo tipo com uma
flag?'. Quase sempre é a flag."

Sobre "Contrato honesto":
"Honesto = a assinatura da função fala a verdade. Se a função pode falhar
parcialmente, o tipo de retorno tem que admitir isso. Esconder com int ou
void é mentir pro caller."

Sobre a regra final "composição > herança":
"Herança é uma promessa rígida — 'subtipo se comporta como pai'. Toda vez
que um subtipo precisa mentir sobre essa promessa (override que muda
contrato), você acabou de plantar bomba. Se você precisa de polimorfismo,
prefira interface (Protocol em Python) + composição. Reserve herança pra
casos onde o subtipo só acrescenta, nunca substitui."
-->

---

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
implementa OS 12."
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

<<< @/snippets/before/fat_repository.py {all|5-17|20-28}{maxHeight:'450px'}

<!--
Fala (3min30s): "[click] 12 métodos no repo real. add é o único usado pelo
CreatePackage. [click] Fake de teste: 12 NotImplementedError. Se amanhã
alguém adiciona um 13º método, toda infraestrutura de testes quebra.
Pior: o fake é MAIOR que o código sendo testado. 3 linhas pra 20.
Pausa: ISP costuma ser confundido com 'classes pequenas'. Reforce a
distinção — é sobre o cliente NÃO ser obrigado a saber dos métodos
que não usa."

Pergunta: "Quem já desistiu de escrever um teste porque o mock ficou
maior que o código? Não precisa ter orgulho, todo mundo já fez."
-->

---

# I — A cura no `after/`

<<< @/snippets/after/isp_segregated.py {all|6-8|11-14|16-22|25-29}{maxHeight:'430px'}

<!--
Fala (3 min): "[click] 2 Protocols pequenos: Writer (2 métodos) e Reader
(3 métodos). [click] PackageWriter tem só add e update. [click] Use case
declara DEPENDÊNCIA ESTREITA: só Writer. [click] Fake de teste cabe num
post-it: 2 métodos. Mesmo CreatePackage, mesma funcionalidade, teste
10× mais limpo."

Pergunta antecipada: "cadê o sufixo Repository?"

Resposta de bolso: "Sufixo descreve o papel que a classe cumpre, não a
categoria arquitetural. Quando o repositório é monolítico, o papel é
'ser repositório'. Quando você fragmenta, cada fragmento ganha o papel
mais específico." (E o adapter concreto SqlAlchemyPackageRepository
mantém o sufixo — só os Protocols fragmentados é que ganham nome por
papel: Writer/Reader, à la io.Reader/io.Writer do Go.)
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
- **Menos código de teste** — escrever teste fica trivial

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

# D — Dependency Inversion Principle

<div class="text-xl mt-4 mb-6">
Dependa de abstrações, não de implementações.
</div>

<div class="text-base opacity-80">
<p>Alto nível (regra de negócio) e baixo nível (banco, SMTP, cache)
<strong>ambos dependem de abstração</strong>.</p>
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

<<< @/snippets/before/dip_violation_router.py {all|5-7|9-15}{maxHeight:'440px'}

<!--
Fala (3 min): "[click] Router importa SessionLocal. Handler de negócio
importando INFRA. Seta invertida. [click] Construção de sessão dentro
do handler. [click] Chamadas ORM diretas. Pra testar? Precisa subir
banco. Pra trocar banco? Mexe no handler. Regra de negócio ACOPLADA
a detalhe."
-->

---

# D — A cura no `after/`

<<< @/snippets/after/dip_composition.py {all|2-7|10|13-14|17-18|20-24|28-34}{maxHeight:'430px'}

<!--
Fala (3min30s): "[click] get_db provider. [click] DbSession alias. [click]
Repo provider. [click] Aliases pros providers — economiza boilerplate.
[click] Wiring do use case. [click] Handler: RECEBE o use case. Nunca
importa banco, nunca importa SessionLocal, nunca importa SQLAlchemy.
Regra de negócio PURA — depende só de Protocols. Esse é o slide mais
denso da palestra; vale percorrer cada Annotated com calma e mostrar
que NADA aqui é mágico — é Python composto."
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
Fala (3 min): "Aqui está o 'aha moment'. Vocês leram a doc do FastAPI,
aprenderam Depends(), acharam conveniente. NINGUÉM te disse que você
estava aplicando DIP. Mas está. O que muda no after: em vez de depender
de CLASSE CONCRETA (SessionLocal, SqlAlchemyTravelerRepository), vocês
dependem de PROTOCOL (TravelerRepository). Mesma mecânica, abstração
maior. Reforço: peça pra alguém da plateia explicar com as próprias
palavras antes de avançar — esse insight é o que mais cola na semana
seguinte. Se o time pegou esse, levou a palestra."
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
- Mais código pra abrir/fechar sessão do que pra criar viajante
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
- **Composition root explícito** — `presentation/dependencies.py` mostra o mapa
- **Handlers triviais** — 3-5 linhas, impossível esconder bug

</v-clicks>

<div v-click class="mt-8 text-center text-lg opacity-80">
<strong>Negócio decide os detalhes. Não o contrário.</strong>
</div>

<!--
Fala (2 min): "Ganho principal: testabilidade. Antes, precisamos do
banco pra testar 'criar viajante'. Depois, um InMemoryRepository. Esse
é o argumento que vende pro júnior que nunca escreveu teste 'porque dá
trabalho' — olha, não dá mais."
-->

---

# Estrutura do `after/`

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

# Essa estrutura nos mostra algo:

<div class="text-6xl mt-8 font-bold">
Clean Architecture
</div>

<div class="text-lg mt-8 opacity-70 max-w-2xl">
E aqui está a coisa <strong>importante</strong>:<br/>
<u>não definimos</u> isso antes. <br/>
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

<div class="grid grid-cols-2 gap-6 mt-2 text-sm">

<div>

**domain** (o núcleo)
- **S** — entidades + VOs separados
- **L** — entidades planas com flags
- **O** — policies e strategies
- **I** — Protocols segregados

<img src="/clean-architecture.png" class="max-h-40 mx-auto mt-2" alt="Clean Architecture concentric circles by Robert C. Martin" />

</div>

<div>

**application**
- **S** — um use case por ação
- **L** — partial result em vez de explodir mid-loop
- Só conhece `domain/`

**infra**
- **D** — implementa Protocols do domain
- Adapters plugáveis

**presentation**
- **S + I** — schemas e routers finos
- **D** — composition root via `Depends()`

</div>

</div>

<div class="absolute bottom-6 left-0 right-0 text-center text-lg opacity-80">
Setas apontam <strong>pra dentro</strong>. Sempre.
</div>

<!--
Fala (2min30s): "Mapa completo. Qual letra vive onde. DIP é o que
desenha a arquitetura: ele diz que setas apontam pra dentro. SRP
define o tamanho das caixas. OCP abre espaço dentro de cada caixa.
ISP define a fronteira entre caixas. LSP garante que substituir
implementação não quebra nada. Aproveite pra reapresentar o repo
inteiro com essa lente — abrir o IDE rapidinho e mostrar que cada
pasta de after/ é uma das letras virando pasta."
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
Fala (2min30s): "Não decorem. Estudem SOLID, essas regras CAEM. É o
contrário do que o livro do Uncle Bob sugere. Ele diz 'adote essa
estrutura'. Eu digo 'pratique SOLID, a estrutura aparece'. Caminho
diferente, mesmo destino. Antes de avançar, deixe a regra final
respirar: 'enquanto não dói, seu código de 5 linhas É o design
correto' — isso desarma o medo de júnior achar que precisa
arquitetar tudo no dia 1."
-->

---

# Quando SOLID pede ainda mais separação

<div class="text-lg mt-4 mb-6">
Sinais de que projeto está cresendo e precisa de mais divisões:
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
2. **Identifique qual letra dói** mais ali
3. **Refatore 1 princípio por vez** — não aplique SOLID tudo de uma
4. **Escreva o teste antes** — garante que comportamento não muda

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
---

# Me segue lá

<div class="flex flex-col items-center text-center">
  <img src="/linkedin-avatar.jpg" class="w-32 h-32 rounded-full" />
  <div class="mt-3 font-bold text-xl">Luiz Campos</div>
  <div class="text-base opacity-70">@luizcampos331</div>
  <div class="text-sm opacity-80">linkedin.com/in/luizcampos331</div>
  <div class="mt-4 text-sm opacity-80 max-w-xs">
    DM liberada — dúvida, code review, projeto novo.<br/>
    Respondo todos.
  </div>
</div>

::right::

# Pra continuar estudando

- 📖 *Clean Code* — **Robert C. Martin**
- 📖 *Clean Architecture* — **Robert C. Martin**
- 🎥 [refactoring.guru](https://refactoring.guru) — patterns com exemplos
- 💻 Este repo: [github.com/luizcampos331/solid-just-travel](https://github.com/luizcampos331/solid-just-travel)

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
Fala (5 min Q&A): deixar aberto. Perguntas comuns antecipadas:

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
