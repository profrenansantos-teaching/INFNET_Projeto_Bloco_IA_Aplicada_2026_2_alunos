"""
API do Painel ODS Brasil — v11 (Aula 13: a resposta também tem contrato; subcompetência 4.1)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v10 PARA A v11:
  · toda rota declara o que DEVOLVE: response_model=, com os modelos de api/respostas.py.
    Na v10 o /docs mostrava "string" como resposta de TODAS as rotas — e o técnico da
    prefeitura teve de adivinhar o formato (e errou no /fontes, que devolvia uma lista
    com três formatos diferentes dentro);
  · POST /relatos responde 201 (Created) — criou um relato. As consultas continuam 200;
  · a rota do TP4: POST /processar_texto (api/rotas/analise.py) — recebe um texto e devolve
    a análise num formato declarado (ResultadoAnalise). O motor, por enquanto, é um
    conjunto de regras (src/analisador.py); na Etapa 8, um LLM local, no MESMO formato.

"Response models serve as templates for returning data from an API route path."
[Adeshina, p60] — e, na prática (verificado), fazem três coisas: FILTRAM o que sai,
CONFEREM o que sai (500 se a API quebrar a própria promessa) e DOCUMENTAM no /docs.

O QUE MUDOU DA v9 PARA A v10 (Aula 12):
  · a API passou a RECEBER: POST /relatos, com o corpo validado por um modelo Pydantic;
  · as rotas saíram deste arquivo para api/rotas/, uma por assunto, cada uma num
    APIRouter. Este arquivo virou um ROTEADOR — como o app.py do painel, desde a Aula 9.

Como rodar (da pasta painel_ods_brasil/, com o ambiente de requirements-api.txt):
    uvicorn api.main:app --reload            ->  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from api.respostas import Apresentacao, Fonte
from api.rotas import analise, desmatamento, noticias, relatos
from src.desmatamento import metadados_desmatamento
from src.noticias import metadados

VERSAO = "v11 — Aula 13"

app = FastAPI(
    title="API do Painel ODS Brasil",
    version=VERSAO,
    description=(
        "Os dados do **Painel ODS Brasil** para outros programas, uma porta de entrada para "
        "**relatos de campo** e um **analisador de texto**.\n\n"
        "- **Consulta (GET):** desmatamento anual por UF da Amazônia Legal (INPE/PRODES, "
        "**CC BY-SA 4.0**) e notícias da Agência Brasil (**CC BY 3.0 BR**). Toda resposta traz a "
        "fonte e a licença.\n"
        "- **Envio (POST):** `/relatos` recebe um relato — UF, categoria e texto —, valida e grava "
        "(**201**). **Não envie dados pessoais:** campos além dos três são recusados.\n"
        "- **Análise (POST):** `/processar_texto` sugere a categoria de um texto. Motor atual: "
        "regras de palavras-chave (um LLM local na próxima etapa — no mesmo formato de resposta).\n\n"
        "Cada rota declara o **formato da resposta** — veja os *Schemas* no fim desta página.\n\n"
        "Roda localmente: `uvicorn api.main:app --reload`, da pasta do projeto."
    ),
)


@app.get("/", response_model=Apresentacao, tags=["sobre"], summary="O que esta API serve")
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
            "POST /processar_texto",
        ],
    }


@app.get("/fontes", response_model=list[Fonte], tags=["sobre"], summary="Procedência e licença de cada conjunto")
def fontes():
    """De onde vem cada conjunto de dados, quando foi coletado e sob qual licença.

    Os metadados de cada coleta têm campos diferentes (o do desmatamento guarda até quantos
    segundos a coleta levou). A resposta tem **um** formato para os três: `Fonte`.
    """
    # Devolvemos os metadados INTEIROS — e o response_model deixa passar só os campos de
    # Fonte. Na v10, esta rota publicava tudo o que o JSON da coleta tivesse.
    return [
        {"conjunto": "desmatamento", **metadados_desmatamento()},
        {"conjunto": "noticias", **metadados()},
        {"conjunto": "relatos", "aviso": "enviados por pessoas pela rota POST /relatos; não verificados; não versionados"},
    ]


# Os routers: um por assunto. A ordem aqui não importa — os caminhos não se sobrepõem.
app.include_router(desmatamento.router)
app.include_router(noticias.router)
app.include_router(relatos.router)
app.include_router(analise.router)
