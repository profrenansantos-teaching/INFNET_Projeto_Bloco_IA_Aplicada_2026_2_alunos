# Aulas 13–14 — Passo a passo: quem responde, promete; quem falha, explica

> Os passos das **duas** aulas numa pasta só: os cinco da Aula 13 e os cinco da Aula 14. Cada aula tem a sua numeração,
> por isso há dois "passo 1" — a tabela abaixo dá a ordem. Os passos 1–5 da Aula 13 e 1–4 da Aula 14 são **APIs** servidas
> pelo `uvicorn`; os dois clientes (`passo04_cliente.py`, `passo05_cliente.py`) são scripts. O destino é a **v12** em
> `../../aula-14/demo/painel_ods_brasil/`. **Nenhum passo precisa de internet** (só o `/docs`, que baixa o Swagger no
> navegador). `_dados.py` junta os dados das duas aulas; `_motor.py` é o motor provisório da Aula 13.

**Antes:** o ambiente da API (o mesmo das Aulas 11 e 12) e esta pasta como ponto de partida.

```bash
pip install -r ../../aula-14/demo/painel_ods_brasil/requirements-api.txt
uvicorn passo01_sem_contrato:app --reload          # e abra http://127.0.0.1:8000/docs
```

> Só **uma** API por vez na porta 8000: **Ctrl+C** no terminal do `uvicorn` antes de subir a próxima.

## A ordem dos passos

| # | Aula · passo | Arquivo | Como rodar | Rodamos | O que deve aparecer |
|--:|:------------:|---------|------------|:-------:|---------------------|
| 1 | 13 · 1 | `passo01_sem_contrato.py` | `uvicorn passo01_sem_contrato:app --reload` | em aula | no `/docs`, a resposta 200 das 4 rotas é `"string"` |
| 2 | 13 · 2 | `passo02_response_model.py` | `uvicorn passo02_response_model:app --reload` | em aula | `/fontes` 5 · 5 · 5 campos; `palavras: 431`; `/processar_texto` com 6 campos |
| 3 | 13 · 3 | `passo03_promessa_quebrada.py` | `uvicorn passo03_promessa_quebrada:app --reload` | em aula | `/noticias-v1` → **500** em texto puro; no **terminal**, `ResponseValidationError` |
| 4 | 13 · 4 | `passo04_status_201.py` + `passo04_cliente.py` | API: `uvicorn passo04_status_201:app --reload` · cliente: `python passo04_cliente.py` | **em casa** | o cliente diz **"FALHOU"** ao 201 |
| 5 | 13 · 5 | `passo05_contrato_do_motor.py` | `uvicorn passo05_contrato_do_motor:app --reload` | em aula | o barco → `seca` 1.0; o arroio → **`null`** 0.0; `"curto"` → 422 |
| 6 | 14 · 1 | `passo01_200_ou_404.py` | `uvicorn passo01_200_ou_404:app --reload` | em aula | `/v11/ranking/2026` → 200 **vazio**; `/ranking/2026` → **404** com a frase |
| 7 | 14 · 2 | `passo02_status_certo.py` | `uvicorn passo02_status_certo:app --reload` | **em casa** | o mesmo relato duas vezes: 201 e **409** |
| 8 | 14 · 3 | `passo03_motor_fora.py` (+ `regras_passo03.json`) | `uvicorn passo03_motor_fora:app --reload` | em aula | sem as regras: **503** e a `/saude` no ar; sem o `try`: **nenhuma** rota sobe |
| 9 | 14 · 4 | `passo04_erro_inesperado.py` (+ `relatos_excel.csv`) | `uvicorn passo04_erro_inesperado:app --reload` | em aula | sem a rede: 500 em **texto puro**; com: 500 em JSON, com o código |
| 10 | 14 · 5 | `passo05_cliente.py` | com o **passo 2 da Aula 14** no ar: `python passo05_cliente.py` | **em casa** | cinco frases — e o 🐛 cliente ingênuo: `TypeError` |
| 11 | — | `../../aula-14/demo/painel_ods_brasil/` | `uvicorn api.main:app --reload` + `streamlit run app.py` | em aula | a **v12**: o 409 como aviso; o 503 na página |

