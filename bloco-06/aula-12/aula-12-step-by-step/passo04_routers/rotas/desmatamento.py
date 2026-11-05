"""Router do desmatamento (passo 4). O prefixo e o grupo, declarados UMA vez."""

from typing import Literal

from fastapi import APIRouter, Query

from _dados import DESMATAMENTO, LICENCA

# prefix: todas as rotas daqui começam com /desmatamento · tags: o grupo no /docs
router = APIRouter(prefix="/desmatamento", tags=["desmatamento"])

UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]


# "" e não "/": com "/", o endereço viraria /desmatamento/ — e um pedido a /desmatamento
# receberia um 307 (redirecionamento) antes da resposta. Experimente trocar e olhe o terminal.
@router.get("", summary="Todas as UFs, a partir de um ano")
def todas(desde: int = Query(2022, ge=1988)):
    linhas = [d for d in DESMATAMENTO if d["ano"] >= desde]
    return {"licenca": LICENCA, "linhas": len(linhas), "dados": linhas}


@router.get("/total", summary="Total da Amazônia Legal, por ano")       # fixo ANTES de {uf}
def total():
    soma = {}
    for d in DESMATAMENTO:
        soma[d["ano"]] = soma.get(d["ano"], 0.0) + d["area_km2"]
    return {"licenca": LICENCA, "dados": [{"ano": a, "area_km2": v} for a, v in sorted(soma.items())]}


@router.get("/{uf}", summary="Série de uma UF")
def serie(uf: UfAmazonia):
    linhas = [d for d in DESMATAMENTO if d["uf"] == uf]
    return {"licenca": LICENCA, "linhas": len(linhas), "dados": linhas}
