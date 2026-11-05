"""
Passo 4 — 🐛 o erro que ninguém previu: a rede de segurança (Aula 14 · tropeço real da v12).

    uvicorn passo04_erro_inesperado:app --reload        (e olhe o TERMINAL do uvicorn)

relatos_excel.csv é o arquivo de relatos depois de aberto no Excel e salvo de novo: o Excel em
português grava ";" no lugar de ",". O csv.DictReader procura "id" — e a coluna se chama
"id;recebido_em;uf;categoria;texto". KeyError: 'id'.

  1. Com REDE_DE_SEGURANCA = False: GET /relatos → 500, em TEXTO PURO ("Internal Server Error").
     Um programa que faz r.json() quebra com JSONDecodeError. O motivo está só no terminal.
  2. Com REDE_DE_SEGURANCA = True (salve o arquivo): GET /relatos → 500, em JSON, com um CÓDIGO:
        {"detail": "Erro interno na API (código 4d81bc39). Avise quem mantém a API e informe o código."}
     E no terminal, a MESMA etiqueta, a rota e o erro — e, logo abaixo, o traceback:
        ERROR:    Erro inesperado [4d81bc39] em GET /relatos — KeyError: 'id'

Ao usuário, a frase; ao log, o traceback. O traceback nunca vai para o cliente: ele pode conter
caminhos de arquivo, nomes de colunas, pedaços de dado.

(O livro não trata o 500 — só o cita como "internal server error" [Adeshina, p62]. O
@app.exception_handler / add_exception_handler vem da documentação oficial do FastAPI.)
"""

import csv
import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

REDE_DE_SEGURANCA = False     # mude para True e salve

app = FastAPI(title="Passo 4 — o erro inesperado")
log = logging.getLogger("uvicorn.error")
ARQUIVO = Path(__file__).parent / "relatos_excel.csv"


def erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
    codigo = uuid.uuid4().hex[:8]
    log.error("Erro inesperado [%s] em %s %s — %s: %s",
              codigo, request.method, request.url.path, type(exc).__name__, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno na API (código {codigo}). Avise quem mantém a API e informe o código."},
    )


if REDE_DE_SEGURANCA:
    app.add_exception_handler(Exception, erro_inesperado)    # qualquer exceção que nenhuma rota tratou


@app.get("/relatos")
def relatos():
    with ARQUIVO.open(encoding="utf-8", newline="") as f:
        return [{**linha, "id": int(linha["id"])} for linha in csv.DictReader(f)]   # KeyError: 'id'
