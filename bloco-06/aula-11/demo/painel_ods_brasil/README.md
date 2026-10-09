# Painel de Indicadores Sustentáveis do Brasil — v9

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 11 · PB Etapa 6**.

Painel ESG/ODS em **Python puro** (sem pandas). Esta versão (**v9**) dá ao projeto uma **API própria**,
com **FastAPI**: os mesmos dados que o painel mostra a pessoas, agora em JSON, para **outros
programas** — um endereço por pergunta, com documentação gerada do próprio código.

**Por quê:** para o `requests`, o nosso painel é uma **casca** — `status 200`, *"You need to enable
JavaScript to run this app."*, nenhuma tabela. Quem quisesse os números teria de pilotar um navegador
(o degrau 4 da escada da Aula 10). A API é o **degrau 1** que nós oferecemos.

## Três ambientes, três arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |
| **servir a API** (só na sua máquina) | `pip install -r requirements-api.txt` | tudo acima do app **+ fastapi + uvicorn** |

> O app **não importa** o FastAPI: no `requirements.txt` ele seria peso morto no *build* do Community
> Cloud. *O que se importa, se declara* (Aula 5) — **no arquivo do ambiente que importa**. A mesma
> regra que pôs o Selenium em `requirements-coleta.txt`.

## Rodar localmente — dois terminais

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1                 # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements-api.txt        # app + API (para coletar, requirements-coleta.txt)
```

| Terminal 1 — o **painel** (pessoas) | Terminal 2 — a **API** (programas) |
|---|---|
| `streamlit run app.py` | `uvicorn api.main:app --reload` |
| http://localhost:8501 | http://127.0.0.1:8000/docs |

Os dois comandos rodam **da pasta `painel_ods_brasil/`**. Os dois leem os mesmos arquivos de
`data/processed/`, com as mesmas funções de `src/` — uma leitura, dois clientes.

> ⚠️ **`python api/main.py` não sobe nada.** O arquivo só *define* a aplicação; quem a serve é o
> `uvicorn`. E rodar o `uvicorn` de dentro de `api/` dá `ModuleNotFoundError: No module named 'src'`:
> o ponto de partida é a pasta do projeto.

## A API (v9)

| Rota (GET) | Parâmetros | Responde |
|------------|------------|----------|
| `/` | — | o que a API serve e onde está a documentação |
| `/fontes` | — | procedência, data da coleta e licença de cada conjunto |
| `/desmatamento` | `?desde=1988&ate=` | a taxa anual de todas as UFs, no período |
| `/desmatamento/total` | `?desde=&ate=` | a soma das 9 UFs por ano (a Amazônia Legal) |
| `/desmatamento/ranking/{ano}` | `ano` inteiro ≥ 1988 | as UFs no ano, da que mais à que menos desmatou |
| `/desmatamento/{uf}` | `uf` ∈ 9 UFs · `?desde=&ate=` | a série de uma UF |
| `/noticias` | `?secao=&limite=10` (1–50) | as notícias da última coleta |

Toda rota de dados responde um **envelope** — a licença viaja com o dado:

```json
{"fonte": "INPE/PRODES — TerraBrasilis",
 "licenca": "Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)",
 "coletado_em": "01/10/2026 21:50",
 "linhas": 3,
 "dados": [{"uf": "PA", "estado": "Pará", "ano": 2023, "area_km2": 3299.0, "fonte": "…"}, …]}
```

**Consumir de outro programa** — é o código da Aula 2, apontado para a nossa API:

```python
import requests
r = requests.get("http://127.0.0.1:8000/desmatamento/PA", params={"desde": 2020}, timeout=10)
r.raise_for_status()
for linha in r.json()["dados"]:
    print(linha["ano"], linha["area_km2"])
