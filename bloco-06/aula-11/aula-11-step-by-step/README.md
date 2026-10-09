# Aula 11 — Passo a passo: do outro lado da API

> Os passos 1–3 são **APIs** (servidas pelo `uvicorn`); o passo 4 é um **cliente** que as consome.
> O destino é a **v9** em `../demo/painel_ods_brasil/`. **Nenhum passo precisa de internet** — os
> dados vêm de `_dados.py`, um recorte real do PRODES (2022–2025, 9 UFs) tirado da coleta da Aula 10.
> *(Só o `/docs` usa a internet — ver o aviso abaixo.)*

**Antes:** instale o ambiente da API (a partir da pasta do demo) e volte para esta pasta.

```bash
pip install -r ../demo/painel_ods_brasil/requirements-api.txt     # app + fastapi + uvicorn
uvicorn passo01_ola:app --reload                                  # e abra http://127.0.0.1:8000/docs
```

| Passo | Arquivo | Como rodar | O que ensina |
|------:|---------|-----------|--------------|
| **1** | `passo01_ola.py` | `uvicorn passo01_ola:app --reload` | a menor API: decorador + função + dicionário → JSON; `/docs` de graça; **`python passo01_ola.py` não sobe nada** |
| **2** | `passo02_tipos.py` | `uvicorn passo02_tipos:app --reload` | parâmetro de **caminho**; **o tipo é a guarda**: sem ele, 200 e lista vazia; com ele, conversão e 422 |
| **3** | `passo03_consulta_e_ordem.py` | `uvicorn passo03_consulta_e_ordem:app --reload` | parâmetros de **consulta** com padrão e limites; **a ordem das rotas** (🐛 tropeço da v9) |
| **4** | `passo04_cliente.py` | com o passo 3 no ar: `python passo04_cliente.py` | o **outro lado**: o código da Aula 2 consumindo a **nossa** API; ler o `detail` de um 422 |
| **5** | `../demo/painel_ods_brasil/` | `uvicorn api.main:app --reload` (da pasta do demo) | tudo junto, sobre os CSVs de `data/processed/` — a **v9** |

> Só **uma** API por vez na porta 8000. Para trocar de passo: **Ctrl+C** no terminal do `uvicorn`, e
> suba o próximo.

---

## A ideia que amarra os passos

```
@app.get("/desmatamento/{uf}")          o MÉTODO e o CAMINHO           — o QUE se pede
def serie(uf: UfAmazonia,               entre { }: vem do CAMINHO
          desde: int = 1988):           o resto: vem da CONSULTA (?desde=2010) — o COMO
    return {...}                        dicionários e listas viram JSON
```

**Tudo o que chega numa URL é texto.** Quem converte para o tipo declarado — e recusa com **422** o
que não converte, **antes** de a função rodar — é o FastAPI. Sem tipo, nada é convertido, e nada é
recusado.

## Passo 1 · ⚠️ `python passo01_ola.py` não sobe nada

```
> python passo01_ola.py
>                                   ← termina em ~2 s, código 0, nenhuma mensagem
```

O arquivo só **define** a aplicação (a variável `app`). Quem a **serve** — fica escutando a porta e
entrega cada pedido à função certa — é o **uvicorn**: `uvicorn passo01_ola:app` = *"no módulo
`passo01_ola`, a variável `app`"* ("file:instance" [Adeshina, p33]).

| Sintoma | Causa | Correção |
|---------|-------|----------|
| `python arquivo.py` termina calado | o Python não é servidor | `uvicorn arquivo:app --reload` |
| `Error loading ASGI app. Could not import module "main"` | rodou o `uvicorn` de outra pasta | `cd` para a pasta do arquivo |
| (no demo) `ModuleNotFoundError: No module named 'src'` | rodou de dentro de `api/` | rode da pasta `painel_ods_brasil/`: `uvicorn api.main:app` |
| `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)` | já há um servidor na porta — às vezes um **processo órfão** de uma sessão anterior | **Ctrl+C** no terminal antigo; se não houver: `netstat -ano \| findstr :8000` e `taskkill /PID <número> /F` |

## Passo 2 · o tipo é a guarda (🐛 tropeço da v9)

| Pedido | Sem tipo (`def ranking(ano)`) | Com tipo (`ano: int = Path(ge=1988)`) |
|--------|:----------------------------:|:-------------------------------------:|
| `/…/ranking/2024` | **200 · 0 linhas** (`ano` chegou como `str`) | 200 · 9 linhas (PA 2.395 km² à frente) |
| `/…/ranking/abc` | 200 · 0 linhas | **422** · *"Input should be a valid integer"* |
| `/…/ranking/1950` | 200 · 0 linhas | **422** · *"greater than or equal to 1988"* |

