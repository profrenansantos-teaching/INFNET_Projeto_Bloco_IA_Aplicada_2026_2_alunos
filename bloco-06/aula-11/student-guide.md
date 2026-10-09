# Aula 11 — Material de apoio do aluno
### Do outro lado da API · PB Etapa 6 · subcompetências 3.3 e 3.4

> Consulte enquanto faz o **item 4 do TP3** — *"crie uma API simples com rotas e endpoints que permitam
> interagir com os dados da aplicação… ao menos duas rotas… documente-as"*. Esta aula cobre o
> **ambiente** e as rotas de **consulta (GET)**; a Aula 12 cobre o **envio (POST)** e fecha o TP3.

---

## 1. Por que uma API, se o painel já mostra tudo?

O painel é para **pessoas**. Um **programa** que quisesse os seus dados teria de raspá-lo — e um app
Streamlit, para o `requests`, é uma **casca**:

```
requests.get("http://localhost:8501/desmatamento")
status 200 · 10.951 bytes · texto visível: "You need to enable JavaScript to run this app." · tabelas: 0
```

Seria o **degrau 4** da escada da Aula 10 (navegador pilotado). A API é o **degrau 1** que **você**
oferece: um endereço por pergunta, resposta em JSON, documentação gerada do próprio código.

| | Desde a Aula 2 | A partir de hoje |
|---|---|---|
| Papel | **consumidor** — o seu código pede | **provedor** — outro programa pede ao seu |
| Exemplo | `requests.get(URL_DO_IBGE)` | `@app.get("/desmatamento/{uf}")` |
| Documentação | você **lê** a do IBGE | você **escreve** a sua (o FastAPI a gera em `/docs`) |

---

## 2. O ambiente (subcompetência 3.3)

```bash
pip install fastapi uvicorn
```

| Pacote | Para quê |
|--------|----------|
| `fastapi` | o *framework*: rotas, validação pelos tipos, documentação automática |
| `uvicorn` | o **servidor** que roda a API — *"a module to run our application"* [Adeshina, p32] |

**No seu projeto, um terceiro arquivo de requisitos** — a mesma regra do `requirements-coleta.txt`:

```
requirements.txt          # o app — o que o Community Cloud instala. SEM fastapi.
requirements-api.txt      # -r requirements.txt
                          # fastapi>=0.115
                          # uvicorn>=0.30
```

> ⚠️ **Não copie as versões do livro** (`fastapi==0.78.0`, `uvicorn==0.17.6` [Adeshina, p194]). Elas
> trazem Starlette 0.19 e Pydantic 1 — e o Streamlit atual exige Starlette ≥ 0.46. No mesmo ambiente, a
> API quebraria o painel.

---

## 3. A menor API — e como rodá-la

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")                     # o decorador: qual pedido esta função atende (GET em "/")
def ola():                        # o handler
    return {"mensagem": "Olá!"}   # o dicionário vira JSON
```

```bash
uvicorn main:app --reload
```

| Pedaço | Significa |
|--------|-----------|
| `main` | o **módulo** (o arquivo, sem `.py`) |
| `:app` | a **variável** que guarda a aplicação (*"file:instance"* [Adeshina, p33]) |
| `--reload` | reinicia a cada `.py` salvo — só para desenvolver, e num **terminal de verdade** |
| (padrão) | porta **8000**, endereço **127.0.0.1** |

Abra **http://127.0.0.1:8000/** (o JSON), **/docs** (a documentação interativa) e **/redoc**.

**No projeto**, com a API numa pasta `api/` que importa `src/`: rode **da pasta do projeto**:

```bash
uvicorn api.main:app --reload          # "no pacote api, o módulo main, a variável app"
```

> ⚠️ **`python main.py` não sobe nada.** O arquivo só *define* a aplicação; quem a *serve* é o
> `uvicorn`. É como o app: ele não roda com `python app.py`, roda com `streamlit run`.

---

## 4. Quando a API não sobe

| Sintoma | Causa | Correção |
|---------|-------|----------|
| `python arquivo.py` termina calado | o Python não é servidor | `uvicorn arquivo:app --reload` |
| `Error loading ASGI app. Could not import module "main"` | rodou o `uvicorn` de outra pasta | `cd` para a pasta do arquivo |
| `ModuleNotFoundError: No module named 'src'` | rodou de **dentro** de `api/` | rode da pasta do projeto: `uvicorn api.main:app` |
| `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)` | já há um servidor na porta (às vezes um **processo órfão** de uma janela fechada "no X") | **Ctrl+C** no terminal antigo; se não houver: `netstat -ano \| findstr :8000` e `taskkill /PID <número> /F` |
| `/docs` em branco | o **navegador** está sem internet (a página baixa o Swagger de `cdn.jsdelivr.net`) | a API está bem: teste pela URL da rota, ou com o `requests` |
| `"olá"` aparece como `"olÃ¡"` | no **Windows PowerShell 5.1**, `curl` é um apelido do `Invoke-WebRequest` | use **`curl.exe`**, o navegador, o `/docs` ou o `requests` |

> **Pare o servidor com Ctrl+C**, sempre. E não use `http://0.0.0.0:8000` como endereço (o livro usa,
> no Unix [Adeshina, p33]): no Windows, `0.0.0.0` não é destino válido. Use `127.0.0.1` ou `localhost`.

