"""
Rotas do desmatamento (PRODES/INPE) — Painel ODS Brasil, v11 (Aula 13; criadas na v9).

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
"""

from fastapi import APIRouter, Path, Query

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
router = APIRouter(prefix="/desmatamento", tags=["desmatamento"])


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
    """Taxa anual de desmatamento (km²) de cada UF da Amazônia Legal, no período pedido."""
    linhas = carregar_desmatamento()
    fim = _ate(ate, linhas)
    return _envelope([l for l in linhas if desde <= l["ano"] <= fim])


@router.get("/total", response_model=RespostaTotais, summary="Total da Amazônia Legal, por ano")
def desmatamento_total(desde: int = Query(1988, ge=1988), ate: int | None = Query(None)):
    """A soma das nove UFs em cada ano: a taxa da Amazônia Legal inteira."""
    linhas = carregar_desmatamento()
    fim = _ate(ate, linhas)
    return _envelope([t for t in total_por_ano(linhas) if desde <= t["ano"] <= fim])


@router.get("/ranking/{ano}", response_model=RespostaRanking, summary="Ranking das UFs num ano")
def ranking(ano: int = Path(ge=1988, description="Ano do ranking.")):
    """As UFs no ano escolhido, da que mais desmatou para a que menos desmatou.

    Ano sem dado (ex.: 2026, que o PRODES ainda não publicou) devolve `"linhas": 0` com
    status 200 — responder 404 é a Aula 14 (exceções HTTP).
    """
    return _envelope(ranking_do_ano(carregar_desmatamento(), ano))


@router.get("/{uf}", response_model=RespostaDesmatamento, summary="Série anual de uma UF")
def serie_da_uf(uf: UfAmazonia, desde: int = Query(1988, ge=1988), ate: int | None = Query(None)):
    """A série anual de uma UF da Amazônia Legal — a UF no caminho; o período, na consulta."""
    linhas = carregar_desmatamento()
    fim = _ate(ate, linhas)
    return _envelope([l for l in linhas if l["uf"] == uf and desde <= l["ano"] <= fim])