A rota **sem** tipo nunca dá erro — e nunca dá dado. É o *"200 não quer dizer que veio o dado"* da
Aula 10, agora do lado de quem **serve**. E `uf: UfAmazonia` (um `Literal` com as 9 UFs) recusa `ZZ` e
`pa` com 422 **e a lista do que vale** — e vira um **menu** no `/docs`.

## Passo 3 · consulta, e a ordem das rotas (🐛 tropeço da v9)

| Pedido | Status | Resultado |
|--------|:------:|-----------|
| `/desmatamento` | 200 | 36 linhas |
| `/desmatamento?desde=2024` | 200 | 18 linhas |
| `/desmatamento?desde=2024&limite=3` | 200 | 3 linhas |
| `/desmatamento?desde=1950` | 422 | *"greater than or equal to 1988"* |
| `/errado/desmatamento/total` | **422** | *"Input should be 'AC', 'AM', …"* — `total` casou com `{uf}` |
| `/certo/desmatamento/total` | 200 | 2022: 11.594 · 2023: 9.064 · 2024: 6.518 · 2025: 5.731 km² |

O FastAPI testa as rotas **na ordem em que foram declaradas**. **Caminho fixo antes de caminho com
parâmetro.** *(O livro não trata da ordem; a primeira versão da v9 caiu exatamente aqui.)*

## Passo 4 · o outro lado

```
GET http://127.0.0.1:8000/desmatamento?desde=2024&limite=3  ->  200
   2024  AC      449 km²
   2024  AM     1223 km²
   2024  AP       27 km²

GET http://127.0.0.1:8000/desmatamento?desde=1950  ->  422
   recusado: ['query', 'desde'] — Input should be greater than or equal to 1988
```

O `requests` monta o `?desde=2024&limite=3` a partir do dicionário `params`. E o 422 não é um
mistério: o `detail` diz **onde** (`['query', 'desde']`) e **por quê**.

## ⚠️ Três avisos de sala (todos medidos)

- **O `/docs` precisa de internet no navegador.** A página carrega o Swagger de `cdn.jsdelivr.net`. Com
  o acesso externo bloqueado, ela fica **em branco** — e a API continua respondendo normalmente em
  `http://127.0.0.1:8000/...`. Sem internet, teste pelo navegador direto na rota, ou pelo passo 4.
- **No Windows PowerShell 5.1, `curl` não é o curl.** É um apelido do `Invoke-WebRequest`, e ele mostra
  `"Olá"` como `"OlÃ¡"` (a resposta é UTF-8; o PowerShell 5.1 a lê como outra codificação). Use
  **`curl.exe`**, o navegador, o `/docs` ou o passo 4.
- **O `--reload` só funciona num terminal de verdade.** Ele reinicia o servidor a cada arquivo `.py`
  salvo. Rode o `uvicorn` no terminal do VS Code ou no PowerShell — não "em segundo plano".

## `def` ou `async def`?

O livro escreve todas as rotas com `async def`, sem explicar por quê [Adeshina, p32]. **Use `def`.**
Medido aqui, com uma rota que faz um trabalho que bloqueia (como ler um arquivo ou chamar o
`requests`) por 2 s:

| 4 pedidos ao mesmo tempo | Tempo total |
|--------------------------|------------:|
| rota `async def` com trabalho que bloqueia | **8,0 s** (um depois do outro) |
| rota `def` com o mesmo trabalho | **2,0 s** (o FastAPI roda `def` em paralelo) |

`async def` só ajuda quando **tudo** lá dentro é assíncrono (`await`). Sem saber, `def`.

## Números medidos (não estimados)

| Onde | Medição (06/10/2026 · FastAPI 0.142 · Pydantic 2.13 · uvicorn 0.52 · Python 3.13) |
|------|----------------------------------------------------------------------------------|
| `python passo01_ola.py` | termina em ~1,6 s (até ~10 s na 1ª vez, importando do Google Drive), código 0, sem mensagem |
| Passo 2 | sem tipo: `ranking/2024` → 200 · 0 linhas · `tipo_recebido = str`; com tipo: 9 linhas |
| Passo 3 | 36 · 18 · 3 linhas; `/errado/desmatamento/total` → 422; `/certo/…` → 4 totais |
| Passo 4 sem API no ar | mensagem *"Não há API escutando em 127.0.0.1:8000…"*, código 1 |
| `/docs` sem acesso externo | 0 blocos de rota, página em branco; a API responde |
| `async def` × `def` (4 pedidos, 2 s cada) | 8,0 s × 2,0 s (duas rodadas, iguais) |
