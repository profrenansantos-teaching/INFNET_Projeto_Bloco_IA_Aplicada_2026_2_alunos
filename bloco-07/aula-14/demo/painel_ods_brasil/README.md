# Painel de Indicadores Sustentáveis do Brasil — v12

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 14 · PB Etapa 7**.

Painel ESG/ODS em **Python puro** (sem pandas), com uma **API** própria (FastAPI). Na v11, a API passou a
declarar **o que devolve** (modelos de resposta) e ganhou a rota do TP4, **`POST /processar_texto`**. Na
**v12**, ela passa a dizer **o que deu errado** — com o status certo e uma frase: **404** quando o que se pediu
não existe, **409** quando o pedido conflita com o que já existe, **503** quando falta algo no servidor (o motor
de análise não carregou), e um **500 em JSON, com código**, para o que ninguém previu. O painel passa a ler as
respostas **pelo status** e mostra ao usuário o que a API disse, no tom certo.

## Três ambientes, três arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |
| **servir a API** (só na sua máquina) | `pip install -r requirements-api.txt` | tudo acima do app **+ fastapi + uvicorn** |

> **Nenhuma dependência nova na v12.** `HTTPException`, `status` e `JSONResponse` vêm do FastAPI.

## Rodar localmente — dois terminais

| Terminal 1 — o **painel** (pessoas) | Terminal 2 — a **API** (programas) |
|---|---|
| `streamlit run app.py` | `uvicorn api.main:app --reload` |
| http://localhost:8501 → **🗣️ Relatos** e **🔎 Analisador** | http://127.0.0.1:8000/docs |

## A API (v12) — o que cada rota responde, inclusive quando dá errado

| Método e rota | Sucesso | Erros declarados (além do 422 e do 500) |
|---------------|:-------:|------------------------------------------|
| `GET /` · `GET /fontes` | 200 | — |
| `GET /desmatamento` · `/total` · `/{uf}` | 200 (período sem dado: `"linhas": 0`) | **503** — a coleta não está nesta máquina |
| `GET /desmatamento/ranking/{ano}` | 200 | **404** — o PRODES não tem o ano · **503** |
| `GET /noticias` | 200 (seção sem notícia: `"linhas": 0`) | **503** — a coleta não está nesta máquina |
| `GET /relatos` | 200 (filtro sem relato: `"linhas": 0`) | — |
| **`GET /relatos/{id}`** | 200 | **404** — não há relato com esse número |
| `POST /relatos` | **201** | **409** — o mesmo relato há menos de 10 minutos |
| `POST /processar_texto` | 200 | **503** — o motor de análise não carregou |

**Todo erro tem o mesmo formato**, `{"detail": …}` — mas o `detail` muda com o status:

| Status | Quando | `detail` |
|:------:|--------|----------|
| **422** | o pedido não cumpre o contrato (tipo, limite, campo a mais) | uma **lista**, um item por campo (`loc`, `type`, `msg`) |
| **404** · **409** · **503** | não existe · conflita · falta algo no servidor | uma **frase** para quem pediu |
| **500** | um erro que ninguém previu | uma frase com um **código** — o mesmo que aparece no terminal da API |

```json
GET /desmatamento/ranking/2026   ->   404
{"detail": "O PRODES não tem a taxa de 2026: a série vai de 1988 a 2025."}

POST /relatos  (o mesmo relato, de novo)   ->   409
{"detail": "Este relato já foi recebido: nº 3, em 27/10/2026 10:49. Não é preciso enviar de novo."}

POST /processar_texto  (sem data/analisador/regras.json)   ->   503
{"detail": "O analisador de texto está indisponível: o motor não foi carregado quando a API subiu. As outras rotas funcionam normalmente."}
```

### O critério do 404: identificar × recortar (o da Aula 11)

| Pedido | Resposta | Por quê |
|--------|:--------:|---------|
| `GET /desmatamento/ranking/2026` | **404** | o **caminho** identifica *um* ranking — e ele não existe |
| `GET /relatos/99` | **404** | o caminho identifica *um* relato — e ele não existe |
| `GET /relatos?uf=AC` (nenhum do Acre) | **200**, `[]` | a **consulta** recorta uma coleção — vazia é a resposta certa para "quais?" |
| `GET /desmatamento?desde=2030` | **200**, `[]` | idem |

### Ler uma resposta de erro, de outro programa

```python
import requests
r = requests.get("http://127.0.0.1:8000/desmatamento/ranking/2026", timeout=10)
if r.ok:                                   # 2xx — inclusive o 201
    dados = r.json()["dados"]
elif r.status_code == 422:                 # o detail é uma LISTA
    print([e["msg"] for e in r.json()["detail"]])
else:                                      # o detail é uma FRASE
    print(r.status_code, r.json()["detail"])
```

## O que mudou da v11 para a v12

