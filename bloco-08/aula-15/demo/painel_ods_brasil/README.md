# Painel de Indicadores Sustentáveis do Brasil — v13

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 15 · PB Etapa 8**.

Painel ESG/ODS em **Python puro** (sem pandas), com uma **API** própria (FastAPI). Desde a v11, a rota do TP4,
**`POST /processar_texto`**, sugere a categoria de um relato — com um motor **provisório** de regras, que acerta quando
acha uma palavra da lista e cala quando não acha. Na **v13**, o projeto **escolhe o modelo de linguagem** que vai
substituir as regras — **medindo**: a **ficha** de cada candidato no Hub (licença, *gated*, línguas, tamanho), a
**bancada** que mede cada um no **banco de provas** (30 relatos rotulados) e na máquina da API, e a **justificativa**
(o item 1 do TP4), que a nova página **🧪 Escolha do modelo** mostra. **A API não muda nesta versão**: o modelo
escolhido entra atrás da rota na **v14** (Aula 16).

## Três ambientes, três arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |
| **servir a API e escolher o modelo** (só na sua máquina) | `pip install -r requirements-api.txt` | tudo acima do app **+ fastapi + uvicorn + transformers + torch + huggingface_hub** |

> **Novas na v13: `transformers`, `torch` e `huggingface_hub`** — no ambiente da API, porque o modelo vai morar
> nela. No **Windows e no Mac**, o `pip` traz o `torch` de CPU (~125 MB). No **Linux**, o pacote padrão traz também a
> CUDA da NVIDIA (vários GB): instale antes o de CPU — `pip install torch --index-url https://download.pytorch.org/whl/cpu`.
> O app publicado **não** importa nada disso: a página 🧪 só **lê** arquivos.

## Escolher o modelo — três comandos

```bash
python -m src.ficha_modelo Qwen/Qwen2.5-1.5B-Instruct google/gemma-3-1b-it   # 1. a ficha, ANTES de baixar (internet)
python -m src.bancada regras                                                   # 2. a linha de base
python -m src.bancada Qwen/Qwen2.5-1.5B-Instruct --tarefa gerar                # 3. um candidato (baixa na 1ª vez)
streamlit run app.py                                                           # → 🧪 Escolha do modelo
```

Cada execução da bancada grava uma linha em `data/analisador/avaliacao.json`. Opções: `--tarefa zero-shot` (modelos de
inferência textual, família BERT), `--dtype bfloat16|float16|auto` (o tipo dos números — **custo**), `--prompt simples`.

## A decisão (o item 1 do TP4) — `docs/escolha_do_modelo.md`

**`Qwen/Qwen2.5-1.5B-Instruct`, em float32, na CPU, com as definições das categorias no prompt.**

| Critério do TP4 | O que pesou |
|-----------------|-------------|
| **Desempenho** | **27 de 30** no banco de provas (regras: 13; o melhor zero-shot: 18). Decoder (família GPT), treinado para seguir instruções. |
| **Custo computacional local** | 3,1 GB de download; **6,2 GB** de pesos em float32; **2,8 s** por relato na CPU; ~16 s para carregar, uma vez. |
| **Acessibilidade local** | **Apache 2.0**, sem *gated*; `transformers` + `torch` na CPU; depois de baixado, roda sem internet. |

| Motor (bancada, na nossa máquina) | Acertos | s por relato | Pesos |
|-----------------------------------|--------:|-------------:|------:|
| regras (v11) | 13/30 (17 sem resposta) | 0,0 | — |
| MiniLM-L6 · BART-large-MNLI (zero-shot) | 7/30 · 9/30 | 0,05 · 1,05 | 0,4 · 1,6 GB |
| mDeBERTa (zero-shot) — float16 × float32 | 18/30 · 18/30 | **4,5** × 0,57 | 0,6 × 1,1 GB |
| Qwen2.5-0.5B (gera) — prompt simples × definições | 4/30 · 11/30 | 0,51 · 0,79 | 2,0 GB |
| Qwen3-0.6B (gera) | 20/30 | 1,06 | 2,4 GB |
| Qwen2.5-1.5B (gera) — simples × **definições** | 23/30 · **27/30** | 1,42 · **2,8** | **6,2 GB** |
| Qwen2.5-1.5B (gera) — bfloat16 | 27/30 | **12,9** | 3,1 GB |
| Qwen3-1.7B (gera) | 27/30 | 2,97 | 6,9 GB |

