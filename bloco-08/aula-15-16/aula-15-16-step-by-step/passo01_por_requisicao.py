"""
Passo 1 · O modelo carregado A CADA PEDIDO (Aula 16 · B3)

Este é o primeiro exemplo do livro, trazido para o nosso contrato: a função da rota CARREGA o modelo
e depois o usa [Parandeh, p92, exemplo 3-2]. Funciona — e o próprio autor avisa:
  "the model is loaded and unloaded onto memory every time a request is processed. Having to
   load/unload a large model to and from memory is slow and I/O blocking." [Parandeh, p96]

🐛 Rode e meça. Cada análise paga a carga inteira de novo — com o modelo PEQUENO dos passos. O do
   demo (1.5B) leva ~8 s só para carregar.

Rodar:  uvicorn passo01_por_requisicao:app            (terminal 1)
        python cronometro.py analisar 3               (terminal 2)
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from _motor import carregar, classificar

app = FastAPI(title="Passo 1 — o modelo carregado a cada pedido")


class Pedido(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


@app.get("/saude")
def saude():
    return {"ok": True}


@app.post("/processar_texto")
def processar_texto(pedido: Pedido):
    motor = carregar()                          # 🐛 a cada pedido: do disco para a memória, de novo
    return classificar(pedido.texto, motor)