## Os passos com interruptor

**Linha 8 — 14 · 3 · o motor fora** (com `--reload`, salvar o `.py` reinicia a API):

1. Suba: `POST /processar_texto` → 200.
2. Renomeie `regras_passo03.json` para `regras_passo03.json.bak` e salve o `.py`. No terminal:
   `ERROR: Motor NÃO carregado — FileNotFoundError…`. `POST /processar_texto` → **503**; `GET /saude` → **200**.
3. 🐛 Mude `CARREGAR_COM_SEGURANCA = False` e salve: a API **não sobe**. Nem a `/saude`.
4. **Desfaça:** o nome do arquivo de volta, `True` de volta. (O `.gitignore` desta pasta ignora o `.bak`.)

**Linha 9 — 14 · 4 · o erro que ninguém previu:** `GET /relatos` com `REDE_DE_SEGURANCA = False` (500, *"Internal
Server Error"*, `r.json()` quebra); mude para `True`, salve, e de novo: o 500 vem em JSON, com o código que liga a frase
do usuário ao traceback do terminal.

## A ideia que amarra os passos

```
  quem responde, promete                                  quem falha, explica
  ─────────────────────                                   ───────────────────
  response_model: a saída FILTRADA, CONFERIDA, DOCUMENTADA   o status certo (a 1ª palavra) + uma frase (detail)
  não cumpre? 500 — a API quebrou a promessa               404 não existe · 409 conflito · 503 falta algo · 500 imprevisto
```

O 422 da Aula 12 diz que o **cliente** errou (`loc` começa com `"body"`); o 500 do passo 3 da Aula 13, que a **API**
errou (`loc` começa com `"response"`, no terminal). O porquê de cada passo e o código comentado estão nos guias:
[`../../aula-13/student-guide.md`](../../aula-13/student-guide.md) e
[`../../aula-14/student-guide.md`](../../aula-14/student-guide.md).

## Números medidos (não estimados)

| Linha | Medição |
|------:|---------|
| 1 | as 4 rotas com esquema vazio no `/openapi.json`; `/fontes` 11 · 6 · 3 campos; `palavras` `"431"`; `/processar_texto` 8 campos |
| 2 | `/fontes` 5 · 5 · 5; `palavras` 431; `/processar_texto` 6 campos |
| 3 | `/relatos-v1` e `/noticias-v1` → 500 `text/plain`; `/relatos` e `/noticias` → 200 |
| 4 | `POST /v1/relatos` → 200 (*"gravado"*) · `POST /relatos` → 201 (`== 200`: *"FALHOU"*; `r.ok`: *"gravado"*) |
| 5 | seca 1.0 (`nível do rio`, `baixou`) · `null` 0.0 · 422 `string_too_short` |
| 6 | `/v11/ranking/2026` 200 vazio · `/ranking/2026` 404 *"O PRODES não tem a taxa de 2026: a série vai de 2022 a 2025."* · `/relatos/99` 404 · `/relatos?uf=AC` 200 vazio |
| 7 | 201 · 409 (*"Este relato já foi recebido: nº 1, em …"*) · 422 (`"fumaça"`) · 404 |
| 8 | com as regras: 200 · sem: 503 + `/saude` 200 · sem o `try`: a API não sobe (`FileNotFoundError`) |
| 9 | sem a rede: 500 `text/plain` · com: 500 JSON (*"Erro interno na API (código …)"*) |
| 10 | as cinco mensagens (201 · 409 · 404 · 422 · *"A API demorou demais…"*); o ingênuo: `TypeError: string indices must be integers` |
