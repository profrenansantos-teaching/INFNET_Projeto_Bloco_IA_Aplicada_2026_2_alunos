# Aulas 15–16 — Passo a passo: quem escolhe, mede; quem pesa, carrega uma vez

> Os passos das **duas** aulas numa pasta só: o passo 0 (o download), os cinco **scripts** da Aula 15 e as cinco **APIs**
> da Aula 16, com o `cronometro.py`, o cliente que mede. Cada aula tem a sua numeração, por isso há dois "passo 1" — a
> tabela abaixo dá a ordem. O destino é a **v14** em `../../aula-16/demo/painel_ods_brasil/`. Os dados vêm de `_dados.py`
> e `banco_de_provas.csv` (30 relatos **fictícios**, rotulados à mão); o motor das APIs, de `_motor.py` (o Qwen2.5-0.5B).

**Antes — com internet, UMA vez** (os modelos vão para o cache do Hugging Face, fora do projeto):

```bash
pip install -r ../../aula-16/demo/painel_ods_brasil/requirements-api.txt   # Linux: veja o comentário do torch no arquivo
python passo00_baixar.py              # os dois modelos dos passos (~1,5 GB)
python passo00_baixar.py --grande     # opcional, com 16 GB de RAM: + o Qwen2.5-1.5B (3,1 GB)
cd ../../aula-16/demo/painel_ods_brasil && python -m src.baixar_modelo     # o modelo da v14, para rodar o demo
```

Depois disso, **nenhum passo precisa de internet** — só o passo 2 da Aula 15, que consulta o Hub (sem rede, ele mostra
as fichas salvas em `fichas_salvas.json`).

> Só **uma** API por vez na porta 8000: **Ctrl+C** no terminal do `uvicorn` antes de subir a próxima. **Memória:** não
> rode o demo (~6,5 GB) com um passo da Aula 16 no ar — feche um antes do outro. As APIs sobem **sem** `--reload`.

## A ordem dos passos

| # | Aula · passo | Arquivo (o que trocar) | Como rodar | Rodamos | O que deve aparecer |
|--:|:------------:|------------------------|------------|:-------:|---------------------|
| 0 | 15 · 0 | `passo00_baixar.py` | `python passo00_baixar.py` | **antes** | *"pronto em … s"* para cada modelo; da 2ª vez, 0 s |
| 1 | 15 · 1 | `passo01_pipeline.py` | `python passo01_pipeline.py` | em aula | o arroio → **enchente 0,80**; a análise leva ~5 s |
| 2 | 15 · 2 | `passo02_ficha.py` | `python passo02_ficha.py` | **em casa** | as 8 fichas: o mais baixado é **inglês**; o "multilingual" sem português; o *gated* |
| 3 | 15 · 3 | `passo03_custo.py` (`DTYPE`) | `python passo03_custo.py` — depois `DTYPE = "float32"` | em aula | float16: 558 MB, **~4,9 s** por relato · float32: 1.115 MB, **~0,5 s** |
| 4 | 15 · 4 | `passo04_banco_de_provas.py` | `python passo04_banco_de_provas.py` | em aula | regras **13** certos / 17 calados / 0 errados · mDeBERTa **18** / 0 / **12** |
| 5 | 15 · 5 | `passo05_gerador.py` (`PROMPT`) | `python passo05_gerador.py` — depois `PROMPT = "definicoes"` | **em casa** | 0.5B: **4/30** ("Desmatamento" a quase tudo, **"Chuveiro"**) → 11/30 com as definições |
| 6 | 16 · 1 | `passo01_por_requisicao.py` | `uvicorn passo01_por_requisicao:app` · `python cronometro.py analisar 3` | **em casa** | cada pedido paga a carga: ~6 s, depois 2–3 s |
| 7 | 16 · 2 | `passo02_lifespan.py` | `uvicorn passo02_lifespan:app` · `python cronometro.py analisar 3` | em aula | a carga **antes** de *Application startup complete*; **0,4 s** por pedido |
| 8 | 16 · 3 | `passo03_async_trava.py` (`TRAVAR`) | `uvicorn passo03_async_trava:app` · `python cronometro.py junto` — depois `TRAVAR = False` | em aula | `async def`: o `/saude` espera **~1,6 s** · `def`: **0,01 s** |
| 9 | 16 · 4 | `passo04_modelo_fora.py` (`PROTEGER`, `NOME`) | `uvicorn passo04_modelo_fora:app` · `python cronometro.py analisar 1` + `/saude` | **em casa** | com o `try`: `/saude` no ar, análise **503** · sem: *Application startup failed* |
| 10 | 16 · 5 | `passo05_contrato.py` (`PONTUAR`) | `uvicorn passo05_contrato:app` · `/docs` → `POST /processar_texto` | **em casa** | escrevendo: **500** (`'chuveiro'`) · pontuando: 200, sempre uma das seis |
| 11 | — | `../../aula-16/demo/painel_ods_brasil/` | `uvicorn api.main:app` + `streamlit run app.py` | **em casa** | a **v14**: a página 🧪, o `/docs`, o Analisador, o 503 |

