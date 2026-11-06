"""
Passo 2 · Carregar UMA vez, quando a API sobe — o lifespan (Aula 16 · B3)

"The most compute-efficient strategy for loading models in FastAPI is to use the application lifespan.
With this approach, you load models on application startup and unload them on shutdown." [Parandeh, p128]

O lifespan é uma função com UM yield: o que vem antes roda quando a API SOBE (antes do primeiro pedido);
o que vem depois, quando ela DESCE. O modelo carregado fica num dicionário, como no exemplo 3-16 do
livro [p129] — e a rota só o usa.

Compare com o passo 1: a SUBIDA ficou mais lenta (o terminal mostra a carga antes de "Application
startup complete"); cada PEDIDO ficou só com o tempo de pensar.

Rodar:  uvicorn passo02_lifespan:app                  (terminal 1)
        python cronometro.py analisar 3               (terminal 2)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from _motor import carregar, classificar

MOTORES = {}          # o modelo carregado mora aqui


@asynccontextmanager
async def lifespan(_: FastAPI):
    MOTORES["analise"] = carregar()             # quando a API SOBE — uma vez
    yield
    MOTORES.clear()                             # quando a API DESCE


app = FastAPI(title="Passo 2 — o modelo carregado uma vez", lifespan=lifespan)


class Pedido(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


@app.get("/saude")
def saude():
    return {"ok": True}


@app.post("/processar_texto")
def processar_texto(pedido: Pedido):
    return classificar(pedido.texto, MOTORES["analise"])    # só usa