---

## 5. Rotas que respondem (subcompetência 3.4)

### Caminho e consulta

```python
from typing import Literal
from fastapi import FastAPI, Path, Query

UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]

@app.get("/desmatamento/{uf}")                              # {uf}: vem do CAMINHO
def serie_da_uf(uf: UfAmazonia,                             # o tipo restringe às 9 UFs
                desde: int = Query(1988, ge=1988),          # o resto: vem da CONSULTA
                ate: int | None = None):
    ...

# GET /desmatamento/PA?desde=2020&ate=2024
```

| Vai no… | Quando | Exemplo |
|---------|--------|---------|
| **caminho** | **identifica** o recurso — o QUE você quer | `/desmatamento/PA` · `/desmatamento/ranking/2024` |
| **consulta** | **recorta** a resposta — o COMO você quer | `?desde=2020&ate=2024` · `?limite=5` |

> ⚠️ Parâmetro de consulta só é **opcional** se tiver **valor padrão**. `def f(secao: str)` sem
> `?secao=` → **422 "Field required"**. Opcional: `secao: str | None = None`. *(O livro diz que todo
> parâmetro de consulta é "optional" [Adeshina, p47] — não é.)*

### O tipo é a guarda

**Tudo o que chega numa URL é texto.** Quem converte para o tipo declarado — e recusa o que não converte,
**antes** de a sua função rodar — é o FastAPI:

| Pedido | `def ranking(ano):` (sem tipo) | `def ranking(ano: int = Path(ge=1988)):` |
|--------|:------------------------------:|:----------------------------------------:|
| `/ranking/2024` | **200 · lista vazia** (`"2024"` ≠ `2024`) | 200 · 9 UFs |
| `/ranking/abc` | 200 · lista vazia | **422** · *"Input should be a valid integer"* |
| `/ranking/1950` | 200 · lista vazia | **422** · *"greater than or equal to 1988"* |

Sem tipo, a API **engana** (200 vazio). Com tipo, ela **quebra** (422, com o motivo). Prefira o que
quebra. E um `Literal` vira um **menu** no `/docs`.

Validações numéricas em `Path(...)` e `Query(...)`: `ge` (≥), `gt` (>), `le` (≤), `lt` (<). *(O livro
diz que `le` é "less than" [Adeshina, p47] — é "menor **ou igual**".)*

### A ordem das rotas

O FastAPI testa as rotas **na ordem em que foram declaradas**. `/desmatamento/{uf}` casa com qualquer
palavra — inclusive `total`:

```python
@app.get("/desmatamento/total")      # ✅ o caminho FIXO primeiro
def total(): ...

@app.get("/desmatamento/{uf}")       # depois, o caminho com parâmetro
def serie_da_uf(uf: UfAmazonia): ...
```

Na ordem inversa, `GET /desmatamento/total` → **422** (`"input": "total"`).

> **IA como copiloto.** Pedir a uma IA "as rotas GET da minha API" funciona — e o código pode vir
> **sem tipo** nos parâmetros, com `async def` e com as rotas na ordem em que você as pediu. Use o que veio,
> mas confira os três pontos desta seção: **tipos**, **ordem** e **`def`**. Você precisa saber explicar
> cada um — inclusive por que a IA errou.

---

## 6. `def`, não `async def`

