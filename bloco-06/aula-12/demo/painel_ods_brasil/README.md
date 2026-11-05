# Painel de Indicadores Sustentáveis do Brasil — v10

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 12 · PB Etapa 6**.

Painel ESG/ODS em **Python puro** (sem pandas). Na v9 o projeto ganhou uma **API** (FastAPI) que serve os
dados a outros programas. Na **v10**, a API passa a **receber**: `POST /relatos`, com o corpo
**validado por um modelo Pydantic** — e o painel ganha a página **🗣️ Relatos de campo**, que **envia** cada
relato à API e lista os que chegaram. As rotas foram organizadas em **routers**, uma por assunto, e
cada uma ganhou título e descrição no `/docs`. **A v10 é a base do TP4:** o `POST /relatos` tem o desenho do
`POST /processar_texto` (uma rota que recebe texto validado) — falta o LLM atrás dela (Etapa 8), e as respostas
e os erros com formato declarado (Etapa 7).

## Três ambientes, três arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |
| **servir a API** (só na sua máquina) | `pip install -r requirements-api.txt` | tudo acima do app **+ fastapi + uvicorn** |

> O app fala com a API **pelo `requests`**, que já estava no `requirements.txt`. Nenhuma dependência nova
> na v10.

## Rodar localmente — dois terminais

| Terminal 1 — o **painel** (pessoas) | Terminal 2 — a **API** (programas) |
|---|---|
| `streamlit run app.py` | `uvicorn api.main:app --reload` |
| http://localhost:8501 → **🗣️ Relatos de campo** | http://127.0.0.1:8000/docs |

Os dois **da pasta `painel_ods_brasil/`**. Com a API no ar, a página Relatos **envia** e **lista**; sem ela
(ou no Community Cloud), **avisa**, desliga o envio e mostra **exemplos fictícios**.

## A API (v10)

| Método e rota | Recebe | Responde |
|---------------|--------|----------|
| `GET /` · `GET /fontes` | — | o que a API serve · procedência e licença de cada conjunto |
| `GET /desmatamento` · `/total` · `/ranking/{ano}` · `/{uf}` | caminho e consulta tipados (v9) | dados do PRODES/INPE, com fonte e licença |
| `GET /noticias` | `?secao=&limite=` | as notícias da última coleta |
| **`POST /relatos`** | corpo JSON `{uf, categoria, texto}` — validado pelo modelo **Relato** | `{"mensagem": "Relato recebido.", "relato": {id, recebido_em, uf, categoria, texto}}` |
| **`GET /relatos`** | `?uf=&categoria=&limite=20` | os relatos recebidos, do mais recente ao mais antigo |

**O que o `POST /relatos` aceita** (`api/modelos.py`):

| Campo | Regra | Se não cumprir |
|-------|-------|----------------|
| `uf` | uma das 27 siglas | 422 · `literal_error` |
| `categoria` | `queimada` · `desmatamento` · `enchente` · `seca` · `poluicao` · `lixo` · `outro` | 422 · `literal_error` |
| `texto` | 15 a 500 caracteres, sem contar os espaços das pontas | 422 · `string_too_short` / `string_too_long` |
| **qualquer outro campo** (`nome`, `telefone`…) | **recusado** — a API não guarda dado pessoal | 422 · `extra_forbidden` |

Todos os problemas de um envio voltam **juntos**, no mesmo 422:

```json
{"detail": [
  {"type": "literal_error",    "loc": ["body", "uf"],        "msg": "Input should be 'AC', 'AL', …"},
  {"type": "literal_error",    "loc": ["body", "categoria"], "msg": "Input should be 'queimada', …"},
  {"type": "string_too_short", "loc": ["body", "texto"],     "msg": "String should have at least 15 characters"}]}
```

**Enviar de outro programa** — o mesmo `requests` da Aula 2, agora com `post` e **`json=`**:

```python
import requests
r = requests.post("http://127.0.0.1:8000/relatos",
                  json={"uf": "PA", "categoria": "queimada", "texto": "Fumaça densa na beira da estrada desde cedo."},
                  timeout=10)
print(r.status_code, r.json())
```

> ⚠️ **`json=`, não `data=`.** Com `data=`, o `requests` manda um formulário, e a API responde 422 com uma
> mensagem que não ajuda: *"Input should be a valid dictionary or object to extract fields from"*.

## O que mudou da v9 para a v10

