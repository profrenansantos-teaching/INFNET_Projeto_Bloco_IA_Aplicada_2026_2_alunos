"""
Passo 3 — parâmetros de CONSULTA, e a ORDEM das rotas (Aula 11 · subcompetência 3.4).

    uvicorn passo03_consulta_e_ordem:app --reload        e abra  http://127.0.0.1:8000/docs

PARTE A · consulta (o que vem depois do "?").
Todo parâmetro da função que NÃO aparece entre { } no caminho é de consulta. Com
valor padrão, ele é opcional:

    /desmatamento                       -> as 36 linhas (2022–2025)
    /desmatamento?desde=2024            -> 18 linhas
    /desmatamento?desde=2024&limite=3   -> 3 linhas
    /desmatamento?desde=1950            -> 422  (desde tem de ser ≥ 1988)
    /desmatamento?limite=abc            -> 422  (limite tem de ser inteiro)

Regra do curso: o QUE você quer (a UF, o ano do ranking) vai no CAMINHO;
o COMO você quer (desde quando, quantas linhas) vai na CONSULTA.

PARTE B · a ordem (🐛 tropeço real da v9).
O FastAPI testa as rotas NA ORDEM EM QUE FORAM DECLARADAS e usa a primeira cujo
desenho casa com o endereço. "/errado/desmatamento/{uf}" foi declarada antes de
"/errado/desmatamento/total" — e "total" casa com {uf}:

    /errado/desmatamento/total   -> 422  "Input should be 'AC', 'AM', …"  ("total" não é UF)
    /certo/desmatamento/total    -> 200  a soma das 9 UFs por ano

Caminho FIXO antes de caminho com PARÂMETRO.
"""

from typing import Literal

from fastapi import FastAPI, Query

from _dados import DESMATAMENTO, LICENCA

app = FastAPI(title="Passo 3 — consulta e ordem das rotas")

UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]


def _total_por_ano(linhas):
    soma = {}
    for d in linhas:
        soma[d["ano"]] = soma.get(d["ano"], 0.0) + d["area_km2"]
    return [{"ano": ano, "area_km2": area} for ano, area in sorted(soma.items())]


# ---------------------------------------------------------------- A · consulta
@app.get("/desmatamento")
def desmatamento(
    desde: int = Query(1988, ge=1988, description="Primeiro ano."),
    limite: int = Query(50, ge=1, le=100, description="Quantas linhas, no máximo."),
):
    linhas = [d for d in DESMATAMENTO if d["ano"] >= desde][:limite]
    return {"licenca": LICENCA, "linhas": len(linhas), "dados": linhas}


# ---------------------------------------------------------------- B · ordem ERRADA
@app.get("/errado/desmatamento/{uf}")
def errado_serie(uf: UfAmazonia):
    return [d for d in DESMATAMENTO if d["uf"] == uf]


@app.get("/errado/desmatamento/total")          # nunca é alcançada: {uf} casa antes
def errado_total():
    return _total_por_ano(DESMATAMENTO)


# ---------------------------------------------------------------- B · ordem CERTA
@app.get("/certo/desmatamento/total")           # o caminho fixo primeiro
def certo_total():
    return _total_por_ano(DESMATAMENTO)


@app.get("/certo/desmatamento/{uf}")
def certo_serie(uf: UfAmazonia):
    return [d for d in DESMATAMENTO if d["uf"] == uf]