O livro escreve todas as rotas com `async def` [Adeshina, p32]. **Use `def`.** Medido com uma rota que
faz um trabalho que bloqueia por 2 s (ler arquivo, chamar o `requests`): **4 pedidos ao mesmo tempo**
levaram **8,0 s** com `async def` e **2,0 s** com `def` — o FastAPI roda as rotas `def` em paralelo.
`async def` só ajuda quando tudo lá dentro é assíncrono (`await`).

---

## 7. Testar a sua API

**Pelo `/docs`:** abra a rota → **Try it out** → preencha → **Execute**. Ele mostra a URL montada, o
`curl` equivalente e a resposta.

**Por um programa** — o código da Aula 2, apontado para a sua API:

```python
import requests

r = requests.get("http://127.0.0.1:8000/desmatamento/PA", params={"desde": 2020}, timeout=10)
r.raise_for_status()
for linha in r.json()["dados"]:
    print(linha["ano"], linha["area_km2"])
```

**Um 422 não é mistério:** o `detail` diz **onde** e **por quê**.

```json
{"detail": [{"type": "greater_than_equal", "loc": ["query", "desde"],
             "msg": "Input should be greater than or equal to 1988", "input": "1950"}]}
```

---

## 8. A licença viaja com o dado

Se os seus dados têm licença (CC BY, CC BY-SA…), **a resposta da API deve dizer qual**. Quem recebe uma
lista de números solta não tem como saber que deve citar — ou compartilhar igual. Um envelope resolve:

```json
{"fonte": "INPE/PRODES — TerraBrasilis",
 "licenca": "CC BY-SA 4.0",
 "coletado_em": "01/10/2026 21:50",
 "linhas": 3,
 "dados": [ ... ]}
```

E faça a API ler os dados **com as mesmas funções** que o painel usa (`src/`). Duas leituras diferentes
um dia mostram números diferentes.

> **E "não encontrado"?** Na Etapa 6, um pedido sem resultado responde **200** com uma lista vazia — é o
> que o capítulo 2 do livro faz [Adeshina, p45]. Responder **404** é a **Etapa 7**.

---

## 9. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| rota sem tipo | 200 e lista vazia — quem consome conclui que não há dados |
| caminho com parâmetro antes do caminho fixo | a rota fixa nunca é alcançada |
| `async def` com trabalho que bloqueia | os pedidos entram em fila (8,0 s × 2,0 s) |
| copiar as versões do livro | Starlette e Pydantic antigos quebram o Streamlit |
| `fastapi` no `requirements.txt` de um app que não o importa | peso morto no *build* do Community Cloud |
| resposta de dados sem a licença | quem reutiliza não sabe que deve citar |
| a API lendo os dados do seu próprio jeito | painel e API mostrando números diferentes |
| `curl` do PowerShell 5.1 como prova de "problema de acento" | o problema é do leitor, não da API |

---

## 10. Checklist do item 4 do TP3 — a parte de hoje

- [ ] `requirements-api.txt` (ou equivalente) com `fastapi` e `uvicorn` — **fora** do `requirements.txt`
      do app, se o app não importa o FastAPI
- [ ] A API numa pasta própria (ex.: `api/main.py`), lendo os dados **com as mesmas funções** do app
- [ ] Sobe com `uvicorn api.main:app --reload` **da pasta do projeto**; `/docs` abre
- [ ] **Ao menos uma rota GET** que consulta os dados do seu projeto — com **tipos** nos parâmetros
- [ ] Caminho × consulta decididos (o QUE no caminho; o COMO na consulta); rotas fixas antes das com
      parâmetro
- [ ] Cada rota com uma **docstring** que diz o que ela responde (vira a descrição no `/docs`)
- [ ] Testada pelo `/docs` **e** por um script `requests`
- [ ] *(Aula 12)* a rota de **envio (POST)**, com validação — e o README explicando como usar a API

---

## 11. Fontes

- **ADESHINA, A. A.** *Building Python Web APIs with FastAPI*. Packt, 2022 — cap. 1 (*Getting Started
  with FastAPI*, p20–33); cap. 2 (*Routing in FastAPI*, p34–59: parâmetros de caminho, p44–47; de
  consulta, p47; documentação automática, p48–53). **[G1, G2]** — páginas do PDF.
- Documentação oficial do FastAPI — parâmetros de caminho e de consulta, validações numéricas, *async*.
  Verificados por execução (FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Python 3.13), em 06/10/2026.
- INPE. **PRODES — TerraBrasilis**, CC BY-SA 4.0 · Agência Brasil (EBC), CC BY 3.0 BR.