```

> **No Windows PowerShell 5.1, `curl` não é o curl:** é um apelido do `Invoke-WebRequest`, e ele mostra
> `"olá"` como `"olÃ¡"`. Use **`curl.exe`**, o navegador, o `/docs` ou o `requests`.

## O que mudou da v8 para a v9

| # | Mudança | Onde | Por quê |
|---|---------|------|---------|
| 1 | **API** com 7 rotas GET | `api/main.py` | outros programas sem raspar o painel |
| 2 | **Tipos** nos parâmetros (`ano: int`, `uf` ∈ 9 UFs) | `api/main.py` | sem o tipo, `ranking/2024` respondia **200 e lista vazia** (🐛) |
| 3 | `/desmatamento/total` **antes** de `/desmatamento/{uf}` | `api/main.py` | na ordem inversa, "total" virava UF e dava **422** (🐛) |
| 4 | **Envelope** com `fonte`/`licenca`/`coletado_em` | `api/main.py` | CC BY-SA: a licença tem de acompanhar o dado |
| 5 | `requirements-api.txt` | raiz | o ambiente da API ≠ o ambiente do app |
| 6 | A API na página **ℹ️ Dados e método** e no rodapé | `paginas/sobre.py` · `app.py` | quem usa o painel fica sabendo que ela existe |
| 7 | Charter e Data Summary revisados | `docs/` | item 1 do TP3: o problema "à luz das novas ferramentas" |

## Estrutura

```
painel_ods_brasil/
├── app.py                    ROTEADOR do painel — só o rodapé muda
├── comum.py · paginas/       (as sete páginas da v8; Dados e método cita a API)
├── src/                      DADOS + LÓGICA — o painel E a API usam estas funções
├── api/
│   ├── __init__.py
│   └── main.py               a API: 7 rotas GET sobre data/processed/               ← novo
├── data/processed/           os CSVs que a coleta grava (VERSIONADOS) — o painel e a API leem daqui
├── requirements.txt          o app (e o Community Cloud)
├── requirements-coleta.txt   a coleta (+ selenium)
└── requirements-api.txt      a API (+ fastapi, uvicorn)                              ← novo
```

## Publicar

```bash
git add .
git commit -m "v9: API do projeto com FastAPI (7 rotas GET, documentadas em /docs)"
git push
```

O app publicado continua o mesmo; a pasta `api/` sobe junto, mas o Community Cloud não a roda (ver
`DEPLOY.md` §11). O rodapé da barra lateral mostra `v9 — Aula 11 (a API do projeto, com FastAPI)`.

## Verificação

Confirmado em 06/10/2026 — FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Python 3.13 (Windows), com o
servidor real (`uvicorn` num terminal) + `requests`, e o Chrome *headless* sobre o `/docs`:

| Afirmação | Verificação |
|---|---|
| O painel é uma casca para o `requests` | `GET /desmatamento` do app Streamlit: 200 · 10.951 bytes · *"You need to enable JavaScript to run this app."* · 0 tabelas |
| A API sobe da pasta do projeto | `uvicorn api.main:app` → no ar em ~3 s; de dentro de `api/` → `ModuleNotFoundError: No module named 'src'` |
| `python api/main.py` não sobe servidor | sai com código 0, sem mensagem, depois de importar o FastAPI |
| As 7 rotas respondem | `GET /desmatamento/PA?desde=2020` → 200 · 6 linhas · ~25 ms |
| Os números batem com a coleta | total 2004 = 27.772 km² · 2025 = 5.731 km² · ranking 2025: PA 2.064, MT 1.593, AM 979 … |
| Tipos recusam o que não serve | `ranking/abc` e `ranking/1950` → 422 · `/desmatamento/ZZ` e `/desmatamento/pa` → 422 com as 9 UFs válidas · `noticias?limite=0` → 422 |
| 🐛 Sem o tipo, a rota "funciona" vazia | `def ranking(ano):` → `ranking/2024` = **200, `"linhas": 0`** |
| 🐛 A ordem das rotas importa | `{uf}` antes de `total` → `GET /desmatamento/total` = **422**, `"input": "total"` |
| O `/docs` lista as rotas e executa pedidos | 7 rotas em 3 grupos; a UF vira um **menu com 9 opções**; *Try it out* → `…/desmatamento/PA?desde=2023` → 200 |
| O `/docs` precisa de internet no **navegador** | ele carrega o Swagger de `cdn.jsdelivr.net`: com o acesso externo bloqueado, a página fica **em branco** — e a API continua respondendo |
| O painel continua igual | `AppTest`: as sete páginas, pelo link direto de cada uma, zero exceções |
