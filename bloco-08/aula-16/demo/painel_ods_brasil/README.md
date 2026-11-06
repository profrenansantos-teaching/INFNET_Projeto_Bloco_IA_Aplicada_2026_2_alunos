# Painel de Indicadores Sustentáveis do Brasil — v14

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 16 · PB Etapa 8**.

Painel ESG/ODS em **Python puro** (sem pandas), com uma **API** própria (FastAPI). Na v13 o projeto **escolheu**,
medindo, o modelo de linguagem que vai analisar os relatos. Na **v14**, ele **entra na API**: quem responde o
**`POST /processar_texto`** — a rota do TP4 — passa a ser o **`Qwen/Qwen2.5-1.5B-Instruct`**, rodando **na CPU da
máquina da API**, sem nuvem. O **contrato não muda** (o da Aula 13): o painel e quem mais usa a rota não mudam uma
linha. Mudou **onde** o modelo carrega (uma vez, quando a API sobe), **como** a rota é declarada (`def`, para não
travar a API), e o **503** da Aula 14 ganhou um motivo de verdade: o modelo que não foi baixado.

Com a v14, **os quatro itens do TP4 estão no projeto**.

## Três ambientes, três arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |
| **servir a API — com o modelo** (só na sua máquina) | `pip install -r requirements-api.txt` | tudo acima do app **+ fastapi + uvicorn + transformers + torch + huggingface_hub** |

> **Nenhuma dependência nova na v14** — as do modelo entraram na v13. No **Linux**, instale antes o `torch` de CPU
> (veja o comentário em `requirements-api.txt`).

## Rodar localmente — um passo antes, dois terminais depois

```bash
python -m src.baixar_modelo          # UMA vez, com internet: ~3,1 GB para a pasta de cache do Hugging Face
```

| Terminal 1 — o **painel** (pessoas) | Terminal 2 — a **API** (programas), com o modelo |
|---|---|
| `streamlit run app.py` | `uvicorn api.main:app --reload` |
| http://localhost:8501 → **🔎 Analisador** · **🧪 Escolha do modelo** | http://127.0.0.1:8000/docs |

A API leva **~20 s para subir** (na nossa máquina): ~10 s importando `torch`/`transformers` e ~10 s carregando o
modelo. No terminal: `INFO: Modelo Qwen/Qwen2.5-1.5B-Instruct carregado em 9.6 s.` → `Application startup complete.`
**Memória:** ~6,5 GB para o modelo, enquanto a API estiver no ar.

> ⚠️ Com `--reload`, **cada vez que você salva um `.py`** a API reinicia — e recarrega o modelo. Para usar o painel
> sem editar código, suba sem `--reload`.

## A rota do TP4, agora com o modelo

```json
POST /processar_texto   {"texto": "A água do arroio subiu durante a noite e alcançou as casas da rua de baixo."}

200   {"tipo_analise": "classificacao",
       "texto": "A água do arroio subiu durante a noite e alcançou as casas da rua de baixo.",
       "categoria_sugerida": "enchente", "confianca": 1.0, "pistas": [],
       "motor": "Qwen/Qwen2.5-1.5B-Instruct"}
```

| Campo | Com as regras (v11–v13) | Com o modelo (v14) |
|-------|-------------------------|--------------------|
| `categoria_sugerida` | uma das seis, ou `null` (sem pista) — o arroio: `null` | **sempre** uma das seis — o arroio: `enchente` |
| `confianca` | a fração das pistas | a **probabilidade** que o modelo dá à categoria — **não** é a chance de acerto |
| `pistas` | as palavras encontradas | `[]` — um modelo não aponta palavras |
| `motor` | `regras-v1 (palavras-chave)` | `Qwen/Qwen2.5-1.5B-Instruct` |

**Como o modelo classifica** (`src/analisador_llm.py`): ele lê as instruções (as definições das seis categorias, o
prompt que venceu na bancada) e o relato, e olhamos **uma vez** a próxima palavra que ele diria — a probabilidade de
cada categoria. A maior é a sugestão; o valor, a confiança. A resposta é **sempre** uma das seis (um LLM deixado
escrever já respondeu *"Chuveiro"*). No banco de provas: **27 de 30**, ~2,2 s por relato.

**Quando ele não carregou:**

```json
POST /processar_texto   ->   503
{"detail": "O analisador de texto está indisponível: o modelo de linguagem não foi carregado quando a API subiu. As outras rotas funcionam normalmente."}
```

E no terminal da API:

```
ERROR:    Modelo Qwen/Qwen2.5-1.5B-Instruct NÃO carregado — OSError: We couldn't connect to 'https://huggingface.co' to load the files, and couldn't find them in the cached files. → a rota /processar_texto vai responder 503. Ele foi baixado? python -m src.baixar_modelo
```

## O que mudou da v13 para a v14

