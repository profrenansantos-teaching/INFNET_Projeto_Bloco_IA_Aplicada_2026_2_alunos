# Aula 12 — Passo a passo: quem recebe, valida

> Os passos 1–4 são **APIs** (servidas pelo `uvicorn`); o passo 5 é um **app Streamlit** que fala com a
> API do passo 4. O destino é a **v10** em `../demo/painel_ods_brasil/`. **Nenhum passo precisa de
> internet** (só o `/docs`, que baixa o Swagger no navegador). Os dados de desmatamento vêm de
> `_dados.py` — o mesmo recorte real do PRODES da Aula 11.

**Antes:** o ambiente da API (o mesmo da Aula 11) e esta pasta como ponto de partida.

```bash
pip install -r ../demo/painel_ods_brasil/requirements-api.txt
uvicorn passo01_post_dict:app --reload          # e abra http://127.0.0.1:8000/docs
```

| Passo | Arquivo | Como rodar | O que ensina |
|------:|---------|-----------|--------------|
| **1** | `passo01_post_dict.py` | `uvicorn passo01_post_dict:app --reload` | o primeiro POST do livro, com `dict`: **aceita tudo** — `{"uf": 123}`, `{}`, nome e telefone |
| **2** | `passo02_post_pydantic.py` | `uvicorn passo02_post_pydantic:app --reload` | o **modelo Pydantic**: 422 com **todos** os erros; campo a mais **descartado** × **recusado** (`extra="forbid"`); o `schema_extra` do livro **some** do `/docs` |
| **3** | `passo03_memoria_x_arquivo.py` | `uvicorn passo03_memoria_x_arquivo:app --reload` | 🐛 a lista na memória que o `--reload` **apaga** × o CSV que fica |
| **4** | `passo04_routers/` | `uvicorn passo04_routers.main:app --reload` | **routers**: `APIRouter(prefix=, tags=)` + `include_router` — o `main.py` vira roteador |
| **5** | `passo05_app_cliente.py` | com o passo 4 no ar: `streamlit run passo05_app_cliente.py` | o **app como cliente**: `json=`, `timeout=`, mostrar o 422, sobreviver à API desligada |
| **6** | `../demo/painel_ods_brasil/` | `uvicorn api.main:app --reload` + `streamlit run app.py` | tudo junto: `POST /relatos`, a página **🗣️ Relatos de campo** — a **v10** |

> Só **uma** API por vez na porta 8000: **Ctrl+C** no terminal do `uvicorn` antes de subir a próxima.
> Os passos 3 e 4 gravam `relatos_passo03.csv` e `relatos_passo04.csv` nesta pasta (não versionados).

---

## A ideia que amarra os passos

```
POST /relatos   {"uf": "PA", "categoria": "queimada", "texto": "…"}
                        │
                        ▼
      modelo Relato (Pydantic)  ── não cumpre ──►  422 · TODOS os problemas, juntos
                        │ cumpre                    (a função NEM roda)
                        ▼
      a função roda  →  grava (arquivo, com trava)  →  200 · o relato gravado
```

**Quem recebe, valida.** O modelo é o contrato do corpo: conferido na entrada e publicado no `/docs`.

## Passo 1 · o `dict` aceita tudo

| Corpo enviado | Resposta |
|---------------|----------|
| `{"uf": "PA", "texto": "Fumaça na estrada"}` | 200 |
| `{"uf": 123}` | **200** |
| `{}` | **200** |
| `{"nome": "Maria", "telefone": "91 9999-0000"}` | **200** — e guardado |

O livro diz o problema: *"an empty dictionary could've also been sent without returning any error"*
[Adeshina, p41].

## Passo 2 · o modelo — e os dois jeitos de tratar o que sobra

| Corpo | `/padrao` (modelo padrão) | `/estrito` (`extra="forbid"`) |
|-------|:-------------------------:|:-----------------------------:|
| `{"uf": "Pará", "categoria": "fogo", "texto": "curto"}` | 422 · `uf` · `categoria` · `texto` | igual |
| `{}` | 422 · três `Field required` | igual |
| relato válido **+ `nome` + `telefone`** | **200 — e os dois SOMEM** (descartados) | **422** · `extra_forbidden` × 2 |

