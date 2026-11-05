"""
Passo 2 — um status para cada falha, e cada falha declarada (Aula 14 · subcompetência 4.2).

    uvicorn passo02_status_certo:app --reload        e abra  http://127.0.0.1:8000/docs

Três respostas 4xx — três coisas diferentes que o cliente precisa saber:

  422  o pedido não cumpre o CONTRATO (o modelo)           — automático, desde a Aula 12
  404  o que se pediu NÃO EXISTE                           — GET /relatos/99
  409  o pedido está certo, mas CONFLITA com o que existe  — o mesmo relato duas vezes em 10 min

"A 400 status code shouldn't be returned for a server error. Likewise, a 200 status code shouldn't
be returned for a failed request operation." [Adeshina, p62]

O 409 é o que o modelo NÃO PODE ver: ele confere o corpo, e o corpo está certo. Quem sabe que já existe
um relato igual é quem guarda. (O livro usa o 409 no cadastro de um usuário que já existe [Adeshina, p96].)

DECLARAR (responses=): cada rota diz, no decorador, os erros que pode devolver — e o /docs passa a
listá-los com o formato. Compare com o passo 1, onde o 404 aparecia como "Undocumented".

E GET /lento: um "motor" que leva 5 s — o tamanho de uma resposta de LLM numa CPU (Etapa 8). É para o
passo 5, que mostra o que o CLIENTE faz quando a resposta não vem a tempo.
"""

import time
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Passo 2 — 404, 409, 422: o status certo, declarado")
JANELA = timedelta(minutes=10)
guardados = []      # na memória — o armazenamento foi a Aula 12; aqui, o assunto são os status


class Relato(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    uf: str = Field(min_length=2, max_length=2)
    categoria: str
    texto: str = Field(min_length=15, max_length=500)


class RelatoGravado(BaseModel):
    id: int
    recebido_em: str
    uf: str
    categoria: str
    texto: str


class Erro(BaseModel):
    """O corpo dos erros que a API levanta: {"detail": "uma frase"} — o formato do HTTPException."""
    detail: str


@app.post(
    "/relatos",
    status_code=status.HTTP_201_CREATED,
    response_model=RelatoGravado,
    responses={409: {"model": Erro, "description": "O mesmo relato já chegou há menos de 10 minutos."}},
)
def enviar(relato: Relato):
    agora = datetime.now()
    for anterior in reversed(guardados):
        if agora - anterior["quando"] > JANELA:
            break
        if (anterior["uf"], anterior["categoria"], anterior["texto"]) == (relato.uf, relato.categoria, relato.texto):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Este relato já foi recebido: nº {anterior['id']}, em {anterior['recebido_em']}.",
            )
    novo = {**relato.model_dump(), "id": len(guardados) + 1, "quando": agora,
            "recebido_em": agora.strftime("%d/%m/%Y %H:%M")}
    guardados.append(novo)
    return novo                       # "quando" fica no servidor: não está em RelatoGravado


@app.get(
    "/relatos/{id_relato}",
    response_model=RelatoGravado,
    responses={404: {"model": Erro, "description": "Não há relato com este número."}},
)
def um_relato(id_relato: int):
    for r in guardados:
        if r["id"] == id_relato:
            return r
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Não há relato nº {id_relato}.")


@app.get("/lento")
def lento():
    time.sleep(5)                     # um motor lento (passo 5)
    return {"mensagem": "Respondi — 5 s depois."}
