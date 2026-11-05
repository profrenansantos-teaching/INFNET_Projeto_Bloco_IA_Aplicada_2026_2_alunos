"""
Passo 3 — 🐛 quando a API quebra a própria promessa: 500 (Aula 13 · tropeços reais da v11).

    uvicorn passo03_promessa_quebrada:app --reload        (e olhe o TERMINAL do uvicorn)

O response_model CONFERE o que a função devolve. Se não cumprir, quem errou foi a API — e a
resposta é 500 Internal Server Error, em texto puro. O motivo NÃO vai para o cliente: está no
terminal do uvicorn, como ResponseValidationError. Leia o terminal.

  GET /relatos-v1   🐛 o modelo de ENTRADA da Aula 12 (Relato, extra="forbid") usado na resposta.
                       Cada relato gravado tem "id" e "recebido_em" — que a entrada PROÍBE.
                       Terminal: extra_forbidden em ('response', 0, 'id').
  GET /noticias-v1  🐛 "publicado_em: datetime". O dado é "02/09/2026 08:16" — o Pydantic não lê
                       esse formato como data. Terminal: datetime_from_date_parsing.
  GET /relatos      ✅ RelatoGravado — o contrato de SAÍDA.
  GET /noticias     ✅ publicado_em: str — prometa só o que o seu dado cumpre.

Compare com o 422 da Aula 12: lá, o "loc" começava com "body" — o CLIENTE mandou errado. Aqui
começa com "response" — a API respondeu errado.
"""

from datetime import datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from _dados import NOTICIAS, RELATOS

app = FastAPI(title="Passo 3 — a promessa quebrada (500)")

Categoria = Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]


class Relato(BaseModel):                       # a ENTRADA (Aula 12): o que a API aceita receber
    model_config = ConfigDict(extra="forbid")
    uf: str
    categoria: Categoria
    texto: str = Field(min_length=15, max_length=500)


class RelatoGravado(BaseModel):                # a SAÍDA: o relato como a API o GUARDOU
    id: int
    recebido_em: str
    uf: str
    categoria: Categoria
    texto: str


class NoticiaV1(BaseModel):
    titulo: str
    publicado_em: datetime                     # 🐛 a promessa que o dado não cumpre


class Noticia(BaseModel):
    titulo: str
    publicado_em: str = Field(description="dd/mm/aaaa hh:mm")


@app.get("/relatos-v1", response_model=list[Relato])
def relatos_v1():
    return RELATOS


@app.get("/noticias-v1", response_model=list[NoticiaV1])
def noticias_v1():
    return NOTICIAS


@app.get("/relatos", response_model=list[RelatoGravado])
def relatos():
    return RELATOS


@app.get("/noticias", response_model=list[Noticia])
def noticias():
    return NOTICIAS
