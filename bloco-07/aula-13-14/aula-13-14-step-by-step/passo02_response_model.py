"""
Passo 2 — a resposta ganha contrato: response_model (Aula 13 · subcompetência 4.1).

    uvicorn passo02_response_model:app --reload        e abra  http://127.0.0.1:8000/docs

"Response models serve as templates for returning data from an API route path." [Adeshina, p60]
"we can create a model containing the fields we want to be returned and add it to our route
definition using the response_model argument." [Adeshina, p63]

AS MESMAS QUATRO ROTAS DO PASSO 1. As funções devolvem exatamente o mesmo — e a resposta muda:

  · FILTRA   POST /processar_texto não manda mais "pontuacoes" nem "texto_normalizado";
             GET /fontes manda os mesmos 5 campos para os três conjuntos.
             (O livro mostra isso escondendo o "id" do to-do [Adeshina, p64–65].)
  · CONFERE  "palavras" sai como NÚMERO (431), não como texto ("431"): o modelo diz int, e o
             Pydantic converte o que dá para converter. O que não dá… é o passo 3.
  · DOCUMENTA  no /docs, "Responses" mostra os campos — e, no fim da página, os "Schemas".

DOIS JEITOS DE DECLARAR, o mesmo efeito (verificado):
  @app.get("/relatos", response_model=list[RelatoGravado])     <- o do livro; o que usamos no projeto
  def relatos() -> list[RelatoGravado]:                        <- a anotação de retorno (FastAPI recente)
A rota /noticias usa o segundo, para comparar no /docs. Se houver os dois, vale o response_model
— é o caso do livro, que mantém "-> dict" e acrescenta response_model= [Adeshina, p64].
"""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from _dados import METADADOS, NOTICIAS, RELATOS
from _motor import MOTOR, classificar

app = FastAPI(title="Passo 2 — response_model: filtra, confere, documenta")

Categoria = Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]


class PedidoAnalise(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


# ---------------------------------------------------------------- os modelos de RESPOSTA
class RelatoGravado(BaseModel):
    id: int
    recebido_em: str
    uf: str
    categoria: Categoria
    texto: str


class Fonte(BaseModel):
    conjunto: str
    site: str | None = None
    licenca: str | None = None
    coletado_em: str | None = None
    aviso: str | None = None


class Noticia(BaseModel):
    secao: str
    titulo: str
    publicado_em: str = Field(description="dd/mm/aaaa hh:mm — como a coleta grava")
    palavras: int
    url: str


class ResultadoAnalise(BaseModel):
    tipo_analise: Literal["classificacao"]
    texto: str
    categoria_sugerida: Categoria | None
    confianca: float = Field(ge=0, le=1)
    pistas: list[str]
    motor: str


# ---------------------------------------------------------------- as rotas (funções iguais às do passo 1)
@app.get("/relatos", response_model=list[RelatoGravado])
def relatos():
    return RELATOS


@app.get("/fontes", response_model=list[Fonte])
def fontes():
    return [
        {"conjunto": "desmatamento", **METADADOS["desmatamento"]},
        {"conjunto": "noticias", **METADADOS["noticias"]},
        {"conjunto": "relatos", "origem": "enviados por pessoas", "aviso": "não verificados"},
    ]


@app.get("/noticias")
def noticias() -> list[Noticia]:                     # a anotação de retorno: o mesmo efeito
    return NOTICIAS


@app.post("/processar_texto", response_model=ResultadoAnalise)
def processar_texto(pedido: PedidoAnalise):
    return {"tipo_analise": "classificacao", "texto": pedido.texto, "motor": MOTOR, **classificar(pedido.texto)}
