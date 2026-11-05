"""
API do Painel ODS Brasil — v10 (Aula 12: a API recebe, valida e se organiza; subcompetência 3.4)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v9 PARA A v10:
  · a API passa a RECEBER: POST /relatos, com o corpo validado por um modelo Pydantic
    (api/modelos.py) — e GET /relatos para consultar o que chegou;
  · as rotas saíram deste arquivo para api/rotas/, uma por assunto, cada uma num
    APIRouter. Este arquivo virou um ROTEADOR: cria a aplicação, diz o que ela é e
    INCLUI os routers — como o app.py do painel, desde a Aula 9, inclui as páginas;
  · cada rota ganhou um título (summary=). Na v9, o /docs as chamava de "Serie Da Uf"
    e "Apresentacao" — o FastAPI tira o título do nome da função.

POR QUE APIRouter, SE AS SETE ROTAS DA v9 FUNCIONAVAM NUM ARQUIVO SÓ:
  funcionavam — o livro sugere que não [Adeshina, p36], e não é isso: uma instância
  FastAPI() serve quantas rotas você declarar (a v9 servia sete). O motivo é ORGANIZAÇÃO:
  "The APIRouter class encourages modularity and organization of application routing and
  logic." [Adeshina, p36]. Um assunto, um arquivo — a regra "uma pergunta, uma página" da
  Aula 9, do lado da API.

Como rodar (da pasta painel_ods_brasil/, com o ambiente de requirements-api.txt):
    uvicorn api.main:app --reload            ->  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from api.rotas import desmatamento, noticias, relatos
from src.desmatamento import metadados_desmatamento
from src.noticias import metadados

VERSAO = "v10 — Aula 12"

app = FastAPI(
    title="API do Painel ODS Brasil",
    version=VERSAO,
    description=(
        "Os dados do **Painel ODS Brasil** para outros programas — e uma porta de entrada para "
        "**relatos de campo**.\n\n"
        "- **Consulta (GET):** desmatamento anual por UF da Amazônia Legal (INPE/PRODES, "
        "**CC BY-SA 4.0**) e notícias da Agência Brasil (**CC BY 3.0 BR**). Toda resposta traz a "
        "fonte e a licença.\n"
        "- **Envio (POST):** `/relatos` recebe um relato — UF, categoria e texto —, valida e grava. "
        "**Não envie dados pessoais:** campos além dos três são recusados.\n\n"
        "Roda localmente: `uvicorn api.main:app --reload`, da pasta do projeto."
    ),
)


@app.get("/", tags=["sobre"], summary="O que esta API serve")
def apresentacao():
    """A versão, onde está a documentação e as rotas disponíveis."""
    return {
        "api": "Painel ODS Brasil",
        "versao": VERSAO,
        "documentacao": "/docs",
        "rotas": [
            "GET /fontes",
            "GET /desmatamento",
            "GET /desmatamento/total",
            "GET /desmatamento/ranking/{ano}",
            "GET /desmatamento/{uf}",
            "GET /noticias",
            "GET /relatos",
            "POST /relatos",
        ],
    }


@app.get("/fontes", tags=["sobre"], summary="Procedência e licença de cada conjunto")
def fontes():
    """De onde vem cada conjunto de dados, quando foi coletado e sob qual licença."""
    return [
        {"conjunto": "desmatamento", **metadados_desmatamento()},
        {"conjunto": "noticias", **metadados()},
        {"conjunto": "relatos", "origem": "enviados por pessoas pela rota POST /relatos",
         "aviso": "não verificado pelo projeto; não versionado"},
    ]


# Os routers: um por assunto. A ordem aqui não importa — os caminhos não se sobrepõem.
app.include_router(desmatamento.router)
app.include_router(noticias.router)
app.include_router(relatos.router)
