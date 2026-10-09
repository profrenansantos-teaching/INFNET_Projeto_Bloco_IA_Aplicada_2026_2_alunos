"""
Passo 2 — parâmetros de CAMINHO, e por que o TIPO é a guarda (Aula 11 · subcompetência 3.4).

    uvicorn passo02_tipos:app --reload        e abra  http://127.0.0.1:8000/docs

Tudo o que chega numa URL é TEXTO. "2024", no endereço, é a palavra "2024" — não
o número 2024. Quem converte é o FastAPI, olhando o tipo que você declarou. Sem
tipo, nada é convertido. Compare as duas rotas de ranking:

    /sem_tipo/ranking/2024   -> 200 e lista VAZIA     (o filtro compara "2024" com 2024)
    /ranking/2024            -> 200 e as 9 UFs
    /ranking/abc             -> 422  "Input should be a valid integer…"
    /ranking/1950            -> 422  "Input should be greater than or equal to 1988"
    /serie/PA                -> 200 e os 4 anos do Pará
    /serie/ZZ   e  /serie/pa -> 422  com a lista das 9 UFs que valem

Conhecido da Aula 2: lá, o id do IBGE vinha como texto e o convertíamos à mão
(`int(s["localidade"]["id"])`). Aqui, o tipo faz isso por nós — E recusa o que
não converte, antes de a função rodar.
"""

from typing import Literal

from fastapi import FastAPI, Path

from _dados import DESMATAMENTO, LICENCA

app = FastAPI(title="Passo 2 — tipos nos parâmetros de caminho")

# As 9 UFs da Amazônia Legal: as únicas que o PRODES publica.
UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]


# 🐛 SEM o tipo. Roda, responde 200 — e sempre vazio. Nenhum erro, nenhum aviso.
@app.get("/sem_tipo/ranking/{ano}")
def ranking_sem_tipo(ano):
    do_ano = [d for d in DESMATAMENTO if d["ano"] == ano]      # "2024" == 2024 -> False
    return {"ano_recebido": ano, "tipo_recebido": type(ano).__name__, "linhas": len(do_ano), "dados": do_ano}


# ✅ COM o tipo. "2024" vira 2024; "abc" e 1950 são recusados com 422.
@app.get("/ranking/{ano}")
def ranking(ano: int = Path(ge=1988, description="O PRODES começa em 1988.")):
    do_ano = sorted((d for d in DESMATAMENTO if d["ano"] == ano), key=lambda d: d["area_km2"], reverse=True)
    return {"ano": ano, "licenca": LICENCA, "linhas": len(do_ano), "dados": do_ano}


# ✅ Um tipo que só aceita 9 valores: o /docs mostra um MENU com as nove UFs.
@app.get("/serie/{uf}")
def serie(uf: UfAmazonia):
    da_uf = [d for d in DESMATAMENTO if d["uf"] == uf]
    return {"uf": uf, "licenca": LICENCA, "linhas": len(da_uf), "dados": da_uf}
