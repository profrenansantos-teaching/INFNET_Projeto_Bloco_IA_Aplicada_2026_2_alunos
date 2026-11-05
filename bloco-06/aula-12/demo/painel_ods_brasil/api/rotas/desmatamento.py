"""
Rotas do desmatamento (PRODES/INPE) — Painel ODS Brasil, v10 (Aula 12; criadas na v9).

As mesmas quatro rotas da v9, agora num APIRouter: o prefixo "/desmatamento" e o grupo
("tags") são declarados UMA vez, aqui, em vez de repetidos em cada rota. O main.py as
inclui com uma linha.

Duas regras da v9 continuam valendo DENTRO do router:
  · caminho fixo antes de caminho com parâmetro ("/total" antes de "/{uf}");
  · o tipo é a guarda (ano: int, uf: UfAmazonia).
"""

from typing import Literal

from fastapi import APIRouter, Path, Query

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

UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]


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


@router.get("", summary="Todas as UFs, no período")
def desmatamento(
    desde: int = Query(1988, ge=1988, description="Primeiro ano (o PRODES começa em 1988)."),
    ate: int | None = Query(None, description="Último ano. Sem ele, até o mais recente."),
):
    """Taxa anual de desmatamento (km²) de cada UF da Amazônia Legal, no período pedido."""
    linhas = carregar_desmatamento()
    fim = _ate(ate, linhas)
    return _envelope([l for l in linhas if desde <= l["ano"] <= fim])


@router.get("/total", summary="Total da Amazônia Legal, por ano")
def desmatamento_total(desde: int = Query(1988, ge=1988), ate: int | None = Query(None)):
    """A soma das nove UFs em cada ano: a taxa da Amazônia Legal inteira."""
    linhas = carregar_desmatamento()
    fim = _ate(ate, linhas)
    return _envelope([t for t in total_por_ano(linhas) if desde <= t["ano"] <= fim])


@router.get("/ranking/{ano}", summary="Ranking das UFs num ano")
def ranking(ano: int = Path(ge=1988, description="Ano do ranking.")):
    """As UFs no ano escolhido, da que mais desmatou para a que menos desmatou.

    Ano sem dado (ex.: um ano futuro) devolve `"linhas": 0` com status 200 — responder 404
    é assunto da Etapa 7.
    """
    return _envelope(ranking_do_ano(carregar_desmatamento(), ano))


@router.get("/{uf}", summary="Série anual de uma UF")
def serie_da_uf(uf: UfAmazonia, desde: int = Query(1988, ge=1988), ate: int | None = Query(None)):
    """A série anual de uma UF da Amazônia Legal — a UF no caminho; o período, na consulta."""
    linhas = carregar_desmatamento()
    fim = _ate(ate, linhas)
    return _envelope([l for l in linhas if l["uf"] == uf and desde <= l["ano"] <= fim])