| # | Mudança | Onde | Por quê |
|---|---------|------|---------|
| 1 | **404** no ranking de um ano sem dado | `api/rotas/desmatamento.py` | `ranking/2026` respondia 200 vazio — e um relatório registrou "nenhum desmatamento em 2026" (🐛) |
| 2 | **`GET /relatos/{id}`**, com **404** | `api/rotas/relatos.py` · `src/relatos.py` (`buscar_relato`) | buscar um relato pelo número que o envio devolveu |
| 3 | **409** para o relato repetido em 10 min | `src/relatos.py` (`RelatoRepetido`) · `api/rotas/relatos.py` | com o sinal caindo, o mesmo relato entrava duas, três vezes |
| 4 | **503** quando o motor de análise não carrega — e a API **sobe assim mesmo** | `api/rotas/analise.py` | na v11, sem `regras.json` a API **inteira** não subia (`FileNotFoundError` ao importar) (🐛) |
| 5 | **503** quando a coleta não está nesta máquina | `api/rotas/desmatamento.py` · `noticias.py` | sem o CSV, `/desmatamento` quebrava: `ValueError: min() iterable argument is empty` → 500 (🐛) |
| 6 | **Rede de segurança**: 500 em JSON, com código, e o código no log | `api/erros.py` · `api/main.py` | o CSV salvo pelo Excel (`;`) dava `KeyError: 'id'` → 500 **em texto puro** (🐛) |
| 7 | Erros **declarados** em cada rota (`responses=`) | rotas · `FastAPI(responses={500: …})` | sem isso, o `/docs` mostra o 404 como *Undocumented* (a figura 3.2 do livro) |
| 8 | O painel lê **pelo status**: `FalhaDaAPI` | `src/cliente_api.py` | o painel v11 dizia *"A API não respondeu (HTTPError). Tente de novo."* a um 409 (🐛) |
| 9 | As páginas mostram a frase da API, **no tom certo** | `paginas/relatos.py` · `paginas/analisador.py` | 409 e 503 são avisos; 422 e 500, erros. Com 500 na lista, o aviso de "exemplos fictícios" sai da legenda para a tela (🐛) |

## Estrutura

```
painel_ods_brasil/
├── app.py
├── paginas/relatos.py        mostra o 409 como AVISO; a lista com erro avisa em voz alta    ← v12
├── paginas/analisador.py     503 → aviso + link para o que funciona                         ← v12
├── src/
│   ├── cliente_api.py        FalhaDaAPI: o STATUS decide como ler o corpo                   ← v12
│   ├── relatos.py            + RelatoRepetido, buscar_relato()                              ← v12
│   └── …
└── api/
    ├── main.py               + a rede de segurança; o 500 documentado em toda rota
    ├── erros.py              Erro (o formato), erro() (responses=), erro_inesperado()       ← novo
    ├── modelos.py · respostas.py
    └── rotas/                404 · 409 · 503, cada um declarado na sua rota
```

## Publicar

```bash
git add .
git commit -m "v12: 404, 409 e 503 com HTTPException, 500 em JSON com código, e o painel lendo pelo status"
git push
```

## Verificação

Confirmado em 27/10/2026 — FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Streamlit 1.61, Python 3.13
(Windows): servidor real (`uvicorn` num terminal) + `requests`; `TestClient`; `AppTest` com a API ligada,
desligada **e quebrada de propósito** (sem `regras.json`, com o CSV salvo pelo Excel).

| Afirmação | Verificação |
|---|---|
| 404 no ranking | `ranking/2025` → 200 (9 UFs); `ranking/2026` → 404 *"…a série vai de 1988 a 2025."* |
| 404 × 200 vazio | `relatos/99` → 404; `relatos?uf=AC` → 200 `"linhas": 0`; `desmatamento?desde=2030` → 200 `"linhas": 0` |
| 409 | o mesmo relato duas vezes → 201, depois 409 com o número do primeiro; mesmo texto, outra UF → 201 |
| 503 do analisador | sem `regras.json` (ou com JSON inválido): a API **sobe**, `/processar_texto` → 503, `/desmatamento/total` → 200 |
| v11 sem `regras.json` | a API **não sobe**: `FileNotFoundError` ao importar `api/rotas/analise.py` |
| 503 sem a coleta | v11: `/desmatamento` → 500 (`ValueError: min() iterable argument is empty`); v12: 503 com o que fazer |
| A rede de segurança | CSV com `;` → 500 `application/json` com código; no terminal: `Erro inesperado [código] em GET /relatos — KeyError: 'id'` + o traceback |
| `responses=` | o `/openapi.json` lista 404/409/503/500 nas rotas certas; no `/docs`, o 404 deixa de ser *Undocumented* |
| O painel v11 contra a API v12 | 409 → *"A API não respondeu (HTTPError). Tente de novo."*; 500 na lista → 5 exemplos fictícios, aviso só na legenda |
| O painel v12 | 409 → aviso com o nº do relato; curto → *"…pelo menos 15 caracteres."*; 503 → aviso + link; 500 → erro com o código, e a tabela de exemplos anunciada |
| "Demorou" × "não está no ar" | no Windows, recusar a conexão leva 2,02 s (`localhost`: 4,03 s); com `timeout=2` vira `ConnectTimeout`. O cliente trata `ReadTimeout` → *"demorou"* e `ConnectionError` → *"não está no ar"* (🐛 da produção: a 1ª versão tratava `Timeout` e dizia "demorou" à API desligada) |
| As nove páginas, pelo link direto | `AppTest`, API desligada: zero exceções |