## Os passos com interruptor

Os arquivos vêm com o primeiro valor. Rode, anote, troque, rode de novo.

- **Linha 3 — `DTYPE`:** rode com `"auto"`, anote o número, troque para `"float32"` e rode de novo. *O dobro de memória
  comprou um modelo 8 a 10 vezes mais rápido* (as duas medições abaixo) — com o mesmo acerto (linha 4).
- **Linha 8 — `TRAVAR`:** com `True` (a rota é `async def`), o `cronometro.py junto` manda um relato de 1.899
  caracteres e, 0,5 s depois, um `GET /saude`. Ctrl+C, `TRAVAR = False`, suba de novo, repita.
- **Linha 9 — `PROTEGER` e `NOME`:** o `NOME` vem com um erro de digitação (*Instrukt*). Com `PROTEGER = True`: a API
  sobe, `/saude` diz `"modelo_carregado": false`, a análise responde 503. Com `False`: a API não sobe. Depois, corrija o
  nome (*Instruct*): 200.
- **Linha 10 — `PONTUAR`:** com `False`, o modelo escreve a categoria — e *"Choveu sem parar…"* vira `'chuveiro'`
  (500, `ResponseValidationError` no terminal). Com `True`, as seis categorias são pontuadas: 200.

## A ideia que amarra os passos

| A pergunta | Como se responde | Linhas |
|------------|------------------|-------:|
| **Quem escolhe, mede:** o modelo serve? | a ficha dá pistas (sem baixar); o **banco de provas** dá o veredito; o custo se mede **na sua máquina** | 1–5 |
| **Quem pesa, carrega uma vez:** como ele entra na API? | no `lifespan` (uma vez); numa rota `def` (não trava); com `try` (503, não a API fora); **pontuando** o contrato | 6–10 |

O porquê de cada passo e o código comentado estão nos guias:
[`../../aula-15/student-guide.md`](../../aula-15/student-guide.md) e
[`../../aula-16/student-guide.md`](../../aula-16/student-guide.md).

## Números medidos (não estimados)

Os tempos mudam de máquina para máquina (e de uma rodada para outra); as contagens, não.

| Linha | Medição (i5-12400F, 32 GB, só CPU) |
|------:|------|
| 1 | arroio → enchente 0,80 (seca 0,10); carga 3,0 s; análise 5,0 s |
| 2 | as 8 fichas, do Hub — e as mesmas de `fichas_salvas.json` sem rede |
| 3 | float16: 558 MB, 4,91 s/relato · float32: 1.115 MB, 0,51 s/relato |
| 4 | regras 13 / 17 / 0 · mDeBERTa 18 / 0 / 12 (21 s para os 30) |
| 5 | 0.5B simples 4/30 (#17 *"Chuveiro"*, #25 *"chama-vaquinha"*) · definições 11/30 |
| 6 | 6,3 / 2,9 / 2,9 s por pedido (carga 5,6 / 2,3 / 2,3 s) |
| 7 | carga na subida 4,3 s; 0,4 s por pedido |
| 8 | `async def`: `/saude` esperou 1,59 s · `def`: 0,01 s (análise de 2,1 s) |
| 9 | sem `try`: *Application startup failed. Exiting.* · com: `/saude` `modelo_carregado: false` + análise 503 · nome certo: 200 |
| 10 | escrever: 500 (`literal_error`, `'chuveiro'`); o arroio, 200 com `confianca: null` · pontuar: 200 (desmatamento 0,60 e 0,53) |
