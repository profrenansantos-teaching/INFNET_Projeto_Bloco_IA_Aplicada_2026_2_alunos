# Painel de Indicadores Sustentáveis do Brasil — v11

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 13 · PB Etapa 7**.

Painel ESG/ODS em **Python puro** (sem pandas). Na v9 o projeto ganhou uma **API** (FastAPI); na v10, a API
passou a **receber** relatos. Na **v11**, a API passa a **declarar o que devolve**: toda rota tem um
**modelo de resposta** (`response_model`), e o `/docs` deixa de mostrar `"string"` e mostra os campos. E chega
a rota que o TP4 pede — **`POST /processar_texto`** —, que recebe um texto e devolve a análise num formato
declarado. O motor da análise é **provisório** (regras de palavras-chave); o **formato**, não: na Etapa 8 um
LLM local entra atrás da mesma rota. O painel ganha a página **🔎 Analisador de relatos**, que a usa.

## Três ambientes, três arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |
| **servir a API** (só na sua máquina) | `pip install -r requirements-api.txt` | tudo acima do app **+ fastapi + uvicorn** |

> **Nenhuma dependência nova na v11.** Os modelos de resposta são Pydantic (que vem com o FastAPI); o
> analisador é Python puro (`re` + `json`).

## Rodar localmente — dois terminais

| Terminal 1 — o **painel** (pessoas) | Terminal 2 — a **API** (programas) |
|---|---|
| `streamlit run app.py` | `uvicorn api.main:app --reload` |
| http://localhost:8501 → **🗣️ Relatos** e **🔎 Analisador** | http://127.0.0.1:8000/docs |

Os dois **da pasta `painel_ods_brasil/`**. Sem a API (ou no Community Cloud), as páginas Relatos e Analisador
**avisam** em vez de quebrar.

## A API (v11)

| Método e rota | Recebe | Responde (modelo) | Status |
|---------------|--------|-------------------|:------:|
| `GET /` · `GET /fontes` | — | `Apresentacao` · lista de `Fonte` | 200 |
| `GET /desmatamento` · `/{uf}` | consulta `desde`, `ate` | `RespostaDesmatamento` | 200 |
| `GET /desmatamento/total` | consulta `desde`, `ate` | `RespostaTotais` | 200 |
| `GET /desmatamento/ranking/{ano}` | caminho `ano` | `RespostaRanking` | 200 |
| `GET /noticias` | `?secao=&limite=` | `RespostaNoticias` | 200 |
| `GET /relatos` | `?uf=&categoria=&limite=20` | `RespostaRelatos` | 200 |
| **`POST /relatos`** | `{uf, categoria, texto}` (modelo `Relato`) | `RelatoRecebido` | **201** |
| **`POST /processar_texto`** | `{texto, tipo_analise}` (modelo `PedidoAnalise`) | **`ResultadoAnalise`** | 200 |

Os modelos estão em `api/respostas.py` (o que **sai**) e `api/modelos.py` (o que **entra**) — e no fim do
`/docs`, em *Schemas*.

### A rota do TP4: `POST /processar_texto`

```python
import requests
r = requests.post("http://127.0.0.1:8000/processar_texto",
                  json={"texto": "O nível do rio baixou tanto que o barco não chega mais ao porto."},
                  timeout=30)
print(r.status_code, r.json())
```

```json
200
{"tipo_analise": "classificacao",
 "texto": "O nível do rio baixou tanto que o barco não chega mais ao porto.",
 "categoria_sugerida": "seca",
 "confianca": 1.0,
 "pistas": ["nível do rio", "baixou"],
 "motor": "regras-v1 (palavras-chave)"}
```

| Campo | O que é | Pedido pelo TP4 (item 3) |
|-------|---------|--------------------------|
| `tipo_analise` | a análise feita (hoje, só `classificacao`) | *"o tipo de análise realizada"* |
| `texto` | o texto analisado (sem os espaços das pontas) | *"o texto processado"* |
| `categoria_sugerida` · `confianca` · `pistas` | o resultado — `null`, `0.0` e `[]` se o motor não achar pista | *"os resultados gerados"* |
| `motor` | quem analisou: hoje, regras; na Etapa 8, o nome do modelo LLM | — |

