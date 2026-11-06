"""
Passo 5 · O modelo dentro do contrato: "Chuveiro" não é categoria (Aula 16 · B5)

O contrato da Aula 13 promete uma categoria DA LISTA e uma confiança de 0 a 1. Um LLM, deixado escrever,
escreve o que quiser.

🐛 Tropeço real (bancada da Aula 15): com o prompt simples, o Qwen2.5-0.5B respondeu "Chuveiro" ao
   relato "Choveu sem parar desde sexta e a água já cobre o campo de futebol…". Com PONTUAR = False, a
   rota devolve o que o modelo ESCREVEU no campo `categoria` — e o response_model, que só aceita as
   seis, confere: 500 (ResponseValidationError, no terminal). A promessa quebrada da Aula 13, agora
   quebrada pelo modelo. E a confiança? Um texto escrito não traz número nenhum.

A saída: não deixar o modelo escrever. Com PONTUAR = True, olhamos UMA vez a próxima palavra que ele
diria e ficamos com a probabilidade das seis categorias (o começo de cada nome). A resposta é SEMPRE
uma delas — e a probabilidade é a confiança. (É o que o demo faz: src/analisador_llm.py.)

⚠️ Confiança do modelo não é chance de acerto: no banco de provas, o 1.5B errou um relato com 1,00.

Rodar:  uvicorn passo05_contrato:app                  (terminal 1)
        /docs → POST /processar_texto com o relato acima (terminal 1 mostra o 500 com PONTUAR = False)
"""

from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from _motor import carregar, classificar, escrever

PONTUAR = False       # False: o modelo ESCREVE a categoria · True: pontuamos as seis

MOTORES = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    MOTORES["analise"] = carregar()
    yield
    MOTORES.clear()


app = FastAPI(title="Passo 5 — o modelo dentro do contrato", lifespan=lifespan)


class Pedido(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


class Resultado(BaseModel):
    categoria: Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo"]
    confianca: float | None = Field(ge=0, le=1)


@app.post("/processar_texto", response_model=Resultado)
def processar_texto(pedido: Pedido):
    motor = MOTORES["analise"]
    if PONTUAR:
        return classificar(pedido.texto, motor)
    resposta = escrever(pedido.texto, motor)
    return {"categoria": resposta.lower(), "confianca": None}     # 🐛 o que ele escreveu, como veio