| # | Mudança | Onde | Por quê |
|---|---------|------|---------|
| 1 | O **motor** do `POST /processar_texto` é o modelo da Aula 15 | `src/analisador_llm.py` | o TP4 (item 2): um modelo do Hugging Face, executado localmente |
| 2 | O modelo carrega **uma vez**, no **`lifespan`** | `api/main.py` · `api/rotas/analise.py` | carregado a cada pedido, cada análise pagava a carga inteira (🐛, passo 1) [Parandeh, p92 e p96] |
| 3 | A rota é **`def`**, não `async def` | `api/rotas/analise.py` | com `async def`, enquanto o modelo pensava, a API inteira esperava (🐛, passo 3) [Parandeh, p192] |
| 4 | O modelo é **baixado à parte**; a API só lê do disco (`local_files_only=True`) | `src/baixar_modelo.py` · `src/analisador_llm.py` | sem isso, a subida da API virava um download de 3,1 GB (71 s) — ou, sem internet, 82 s até falhar (🐛) |
| 5 | Falha na carga → **503** só na análise; a API sobe | `api/rotas/analise.py` | o 503 da Aula 14, agora para o modelo (TP4, item 4) |
| 6 | **Pontuar** as categorias, em vez de deixar o modelo escrever | `src/analisador_llm.py` | o contrato promete uma das seis e uma confiança; um LLM que escreve devolveu *"Chuveiro"* → 500 (🐛, passo 5) |
| 7 | A página Analisador: espera, nenhuma pista, o aviso da confiança | `paginas/analisador.py` | a mesma chamada; o que a página **diz** muda com o motor |
| 8 | A bancada mede o motor da API (`--tarefa pontuar`); o prompt vem de **um lugar só** | `src/bancada.py` · `src/analisador_llm.py` | o que a bancada mede é exatamente o que a API usa |
| 9 | Os exemplos do `/docs` e as descrições dos campos | `api/modelos.py` · `api/respostas.py` | o contrato não mudou; o que cada campo **diz**, sim |

## Estrutura

```
painel_ods_brasil/
├── paginas/analisador.py     espera · "o modelo não aponta palavras" · a confiança não é acerto  ← v14
├── src/
│   ├── analisador_llm.py     o MOTOR: carregar_motor() e classificar_com_modelo()               ← v14
│   ├── baixar_modelo.py      baixa o modelo UMA vez (python -m src.baixar_modelo)                ← v14
│   ├── bancada.py            + --tarefa pontuar (o motor da API); ESCOLHA e o prompt vencedor
│   ├── analisador.py         o motor de regras (v11) — a linha de base da bancada
│   └── …
└── api/
    ├── main.py               + o lifespan: carrega o modelo quando a API sobe                    ← v14
    └── rotas/analise.py      MOTORES · carregar_na_subida() · def processar_texto · 503         ← v14
```

## Publicar

```bash
git add .
git commit -m "v14: o modelo de linguagem local atrás do POST /processar_texto — lifespan, def e 503"
git push
```

## Verificação

Confirmado em 27/10/2026 — Python 3.13, torch 2.14.1 (CPU), Transformers 5.21, FastAPI 0.142, uvicorn 0.52,
Streamlit 1.61 (Windows 11 · i5-12400F, 12 *threads*, 32 GB; tudo medido na CPU, com o torch de CPU): servidor **real** (`uvicorn`) + `requests`;
`AppTest` das dez páginas com a API ligada, desligada e **sem o modelo**; e num ambiente **sem `torch`**.

| Afirmação | Verificação |
|---|---|
| A subida | ~21 s até a primeira resposta; o modelo, 9,6 s; ~6,5 GB de memória |
| O arroio | `enchente`, confiança 1,0, em ~2,5 s — o exemplo do `/docs` é a resposta real |
| O erro confiante | *"O nível do rio baixou tanto que o barco…"* (seca) → `enchente`, confiança **1,0** |
| Os limites | 14 caracteres → 422; 2.001 → 422; 1.975 → 200 em **8,1 s** |
| `def` não trava | `GET /desmatamento/total` durante uma análise longa: **0,05 s** |
| A CPU é uma só | duas análises ao mesmo tempo: **4,6 s** cada (uma sozinha: ~2,5 s) |
| O 503 | sem o modelo baixado: a API sobe em ~10 s; análise → 503 em 0,02 s; `/desmatamento/total` → 200 |
| `local_files_only` | sem o modelo: `OSError` em **0,4 s** · sem ele e sem internet: 82,5 s até o `OSError` · com internet: a carga baixou 3,1 GB (**71 s**) |
| A bancada do motor | `python -m src.bancada Qwen/Qwen2.5-1.5B-Instruct --tarefa pontuar` → 27/30, 2,23 s por relato |
| O painel com o modelo | arroio → **enchente · 100%** + o aviso da confiança; sem o modelo → o aviso do 503 |
| As dez páginas | `AppTest`, API desligada: zero exceções — também sem `torch` (como no Community Cloud) |