**O motor é provisório — e tem limite visível.** Nos 5 relatos de exemplo, acerta 4; no quarto (*"A água do
arroio subiu… alcançou as casas"* — uma enchente) não acha nenhuma palavra da lista e devolve
`categoria_sugerida: null`. Uma lista de palavras não entende o sentido; um modelo de linguagem, sim. É a
Etapa 8. As regras ficam em `data/analisador/regras.json` (editável).

## O que mudou da v10 para a v11

| # | Mudança | Onde | Por quê |
|---|---------|------|---------|
| 1 | **`response_model=`** em todas as rotas | `api/respostas.py` · `api/rotas/*.py` · `api/main.py` | na v10, o `/docs` mostrava `"string"` como resposta das **9** rotas |
| 2 | Linhas sem a coluna `fonte` repetida | `LinhaDesmatamento`, `Noticia` | o envelope já diz a fonte; `/desmatamento`: **34.311 → 20.631 bytes** |
| 3 | `/fontes` com **um** formato (`Fonte`) | `api/main.py` | na v10, três formatos numa lista (11, 6 e 3 campos) |
| 4 | **Entrada ≠ saída**: `Relato` entra, `RelatoGravado` sai | `api/respostas.py` | usar o modelo de entrada (com `forbid`) na resposta derrubou o `GET /relatos` — **500** (🐛) |
| 5 | `publicado_em` é **texto** (`dd/mm/aaaa hh:mm`) | `Noticia` | declarado como `datetime`, derrubou a rota `/noticias` inteira — **500** (🐛) |
| 6 | `POST /relatos` responde **201** | `api/rotas/relatos.py` | criou algo; e um cliente que conferia `== 200` passou a dizer "falhou" a relatos gravados (🐛) |
| 7 | **`POST /processar_texto`** + o analisador provisório | `api/rotas/analise.py` · `src/analisador.py` · `data/analisador/` | a rota do TP4, com o contrato pronto antes do LLM |
| 8 | Página **🔎 Analisador de relatos** | `paginas/analisador.py` · `src/cliente_api.py` | o painel pede a análise e mostra só os campos do contrato |
| 9 | Mensagens do 422 com o limite que a **API** informou | `src/cliente_api.py` (`traduzir`) | o relato aceita 500 caracteres; a análise, 2.000 — o painel não repete a regra |

## Estrutura

```
painel_ods_brasil/
├── app.py                    ROTEADOR do painel — + a página Analisador no menu            ← 1 linha
├── paginas/analisador.py     🔎 pede a análise à API e mostra o resultado                   ← novo
├── src/
│   ├── analisador.py         o MOTOR provisório (regras de palavras-chave)                  ← novo
│   ├── cliente_api.py        + analisar_texto(); traduzir() lê o limite do 422
│   └── …
├── api/
│   ├── main.py               ROTEADOR da API: + o router de análise; /  e /fontes com modelo
│   ├── modelos.py            o que a API ACEITA (+ PedidoAnalise)
│   ├── respostas.py          o que a API DEVOLVE (response models)                          ← novo
│   └── rotas/                desmatamento · noticias · relatos · analise (novo)
└── data/analisador/          regras.json — as palavras de cada categoria (versionado)       ← novo
```

## Publicar

```bash
git add .
git commit -m "v11: response models em todas as rotas, POST /processar_texto e a página Analisador"
git push
```

No Community Cloud, a página Analisador abre com um aviso: o analisador mora na API, que roda na sua máquina
(`DEPLOY.md` §13).

## Verificação

Confirmado em 27/10/2026 — FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Streamlit 1.61, Python 3.13
(Windows): servidor real (`uvicorn` num terminal) + `requests`; `TestClient`; `AppTest` com a API ligada e
desligada.

| Afirmação | Verificação |
|---|---|
| Toda rota tem formato declarado | `/openapi.json`: v10, 9 de 9 respostas sem esquema (`"string"` no `/docs`); v11, nenhuma |
| O modelo filtra | `/desmatamento`: 342 linhas sem `fonte` — 34.311 → 20.631 bytes; `/fontes`: 11 · 6 · 3 campos → 5 · 5 · 5 |
| Modelo de entrada na resposta | `GET /relatos` → **500** · `ResponseValidationError` · `extra_forbidden` em `('response', 'dados', 0, 'id')` |
| `datetime` para `"02/09/2026 08:16"` | `GET /noticias` → **500** · `datetime_from_date_parsing` · *"invalid character in year"* |
| O 500 que o cliente vê | `text/plain` · *"Internal Server Error"* — o detalhe fica no terminal |
| `POST /relatos` | **201 Created** (no log do `uvicorn`); o painel continua dizendo *"Relato nº 1 recebido…"* |
| `POST /processar_texto` | 200 + os seis campos; texto curto → 422; `tipo_analise: "resumo"` → 422 `literal_error`; campo extra → 422 `extra_forbidden` |
| O analisador nos 5 exemplos | 4 acertos; o relato da enchente ("arroio subiu") → `categoria_sugerida: null` |
| As nove páginas, pelo link direto | `AppTest`, API desligada: zero exceções; Relatos e Analisador avisam |
| Página Analisador com a API | relato nº 1 → *queimada · 100%*; "arroio subiu" → *sem pista* + aviso; "curto" → *"O texto precisa ter pelo menos 15 caracteres."* |
