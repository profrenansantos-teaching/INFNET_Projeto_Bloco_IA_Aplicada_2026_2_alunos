"""
Passo 1 — uma API que não diz o que devolve (Aula 13 · subcompetência 4.1).

    uvicorn passo01_sem_contrato:app --reload        e abra  http://127.0.0.1:8000/docs

É a v10, por dentro: cada rota devolve o que a função montou — e o /docs não sabe o quê. Abra cada
rota, role até "Responses": a resposta 200 aparece como "string". Para todas.

Agora seja o técnico da prefeitura, que vai escrever um programa para ler esta API:
  · GET /relatos   devolve uma lista de dicionários. Que campos? O /docs não diz.
  · GET /fontes    devolve uma lista — e cada item tem campos DIFERENTES (11, 6 e 3).
  · GET /noticias  devolve "palavras" como TEXTO ("431"), porque o CSV não tem tipos.
  · POST /processar_texto devolve o que o motor calculou — inclusive as pontuações de TODAS as
    categorias e o texto sem acento. Se o programa da prefeitura passar a depender disso, a API
    nunca mais poderá trocar de motor sem quebrá-lo.

"The route returns all the content stored in the todos array." [Adeshina, p63]
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from _dados import METADADOS, NOTICIAS, RELATOS
from _motor import MOTOR, classificar

app = FastAPI(title="Passo 1 — sem contrato de resposta")


class PedidoAnalise(BaseModel):                      # a ENTRADA tem contrato desde a Aula 12…
    texto: str = Field(min_length=15, max_length=2000)


@app.get("/relatos")
def relatos():
    return RELATOS                                   # …a SAÍDA, ainda não


@app.get("/fontes")
def fontes():
    return [
        {"conjunto": "desmatamento", **METADADOS["desmatamento"]},
        {"conjunto": "noticias", **METADADOS["noticias"]},
        {"conjunto": "relatos", "origem": "enviados por pessoas", "aviso": "não verificados"},
    ]


@app.get("/noticias")
def noticias():
    return NOTICIAS


@app.post("/processar_texto")
def processar_texto(pedido: PedidoAnalise):
    return {"tipo_analise": "classificacao", "texto": pedido.texto, "motor": MOTOR, **classificar(pedido.texto)}
