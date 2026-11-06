"""
Os erros da API — o formato, a documentação e a rede de segurança. Painel ODS Brasil, v12 (Aula 14).

"Errors in FastAPI are handled by raising an exception using FastAPI's HTTPException class."
[Adeshina, p65]

TRÊS PEÇAS:
  · Erro — o formato de TODO erro que a própria API levanta: {"detail": "uma frase"}. É o
    formato do HTTPException [Adeshina, p68]; o modelo existe para o /docs MOSTRAR os erros
    de cada rota (responses=). Sem ele, o 404 aparece no /docs como "Undocumented" — a
    figura 3.2 do livro [p68] mostra exatamente isso;
  · erro() — atalho para o responses= de cada rota: {404: erro("…")};
  · erro_inesperado() — a REDE DE SEGURANÇA, para o que ninguém previu.

🐛 Tropeço real da v12: o arquivo data/relatos/relatos.csv foi aberto no Excel e salvo de
   novo — com ";" no lugar de "," (o padrão do Excel em português). O GET /relatos passou a
   falhar com KeyError: 'id', e o cliente recebeu um 500 em TEXTO PURO ("Internal Server
   Error"). Um programa que fazia r.json() quebrou com JSONDecodeError; o painel v11 mostrou
   os 5 relatos FICTÍCIOS no lugar dos reais, e a explicação ficou numa legenda ("a API
   falhou (HTTPError)"). Com a rede de segurança, o 500 vira JSON, com um CÓDIGO; o
   terminal mostra o mesmo código e o traceback. Ao usuário, a frase; ao log, o traceback.

E o 422? Continua o do FastAPI: {"detail": [ {loc, msg, type}, … ]} — uma LISTA, um item por
campo. Por isso o cliente decide pelo STATUS como ler o corpo: 422 → lista; os outros → frase.
"""

import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# O mesmo logger que o uvicorn usa para os erros: a linha aparece no terminal da API.
log = logging.getLogger("uvicorn.error")


class Erro(BaseModel):
    """O corpo de todo erro levantado pela API (404, 409, 500, 503)."""

    detail: str = Field(description="O que aconteceu — e, quando houver, o que fazer.")


def erro(descricao: str) -> dict:
    """Uma entrada do responses= de uma rota: o /docs passa a listar este erro, com o formato."""
    return {"model": Erro, "description": descricao}


def erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
    """A rede de segurança: qualquer exceção que nenhuma rota tratou.

    Ao cliente: 500, em JSON, com uma frase e um código — nunca o traceback (ele pode
    conter caminhos de arquivo, nomes de colunas, pedaços de dado). Ao terminal: o mesmo
    código, a rota e o erro. O traceback completo vem logo abaixo, impresso pelo uvicorn.
    """
    codigo = uuid.uuid4().hex[:8]
    log.error("Erro inesperado [%s] em %s %s — %s: %s",
              codigo, request.method, request.url.path, type(exc).__name__, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno na API (código {codigo}). Avise quem mantém a API e informe o código."},
    )
