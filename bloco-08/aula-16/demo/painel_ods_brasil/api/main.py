"""
API do Painel ODS Brasil — v14 (Aula 16: o modelo de linguagem atrás da rota do TP4; subcompetência 4.4)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v13 PARA A v14:
  · o POST /processar_texto passou a ser respondido por um MODELO DE LINGUAGEM LOCAL — o que a
    Aula 15 escolheu, medindo (src/analisador_llm.py) —, no MESMO contrato da Aula 13;
  · o modelo é carregado UMA vez, quando a API sobe: o `lifespan` abaixo. "With this approach,
    you load models on application startup and unload them on shutdown." [Parandeh, p128];
  · se a carga falhar (o modelo não foi baixado: python -m src.baixar_modelo), a API sobe
    mesmo assim, e só a análise responde 503.
  (A v13, Aula 15, não mudou a API: escolheu o modelo — src/ficha_modelo.py, src/bancada.py.)

O QUE MUDOU DA v11 PARA A v12:
  · cada falha prevista tem o seu status, com HTTPException e uma frase em `detail`:
      404 — o recurso pedido não existe (ranking de 2026; relato nº 99);
      409 — o pedido conflita com o que já existe (o mesmo relato duas vezes em 10 min);
      503 — falta algo no servidor (o motor de análise não carregou; a coleta não está aqui);
    e cada rota DECLARA os seus erros (responses=) — o /docs deixa de mostrá-los como
    "Undocumented", como na figura 3.2 do livro [Adeshina, p68];
  · a REDE DE SEGURANÇA (api/erros.py): qualquer exceção que nenhuma rota tratou vira um
    500 em JSON, com um código — e o mesmo código no terminal, junto do traceback;
  · GET /relatos/{id}: um relato pelo número (404 se não houver).

"A 400 status code shouldn't be returned for a server error. Likewise, a 200 status code
shouldn't be returned for a failed request operation." [Adeshina, p62]

O QUE MUDOU DA v10 PARA A v11 (Aula 13):
  · toda rota declara o que DEVOLVE (response_model=, api/respostas.py); POST /relatos
    responde 201; a rota do TP4, POST /processar_texto, devolve um ResultadoAnalise.

Como rodar (da pasta painel_ods_brasil/, com o ambiente de requirements-api.txt):
    python -m src.baixar_modelo              (uma vez, com internet: ~3,1 GB)
    uvicorn api.main:app --reload            ->  http://127.0.0.1:8000/docs
  A API leva alguns segundos para subir: é o modelo indo do disco para a memória.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.erros import erro, erro_inesperado
from api.respostas import Apresentacao, Fonte
from api.rotas import analise, desmatamento, noticias, relatos
from src.desmatamento import metadados_desmatamento
from src.noticias import metadados

VERSAO = "v14 — Aula 16"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """O que acontece quando a API SOBE (antes do yield) e quando DESCE (depois dele).

    O modelo é carregado aqui, antes do primeiro pedido — e não dentro da rota, a cada pedido.
    É o padrão do exemplo 3-16 do livro [Parandeh, p129]. (O livro também mostra a forma antiga,
    @app.on_event("startup"), que ele mesmo chama de legada [p130].)
    """
    analise.carregar_na_subida()      # se falhar, a API sobe sem o modelo (503 só na análise)
    yield
    analise.liberar_na_descida()

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
        "- **Análise (POST):** `/processar_texto` sugere a categoria de um texto. Quem analisa é um "
        "**modelo de linguagem local** (Qwen2.5-1.5B-Instruct, na CPU): leva alguns segundos.\n\n"
        "**Erros:** todo erro tem um status e um `detail`. **422** — o pedido não cumpre o contrato "
        "(`detail` é uma lista, um item por campo). **404** — não existe. **409** — conflita com o que "
        "já existe. **503** — falta algo no servidor. **500** — erro interno, com um código para "
        "informar a quem mantém a API.\n\n"
        "Roda localmente: `uvicorn api.main:app --reload`, da pasta do projeto."
    ),
    # Documenta o 500 em todas as rotas: qualquer uma pode falhar por um motivo imprevisto.
    responses={500: erro("Erro interno, com um código para informar a quem mantém a API.")},
    lifespan=lifespan,
)

# A rede de segurança: o que nenhuma rota tratou vira 500 em JSON, com código (api/erros.py).
app.add_exception_handler(Exception, erro_inesperado)


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
            "GET /relatos/{id}",
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
