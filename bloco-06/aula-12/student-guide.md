# Aula 12 — Material de apoio do aluno
### Quem recebe, valida · PB Etapa 6 · subcompetência 3.4 · **o começo do TP4**

> Esta aula já conta para o **TP4** (o TP3 fechou com a Aula 11). Consulte enquanto começa o TP4: a rota que
> **recebe** texto (*"POST /processar_texto: rota que recebe um texto enviado pelo usuário"*, item 2), os dados
> enviados **no formato correto** (item 3) e o painel **integrado** à API. O que esta aula cobre — e o que vem
> nas Etapas 7 e 8 — está na seção 9.

---

## 1. Receber: o corpo da requisição

No GET, os dados vão **na URL** (caminho e consulta — Aula 11). No **POST**, vão **no corpo**, em JSON:
*"A request body is data that you send to your API using a routing method such as POST"* [Adeshina, p47].

```python
@app.post("/relatos")
def receber(relato: dict):          # ⚠️ aceita QUALQUER dicionário
    ...
```

Com `dict`, a API aceita `{}`, `{"uf": 123}`, `{"nome": "Maria", "telefone": "…"}` — tudo com **200**. O livro
admite: *"an empty dictionary could've also been sent without returning any error"* [Adeshina, p41].

---

## 2. Validar: o modelo Pydantic

*"A model in FastAPI is a structured class that dictates how data should be received or parsed. Models are
created by subclassing Pydantic's BaseModel class."* [Adeshina, p40]

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

SiglaUF = Literal["AC", "AL", "AP", "AM", "BA", …, "TO"]            # as 27 siglas
Categoria = Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]

class Relato(BaseModel):
    model_config = ConfigDict(
        extra="forbid",                 # campo a mais: 422 (e não descarte silencioso)
        str_strip_whitespace=True,      # espaços das pontas não contam
        json_schema_extra={"examples": [{"uf": "PA", "categoria": "queimada", "texto": "Fumaça densa…"}]},
    )
    uf: SiglaUF = Field(description="Sigla da UF onde o fato foi observado.")
    categoria: Categoria
    texto: str = Field(min_length=15, max_length=500)

@app.post("/relatos")
def enviar_relato(relato: Relato):      # o tipo do parâmetro É o modelo
    ...
```

| Ferramenta | Para quê |
|------------|----------|
| `Literal[...]` | lista **fechada** de valores (siglas, categorias) |
| `Field(min_length=, max_length=)` | limites de **texto** |
| `Field(ge=, le=)` | faixa de **números** (≥, ≤) |
| `extra="forbid"` | **recusar** campos que o modelo não declara |
| `str_strip_whitespace=True` | tirar os espaços das pontas **antes** de medir |
| `json_schema_extra={"examples": [...]}` | o **exemplo** que o `/docs` mostra no *Try it out* |

> **IA como copiloto.** Dê a uma IA três exemplos reais de envio e peça o modelo Pydantic. Ela acerta o
> esqueleto — e pode esquecer `extra="forbid"`, usar `str` onde cabia `Literal`, e escrever a configuração
> no estilo do Pydantic 1 (`class Config`), comum em material antigo. Confira com a tabela acima:
> **cada tipo e cada limite são decisões suas**, e você precisa saber explicá-las.

### O 422: todos os problemas, de uma vez

```json
POST /relatos  {"uf": "Pará", "categoria": "fogo", "texto": "curto"}   ->   422
{"detail": [
  {"type": "literal_error",    "loc": ["body", "uf"],        "msg": "Input should be 'AC', 'AL', …"},
  {"type": "literal_error",    "loc": ["body", "categoria"], "msg": "Input should be 'queimada', …"},
  {"type": "string_too_short", "loc": ["body", "texto"],     "msg": "String should have at least 15 characters"}]}
```

`loc` diz **onde** (`"body"` = no corpo); `type` e `msg`, **o quê**. Corpo vazio → três `"Field required"`. A
função **nem roda**.

### ⚠️ Campo a mais: descartado ou recusado?

**Por padrão, o Pydantic DESCARTA em silêncio** o que o modelo não declara — e responde 200. Quem enviou
`nome` e `telefone` acha que foram gravados. *(O livro dá a entender que o modelo recusa: "can only take four
fields" [Adeshina, p40]. Por padrão, não recusa.)* Com `extra="forbid"`: **422** · `extra_forbidden` para
cada campo a mais. **Recuse em voz alta o que você não guarda** — e, se o dado é pessoal, não o colete
(LGPD: só o necessário).

### ⚠️ Livro × hoje (Pydantic 1 → Pydantic 2)

| No livro | Hoje |
|----------|------|
| `class Config: schema_extra = {...}` [p51–54] | `model_config = ConfigDict(json_schema_extra=...)` — o jeito antigo **roda, avisa no terminal e o exemplo some do `/docs`** |
| `"msg": "field required"`, `"type": "value_error.missing"` [p42] | `"msg": "Field required"`, `"type": "missing"` (+ o `"input"` recebido) |
| `.dict()` | `.model_dump()` |

---

## 3. Guardar: arquivo, não memória

O livro guarda numa lista — *"a temporary in-app database"* [Adeshina, p37]. Com `uvicorn --reload`, **salvar
qualquer `.py` reinicia o servidor e a lista volta vazia** (medido: 3 → 0). Em produção, qualquer reinício
faz o mesmo.

```python
import csv, threading
from pathlib import Path