> ⚠️ **Livro × hoje.** O livro diz que o modelo *"can only take four fields"* [Adeshina, p40] — como se
> recusasse o resto. **Por padrão, o Pydantic descarta em silêncio.** Para recusar, `extra="forbid"`. É o
> 🐛 tropeço da v10: a equipe de campo mandou o nome e o telefone do morador, recebeu 200 — e achou que
> tinham sido gravados.

E o **exemplo** no `/docs`: `/estrito` mostra; `/livro` (escrito com `class Config: schema_extra`, como no
livro [p51–54]) **não** — e o terminal do `uvicorn`, ao subir, avisa:

```
UserWarning: Valid config keys have changed in V2:
* 'schema_extra' has been renamed to 'json_schema_extra'
```

## Passo 3 · 🐛 a memória que o `--reload` apaga

| Momento | `GET /memoria` | `GET /arquivo` |
|---------|:--------------:|:--------------:|
| depois de 3 POSTs em cada | 3 | 3 |
| depois de **salvar um `.py`** (o `--reload` reinicia o servidor) | **0** | **3** |

A lista do livro é *"a temporary in-app database"* [Adeshina, p37] — temporária mesmo. O arquivo abre em
modo **`"a"`** (acrescentar); `"w"` zeraria a coleta anterior (o defeito 2 da A15, na Aula 10).

## Passo 4 · o `main.py` vira roteador

```python
router = APIRouter(prefix="/desmatamento", tags=["desmatamento"])   # em rotas/desmatamento.py
app.include_router(desmatamento.router)                             # em main.py
```

| Pedido | Resposta |
|--------|----------|
| `GET /desmatamento` | 36 linhas |
| `GET /desmatamento/total` | os 4 totais (2022–2025) |
| `GET /desmatamento/PA` | 4 linhas |
| `POST /relatos` (válido) · (com `nome`) | 200 · 422 `extra_forbidden` |

> ⚠️ **Duas pegadinhas:**
> - **`@router.get("")`, não `@router.get("/")`.** Com prefixo e `"/"`, o endereço vira
>   `/desmatamento/` — e um pedido a `/desmatamento` recebe um **307** (redirecionamento) antes da
>   resposta (verificado).
> - O livro justifica o `APIRouter` dizendo que uma instância `FastAPI()` *"will be unable to run both
>   routes"* [Adeshina, p36]. **Não é assim:** a API da Aula 11 servia sete rotas numa instância só.
>   Router é **organização** — o mesmo livro: *"encourages modularity and organization"* [p36].

## Passo 5 · o app como cliente

Com a API do passo 4 no ar: um relato válido → *"Relato recebido. Total na API: …"*; um texto curto →
*"texto: String should have at least 15 characters"* (o 422, mostrado). **Desligue a API** (Ctrl+C) e dê F5:
o app avisa e para (`st.stop()`) — **sem traceback**.

| Decisão | Sem ela |
|---------|---------|
| `json=` (e não `data=`) | 422 *"Input should be a valid dictionary or object to extract fields from"* |
| conferir o status antes de dizer "enviado" | o app diz **"Relato enviado!"** a um envio que a API **recusou** (A19) |
| `try` + `timeout=` | `ConnectionError` com o traceback inteiro na tela |
| o app **não** grava no arquivo | a regra de validação existiria em dois lugares |

## Números medidos (não estimados)

| Onde | Medição (06/10/2026 · FastAPI 0.142 · Pydantic 2.13 · uvicorn 0.52 · Streamlit 1.61) |
|------|----------------------------------------------------------------------------------|
| Passo 1 | 4 corpos, 4 × **200** — inclusive `{}` e `{"uf": 123}` |
| Passo 2 | 3 erros num 422; extras: `/padrao` 200 (descartados) · `/estrito` 422; exemplo só em `/estrito`; o aviso do `schema_extra` no terminal |
| Passo 3 | memória 3 → **0** depois de salvar um `.py`; arquivo 3 → 3 |
| Passo 4 | 36 linhas · 4 totais · PA 4 linhas; prefixo + `"/"` → **307** em `/desmatamento` |
| Passo 5 | envio válido aceito; 422 mostrado; API desligada → aviso, zero exceções |
| `data=` em vez de `json=` | corpo `dict`: 422 `dict_type` · modelo: 422 `model_attributes_type` |
| JSON malformado | 422 `json_invalid` · *"JSON decode error"* |
| No terminal do `uvicorn` | o 422 aparece como `422 Unprocessable Content` |
