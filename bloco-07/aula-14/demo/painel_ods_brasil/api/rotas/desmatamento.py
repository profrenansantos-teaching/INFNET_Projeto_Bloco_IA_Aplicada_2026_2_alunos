"""
Rotas do desmatamento (PRODES/INPE) — Painel ODS Brasil, v12 (Aula 14; criadas na v9).

As mesmas quatro rotas da v9, agora num APIRouter: o prefixo "/desmatamento" e o grupo
("tags") são declarados UMA vez, aqui, em vez de repetidos em cada rota. O main.py as
inclui com uma linha.

Duas regras da v9 continuam valendo DENTRO do router:
  · caminho fixo antes de caminho com parâmetro ("/total" antes de "/{uf}");
  · o tipo é a guarda (ano: int, uf: UfAmazonia).

v11: cada rota declara o que DEVOLVE (response_model=, de api/respostas.py). O CSV da
coleta tem uma coluna "fonte" em TODA linha — 342 vezes a mesma frase, que a v10 mandava
inteira. O envelope já diz a fonte; o modelo da linha não tem "fonte", e ela fica no
servidor (medido: /desmatamento caiu de 34.311 para 20.631 bytes, −40%).

v12: o que NÃO EXISTE responde 404; o que FALTA no servidor responde 503.
  🐛 O sistema da prefeitura pediu GET /desmatamento/ranking/2026 — o PRODES ainda não
     publicou a taxa de 2026 — e recebeu 200, "linhas": 0. O relatório dela registrou
     "nenhum desmatamento em 2026". Um 200 vazio virou uma informação FALSA. Agora: 404,
     com a faixa de anos que existe. "A 200 status code shouldn't be returned for a failed
     request operation." [Adeshina, p62]
  🐛 Sem o CSV da coleta (um clone novo, uma coleta apagada), as rotas com período
     quebravam com ValueError ("min() iterable argument is empty") — 500. Agora: 503,
     com o que fazer. Não é o pedido que está errado; é o servidor que não tem o dado.
"""

from fastapi import APIRouter, HTTPException, Path, Query, status

from api.erros import erro
from api.respostas import (
    RespostaDesmatamento,
    RespostaRanking,
    RespostaTotais,
    UfAmazonia,
)
from src.desmatamento import (
    carregar_desmatamento,
    faixa_de_anos,
    metadados_desmatamento,
    ranking_do_ano,
    total_por_ano,
)

# As rotas abaixo escrevem "" e "/total" — e não "/" e "/total/". Com prefixo e "/", o
# endereço viraria "/desmatamento/", e um pedido a "/desmatamento" receberia um 307
# (redirecionamento) antes da resposta.
router = APIRouter(
    prefix="/desmatamento",
    tags=["desmatamento"],
    # Vale para as quatro rotas: todas dependem do CSV da coleta.
    responses={503: erro("Os dados do PRODES não foram coletados nesta máquina.")},
)


def _linhas() -> list[dict]:
    """As linhas da coleta — ou 503, se a coleta não está nesta máquina."""
    linhas = carregar_desmatamento()
    if not linhas:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Os dados do PRODES não foram coletados nesta máquina. "
                   "Rode a coleta (python -m src.coleta_dinamica) e tente de novo.",
        )
    return linhas


def _envelope(dados: list[dict]) -> dict:
    """A licença viaja com o dado (v9): fonte, licença e data da coleta em toda resposta."""
    meta = metadados_desmatamento()
    return {
        "fonte": meta.get("site", "INPE/PRODES"),
        "licenca": meta.get("licenca", ""),
        "coletado_em": meta.get("coletado_em", ""),
        "linhas": len(dados),
        "dados": dados,
    }


def _ate(ate: int | None, linhas: list[dict]) -> int:
    return ate if ate is not None else faixa_de_anos(linhas)[1]


@router.get("", response_model=RespostaDesmatamento, summary="Todas as UFs, no período")
def desmatamento(
    desde: int = Query(1988, ge=1988, description="Primeiro ano (o PRODES começa em 1988)."),
    ate: int | None = Query(None, description="Último ano. Sem ele, até o mais recente."),
):
    """Taxa anual de desmatamento (km²) de cada UF da Amazônia Legal, no período pedido.

    Período sem dado é uma resposta válida: **200**, `"linhas": 0` — a consulta recorta.
    """
    linhas = _linhas()
    fim = _ate(ate, linhas)
    return _envelope([l for l in linhas if desde <= l["ano"] <= fim])


@router.get("/total", response_model=RespostaTotais, summary="Total da Amazônia Legal, por ano")
def desmatamento_total(desde: int = Query(1988, ge=1988), ate: int | None = Query(None)):
    """A soma das nove UFs em cada ano: a taxa da Amazônia Legal inteira."""
    linhas = _linhas()
    fim = _ate(ate, linhas)
    return _envelope([t for t in total_por_ano(linhas) if desde <= t["ano"] <= fim])


@router.get(
    "/ranking/{ano}",
    response_model=RespostaRanking,
    responses={404: erro("O PRODES não tem a taxa deste ano.")},
    summary="Ranking das UFs num ano",
)
def ranking(ano: int = Path(ge=1988, description="Ano do ranking.")):
    """As UFs no ano escolhido, da que mais desmatou para a que menos desmatou.

    O ano está no CAMINHO: ele identifica um ranking. Ano sem dado (ex.: 2026, que o PRODES
    ainda não publicou) responde **404**, com a faixa de anos disponível — e não 200 com uma
    lista vazia, que um cliente leria como "zero desmatamento".
    """
    linhas = _linhas()
    dados = ranking_do_ano(linhas, ano)
    if not dados:
        primeiro, ultimo = faixa_de_anos(linhas)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"O PRODES não tem a taxa de {ano}: a série vai de {primeiro} a {ultimo}.",
        )
    return _envelope(dados)


@router.get("/{uf}", response_model=RespostaDesmatamento, summary="Série anual de uma UF")
def serie_da_uf(uf: UfAmazonia, desde: int = Query(1988, ge=1988), ate: int | None = Query(None)):
    """A série anual de uma UF da Amazônia Legal — a UF no caminho; o período, na consulta."""
    linhas = _linhas()
    fim = _ate(ate, linhas)
    return _envelope([l for l in linhas if l["uf"] == uf and desde <= l["ano"] <= fim])