ARQ = Path(__file__).resolve().parent.parent / "data" / "relatos" / "relatos.csv"
CAMPOS = ["id", "recebido_em", "uf", "categoria", "texto"]
_TRAVA = threading.Lock()
# carregar_relatos(): lê o CSV com csv.DictReader (o arquivo completo: src/relatos.py da v10)

def gravar_relato(uf, categoria, texto):
    with _TRAVA:                                   # um envio de cada vez
        anteriores = carregar_relatos()
        novo = {"id": max((r["id"] for r in anteriores), default=0) + 1, "uf": uf, ...}
        ARQ.parent.mkdir(parents=True, exist_ok=True)
        novo_arquivo = not ARQ.exists()
        with ARQ.open("a", encoding="utf-8", newline="") as f:      # "a": ACRESCENTA ("w" zeraria)
            escritor = csv.DictWriter(f, fieldnames=CAMPOS)
            if novo_arquivo:
                escritor.writeheader()
            escritor.writerow(novo)
    return novo
```

| Detalhe | Por quê |
|---------|---------|
| modo `"a"` | `"w"` apaga o que já estava lá |
| `csv.DictWriter` | vírgulas, aspas e quebras de linha **dentro** do texto não quebram o arquivo |
| a **trava** | as rotas `def` rodam em paralelo: sem ela, 40 envios simultâneos geraram só **9** números distintos (medido) |
| `data/relatos/` no `.gitignore` | o que pessoas enviam **não** vai para um repositório público |

> A trava resolve para **um** processo do servidor. Com vários, é trabalho para um banco de dados (fora do
> escopo do PB).

---

## 4. Organizar: routers

*"The APIRouter class encourages modularity and organization of application routing and logic."* [Adeshina,
p36]

```python
# api/rotas/relatos.py
from fastapi import APIRouter
router = APIRouter(prefix="/relatos", tags=["relatos"])

@router.post("", summary="Enviar um relato")       # "" -> o endereço é /relatos
def enviar_relato(relato: Relato): ...

# api/main.py — o ROTEADOR da API
app = FastAPI(title=..., description=..., version=...)
app.include_router(desmatamento.router)
app.include_router(relatos.router)
```

É a mesma ideia do `app.py` do painel (Aula 9): o roteador não desenha nem responde — só diz quem existe.
**Um assunto, um arquivo.** O livro propõe a mesma estrutura: `routes/` e `models/` [Adeshina, p89].

> ⚠️ **`@router.post("")`, não `@router.post("/")`.** Com prefixo e `"/"`, o endereço vira `/relatos/`, e um
> pedido a `/relatos` recebe um **307** (redirecionamento) antes da resposta.
>
> ⚠️ O livro diz que uma instância `FastAPI()` não roda duas rotas [Adeshina, p36]. Roda (a API da Aula 11
> servia sete). Router é **organização**.

---

## 5. Documentar: o `/docs` é o contrato

O TP4 pede *"documentação clara… [que] descreva como a integração local foi realizada"* — e quem for usar a
sua API (inclusive o seu painel) lê o `/docs`. Ele é gerado do código — o que ele **diz**, quem escreve é
você:

| Escreva… | …e o `/docs` mostra |
|----------|---------------------|
| `summary="Série anual de uma UF"` no decorador | o **título** (sem ele: o nome da função, tipo "Serie Da Uf") |
| a **docstring** da função | a **descrição** — o que faz, o que recebe, o que devolve |
| `description=` em `Query`/`Path`/`Field` | a explicação de **cada parâmetro** |
| `json_schema_extra` no modelo | o **exemplo** preenchido |
| `tags=` no router | o **grupo** |
| `FastAPI(title=, description=, version=)` | a **capa** |

E no **README** do projeto: *como rodar a API* (`uvicorn api.main:app --reload`) e *onde está a
documentação* (`http://127.0.0.1:8000/docs`), com uma tabela das rotas.

---

## 6. Integrar: o painel como cliente da API

```python
import requests

def enviar_relato(url, uf, categoria, texto):
    corpo = {"uf": uf, "categoria": categoria, "texto": texto}
    r = requests.post(f"{url}/relatos", json=corpo, timeout=10)     # json=, e não data=
    if r.status_code == 422:
        return False, [traduzir(e) for e in r.json()["detail"]]    # a API disse por quê
    r.raise_for_status()
    return True, r.json()["relato"]
```

