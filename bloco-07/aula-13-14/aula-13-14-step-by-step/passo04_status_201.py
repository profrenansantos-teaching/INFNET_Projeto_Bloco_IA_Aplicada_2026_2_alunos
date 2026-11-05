"""
Passo 4 — criou? 201. E o cliente que conferia "== 200" (Aula 13 · tropeço real da v11).

    uvicorn passo04_status_201:app --reload
    (noutro terminal, da mesma pasta)   python passo04_cliente.py

"we can declare the HTTP status code to override the default status code for successful
operations by adding the status_code argument to the decorator function" [Adeshina, p68]
"It is also important to note that the default status code for success is 200." [Adeshina, p68]

  POST /v1/relatos   status padrão: 200   (como na v10)
  POST /relatos      status_code=201 (Created) — o envio CRIOU um relato

Mudar 200 para 201 é certo — e é mudar o CONTRATO. O passo04_cliente.py é o programa da
prefeitura: ele conferia `r.status_code == 200`. Rode e veja o que ele diz para cada rota.
"""

from fastapi import FastAPI, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Passo 4 — 201 Created")
guardados = []      # na memória: aqui não importa onde se guarda (isso foi a Aula 12)


class Relato(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    uf: str = Field(min_length=2, max_length=2)
    categoria: str
    texto: str = Field(min_length=15, max_length=500)


class RelatoRecebido(BaseModel):
    mensagem: str
    id: int


@app.post("/v1/relatos", response_model=RelatoRecebido)
def enviar_v1(relato: Relato):
    guardados.append(relato.model_dump())
    return {"mensagem": "Relato recebido.", "id": len(guardados)}


@app.post("/relatos", status_code=status.HTTP_201_CREATED, response_model=RelatoRecebido)
def enviar(relato: Relato):
    guardados.append(relato.model_dump())
    return {"mensagem": "Relato recebido.", "id": len(guardados)}