| # | Mudança | Onde | Por quê |
|---|---------|------|---------|
| 1 | **`POST /relatos`** + `GET /relatos` | `api/rotas/relatos.py` | a API passa a receber — o desenho do `POST /processar_texto` do TP4 |
| 2 | Corpo validado por **modelo Pydantic** (e não `dict`) | `api/modelos.py` | com `dict`, `{"uf": 123}` e `{}` voltavam 200 |
| 3 | **`extra="forbid"`** | `api/modelos.py` | sem ele, `nome` e `telefone` eram descartados em silêncio — e quem enviou achou que foram gravados (🐛) |
| 4 | Relatos num **CSV**, com **trava** | `src/relatos.py` | na memória, o `--reload` os apagava (🐛); sem trava, 40 envios simultâneos → 9 números distintos |
| 5 | Rotas em **routers** (`APIRouter`, `prefix`, `tags`) | `api/rotas/*.py` · `api/main.py` | um assunto, um arquivo — o `main.py` virou roteador, como o `app.py` da Aula 9 |
| 6 | **Títulos** (`summary=`) e exemplo no `/docs` | rotas · `model_config` | na v9, o `/docs` dizia "Serie Da Uf"; o `schema_extra` do livro **some** no Pydantic 2 |
| 7 | Página **🗣️ Relatos de campo** | `paginas/relatos.py` · `src/cliente_api.py` | o painel **envia** à API (não grava): um dono para cada escrita |
| 8 | Charter e Data Summary revisados (+ **preparação para LLMs**) | `docs/` | a Fonte 5, a privacidade e o texto que o LLM do TP4 vai ler |

## Estrutura

```
painel_ods_brasil/
├── app.py                    ROTEADOR do painel — + a página Relatos no menu              ← 1 linha
├── paginas/relatos.py        🗣️ envia à API, lista o que chegou; sem a API, exemplos         ← novo
├── src/
│   ├── relatos.py            GUARDA e LÊ os relatos (CSV, com trava)                        ← novo
│   ├── cliente_api.py        o painel como CLIENTE da API (requests, json=, timeout)        ← novo
│   └── …                     (as leituras de sempre — o painel e a API as usam)
├── api/
│   ├── main.py               ROTEADOR da API: cria o app e inclui os routers                ← refeito
│   ├── modelos.py            o que a API ACEITA (Pydantic)                                  ← novo
│   └── rotas/                desmatamento.py · noticias.py · relatos.py (um APIRouter cada)  ← novo
├── data/relatos/             relatos.csv — o que chegou (NÃO versionado)
├── data/sample/              relatos_exemplo.csv — 5 exemplos FICTÍCIOS (versionado)
└── requirements-api.txt      (o mesmo da v9)
```

## Publicar

```bash
git add .
git commit -m "v10: a API recebe relatos (POST validado com Pydantic), routers, e a página Relatos"
git push
```

`data/relatos/` não sobe (`.gitignore`). No Community Cloud, a página Relatos abre com o envio desligado e
os exemplos — ver `DEPLOY.md` §12.

## Verificação

Confirmado em 06/10/2026 — FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Streamlit 1.61, Python 3.13
(Windows): servidor real (`uvicorn` num terminal) + `requests`; `TestClient`; `AppTest` com a API ligada e
desligada; Chrome *headless* sobre o app e o `/docs`.

| Afirmação | Verificação |
|---|---|
| As 8 rotas respondem | `GET /desmatamento` 342 linhas · `/total` 38 · `/PA?desde=2023` 3 · `ranking/2025` 9 · `/noticias?limite=2` 2 |
| O POST grava e devolve o relato | `{"mensagem": "Relato recebido.", "relato": {"id": 1, …}}`; o CSV tem a linha |
| Três erros, um 422 | `{"uf": "Pará", "categoria": "fogo", "texto": "curto"}` → `literal_error` · `literal_error` · `string_too_short` |
| Campos extras são recusados | `nome` + `telefone` → 422 · `extra_forbidden` (sem `forbid`: 200, descartados) |
| Espaços não contam | 20 espaços → 422 `string_too_short`; `"   Fumaça… cedo.   "` → gravado sem os espaços |
| `data=` em vez de `json=` | 422 · `model_attributes_type` |
| A trava funciona | 40 POSTs simultâneos: **40** números distintos, 0,8 s (sem a trava: 9 distintos; 120 envios → 117 gravados) |
| Filtros | `?uf=AM` 1 · `?categoria=queimada&limite=1` 1 · `?uf=XX` 422 |
| Títulos e exemplo no `/docs` | `summary` em todas as rotas; `Relato` com `examples` e `additionalProperties: false` |
| A página com a API no ar | 3 envios → *"Relato nº 1 recebido…"*; texto curto → *"O texto precisa ter pelo menos 15 caracteres."*; a lista atualiza; filtro por UF |
| A página sem a API | aviso + formulário desligado + 5 exemplos, zero exceções |
| As oito páginas, pelo link direto | `AppTest`: zero exceções |