| Decisão | Sem ela (medido) |
|---------|------------------|
| `json=`, não `data=` | `data=` manda um formulário → **422** *"Input should be a valid dictionary…"* |
| conferir o status antes de dizer "enviado" | a tela diz **"Relato enviado!"** a um envio recusado — nada é gravado |
| `timeout=` + tratar a API desligada | `ConnectionError` com o traceback na tela |
| o painel **não** grava no arquivo | a regra existiria em dois lugares — e um dia discordariam |

**Um dono para cada escrita:** o painel **pede**; a API **valida e grava**.

**Sem a API** (desligada, ou no Community Cloud — onde ela não roda): a página **avisa**, **desliga o envio** e
mostra **exemplos** — o plano B da Aula 2. O endereço da API é **configuração** (variável de ambiente ou
`.streamlit/secrets.toml`), não código.

---

## 7. O texto que o LLM do TP4 vai ler

Registre no Data Summary Report **que dado** você tem e **que tarefa** de LLM ele permite:

| Se você tem… | …um LLM poderia (Etapa 8) |
|--------------|---------------------------|
| texto curto enviado por pessoas (relatos, comentários, avaliações) | classificar (sentimento, categoria, urgência); resumir por grupo |
| texto longo coletado (notícias, relatórios) | resumir; responder perguntas sobre ele |
| números (séries, rankings) | gerar um parágrafo que os explique |

Melhor ainda se o dado já chega **por uma rota da sua API**: na Etapa 8, o LLM vira **mais uma rota** da
mesma aplicação (`POST /processar_texto`, no TP4).

---

## 8. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| corpo como `dict` | aceita tudo, inclusive `{}` |
| modelo sem `extra="forbid"` quando há risco de dado pessoal | descarta em silêncio — e quem envia acha que foi gravado |
| guardar na memória | some no primeiro reinício (o `--reload` reinicia a cada `.py` salvo) |
| abrir o arquivo em `"w"` | apaga o que já estava lá |
| gravar sem trava, com rotas `def` | números repetidos e envios perdidos |
| `data=` no lugar de `json=` | 422 com uma mensagem que não ajuda |
| dizer "enviado" sem conferir a resposta | o usuário acredita num envio que não aconteceu |
| chamar a API sem `timeout` nem plano B | traceback na tela; app travado |
| o app escrever no mesmo arquivo que a API | dois donos para a mesma regra |
| versionar o que pessoas enviaram | dado pessoal num repositório público |
| copiar `class Config: schema_extra` do livro | roda, avisa — e o exemplo some do `/docs` |

---

## 9. O TP4, depois desta aula

**O que esta aula já cobre:**

- [ ] **Item 2, a rota:** um **POST que recebe texto**, com o corpo validado por um modelo Pydantic (tipos,
      limites, `extra="forbid"`) — o desenho do `POST /processar_texto`, ainda sem o LLM atrás
- [ ] **Item 3, a entrada:** os dados **enviados** no formato correto — o 422 recusa o resto, com o motivo
- [ ] **Item 4, a experiência do usuário:** o painel mostra o 422 **traduzido** (*"feedback útil para o usuário
      final"*)
- [ ] a rota **documentada** (título, descrição, exemplo no `/docs`) e o painel **integrado** à API — e
      funcionando sem ela
- [ ] Git: **nada de dado pessoal** versionado

**O que vem:**

- [ ] **Etapa 7 — itens 3 e 4:** os dados **devolvidos** com formato declarado (*response models*) e os erros
      com exceções HTTP (404, 503)
- [ ] **Etapa 8 — itens 1 e 2:** o **modelo LLM local**, escolhido por desempenho, custo e acessibilidade,
      atrás da rota
- [ ] **Entrega:** `nome_sobrenome_PB_TP4.PDF` com o **link do repositório no GitHub** (calendário: semana de
      16–21/11)

---

## 10. Fontes

- **ADESHINA, A. A.** *Building Python Web APIs with FastAPI*. Packt, 2022 — cap. 2 (*Routing in FastAPI*:
  `APIRouter`, p36–38; validação com modelos, p40–43; *request body*, p47–48; exemplo no esquema, p51–54);
  cap. 5 (estrutura de projeto, p88–102). **[G2]** — páginas do PDF.
- Documentação oficial do FastAPI e do Pydantic 2 — corpo da requisição, `APIRouter`, `ConfigDict`,
  `extra="forbid"`, `json_schema_extra`. Verificados por execução (FastAPI 0.142, Pydantic 2.13, uvicorn
  0.52, Streamlit 1.61), em 06/10/2026.
- Lei nº 13.709/2018 (**LGPD**) — coletar só o necessário.
