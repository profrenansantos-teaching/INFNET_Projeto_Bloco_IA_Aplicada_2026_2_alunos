"""
Passo 2 — o corpo validado por um modelo Pydantic (Aula 12 · subcompetência 3.4).

    uvicorn passo02_post_pydantic:app --reload        e abra  http://127.0.0.1:8000/docs

"Models are created by subclassing Pydantic's BaseModel class." [Adeshina, p40]
O modelo é o CONTRATO do corpo: que campos, de que tipo, com que limites. O FastAPI confere
cada envio ANTES de a função rodar — e devolve 422 com TODOS os problemas de uma vez.

TRÊS ROTAS, TRÊS MODELOS — compare no /docs:

  POST /padrao   RelatoPadrao  — confere tipos e limites; campo A MAIS: descartado em SILÊNCIO
  POST /estrito  RelatoEstrito — igual, mas campo a mais é RECUSADO (422) — o da v10
  POST /livro    TodoDoLivro   — escrito como no livro (Pydantic 1): `class Config: schema_extra`

Experimente:
  {"uf": "Pará", "categoria": "fogo", "texto": "curto"}      -> 422, três erros juntos
  {}                                                         -> 422, três "Field required"
  {"uf": "PA", "categoria": "queimada", "texto": "Fumaça densa na estrada desde cedo.",
   "nome": "Maria", "telefone": "91 9999-0000"}
        em /padrao  -> 200 — e "nome"/"telefone" SUMIRAM da resposta (descartados)
        em /estrito -> 422 "Extra inputs are not permitted" (um erro para cada campo)

E no /docs: /estrito mostra um EXEMPLO de corpo; /livro, não. O `schema_extra` do livro
roda no Pydantic 2, avisa ("'schema_extra' has been renamed to 'json_schema_extra'") — e o
exemplo some. Olhe o terminal do uvicorn ao subir este passo: o aviso está lá.
"""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Passo 2 — POST validado por Pydantic")

SiglaUF = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]
Categoria = Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]


class RelatoPadrao(BaseModel):
    uf: SiglaUF
    categoria: Categoria
    texto: str = Field(min_length=15, max_length=500)


class RelatoEstrito(RelatoPadrao):
    model_config = ConfigDict(
        extra="forbid",                     # campo a mais: 422, e não descarte silencioso
        str_strip_whitespace=True,          # "   " não conta como texto
        json_schema_extra={"examples": [    # o exemplo do /docs — o "schema_extra" de hoje
            {"uf": "PA", "categoria": "queimada", "texto": "Fumaça densa na beira da estrada desde cedo."}
        ]},
    )


class TodoDoLivro(BaseModel):
    """Escrito como no livro [Adeshina, p51–54] — Pydantic 1."""
    id: int
    item: str

    class Config:
        schema_extra = {"example": {"id": 1, "item": "Example Schema!"}}


@app.post("/padrao")
def padrao(relato: RelatoPadrao):
    return {"recebido": relato.model_dump()}    # .model_dump(): o .dict() do Pydantic 1


@app.post("/estrito")
def estrito(relato: RelatoEstrito):
    return {"recebido": relato.model_dump()}


@app.post("/livro")
def livro(todo: TodoDoLivro):
    return {"recebido": todo.model_dump()}