## O que mudou da v12 para a v13

| # | Mudança | Onde | Por quê |
|---|---------|------|---------|
| 1 | O **banco de provas**: 30 relatos fictícios, 5 por categoria, rotulados à mão | `data/analisador/banco_de_provas.csv` | "desempenho" é acertar **no nosso dado** — não num ranking |
| 2 | A **ficha** de um modelo, lida no Hub antes de baixar | `src/ficha_modelo.py` | o mais baixado é inglês; o "multilíngue" não tem português; o Gemma é *gated* (🐛) |
| 3 | A **bancada**: acertos, segundos, carga e memória de cada candidato | `src/bancada.py` · `data/analisador/avaliacao.json` | o mDeBERTa levava 4,5 s por relato em float16 — 0,57 s em float32 (🐛) |
| 4 | A **justificativa** — o item 1 do TP4 | `docs/escolha_do_modelo.md` | escolher é decidir com critérios declarados, e dizer o que pesou contra |
| 5 | A página **🧪 Escolha do modelo** | `paginas/modelo.py` · `app.py` (uma linha) | a escolha visível no painel publicado — sem rodar modelo nenhum |
| 6 | `transformers`, `torch`, `huggingface_hub` | `requirements-api.txt` | o que se importa, se declara — no ambiente que importa |

## Estrutura

```
painel_ods_brasil/
├── app.py                    + uma linha no menu (🧪 Escolha do modelo)
├── paginas/modelo.py         a decisão, os candidatos medidos, onde o escolhido erra        ← v13
├── src/
│   ├── ficha_modelo.py       o que o Hub diz de um modelo, antes de baixar                  ← v13
│   ├── bancada.py            mede um motor no banco de provas; ESCOLHA = a decisão           ← v13
│   ├── analisador.py         o motor de regras (v11) — a linha de base
│   └── …
├── data/analisador/
│   ├── banco_de_provas.csv   30 relatos rotulados (fictícios)                                ← v13
│   ├── avaliacao.json        o que a bancada mediu                                           ← v13
│   └── regras.json
├── docs/escolha_do_modelo.md a justificativa — o item 1 do TP4                               ← v13
└── api/                      sem mudança: o modelo entra na v14
```

> **Os modelos não vão para o Git.** Ficam na pasta de cache do Hugging Face (no Windows,
> `C:\Users\<você>\.cache\huggingface\hub`), fora do projeto: são gigabytes e não são nossos para redistribuir.
> O que vai para o Git é o que **reproduz** a escolha: o banco de provas, a bancada e o que ela mediu.

## Publicar

```bash
git add .
git commit -m "v13: a escolha do modelo — ficha, bancada, banco de provas e a justificativa do TP4"
git push
```

## Verificação

Confirmado em 27/10/2026 — Python 3.13, torch 2.14.1 (CPU), Transformers 5.21, huggingface_hub 2.3, Streamlit 1.61,
FastAPI 0.142 (Windows 11 · i5-12400F, 12 *threads*, 32 GB; tudo medido na CPU, com o torch de CPU).

| Afirmação | Verificação |
|---|---|
| A tabela de medidas | `python -m src.bancada …` para os 13 arranjos; `avaliacao.json` é a saída real |
| float16 × float32 | mDeBERTa com `--dtype auto` → float16, 558 MB, **4,5 s**/relato; float32 → 1.115 MB, **0,57 s**; 18/30 nos dois |
| bfloat16 na nossa CPU | Qwen2.5-1.5B: 27/30 nos dois tipos; bfloat16 **12,9 s** × float32 **2,8 s** por relato |
| As fichas | `python -m src.ficha_modelo` contra o Hub: Gemma `gated: manual`; MiniLM sem `pt`; BART sem língua; BERTimbau `fill-mask`; Qwen2.5-3B licença `other`; repositório inexistente → 401 |
| O Gemma sem token | `pipeline("text-generation", model="google/gemma-3-1b-it")` → `OSError: You are trying to access a gated repo… 401` |
| O XLM-R-large | precisou de `sentencepiece` para carregar o tokenizador (o erro cita `tiktoken`); depois, 17/30 |
| A página 🧪 | `AppTest`: zero exceções — inclusive num ambiente **sem** `torch` (como o Community Cloud) |
| As dez páginas, pelo link direto | `AppTest`, API desligada: zero exceções |
