"""
Passo 1 — 200 vazio ou 404? (Aula 14 · subcompetência 4.2 · o tropeço da prefeitura)

    uvicorn passo01_200_ou_404:app --reload        e abra  http://127.0.0.1:8000/docs

"In our current application, retrieving a to-do that doesn't exist returns a 200 response status
code instead of a 404 response status code" [Adeshina, p66]
"Errors in FastAPI are handled by raising an exception using FastAPI's HTTPException class." [p65]

  GET /v11/ranking/{ano}   como a v11: o ano sem dado devolve 200 e "linhas": 0
  GET /ranking/{ano}       raise HTTPException(404, detail=…) — com a faixa de anos que existe
  GET /relatos/{id}        404 se o relato não existe
  GET /relatos?uf=         200 e lista vazia se nenhum relato for daquela UF — e está CERTO

Peça 2026 nas duas primeiras. O PRODES ainda não publicou a taxa de 2026: o 200 com zero linhas foi
lido pelo sistema da prefeitura como "nenhum desmatamento em 2026".

O CRITÉRIO (o mesmo da Aula 11): o CAMINHO identifica um recurso — se ele não existe, 404. A CONSULTA
recorta uma coleção — vazia é uma resposta válida para "quais?".

E no /docs: faça o "Try it out" de /ranking/2026. O 404 aparece como "Undocumented" — como na figura
3.2 do livro [p68]. A rota levanta o 404, mas não o DECLARA. O passo 2 declara.
"""

from fastapi import FastAPI, HTTPException, Query, status

from _dados import DESMATAMENTO, RELATOS

app = FastAPI(title="Passo 1 — 200 vazio ou 404?")


@app.get("/v11/ranking/{ano}")
def ranking_v11(ano: int):
    dados = sorted((l for l in DESMATAMENTO if l["ano"] == ano), key=lambda l: l["area_km2"], reverse=True)
    return {"linhas": len(dados), "dados": dados}                    # 2026 -> 200, "linhas": 0


@app.get("/ranking/{ano}")
def ranking(ano: int):
    dados = sorted((l for l in DESMATAMENTO if l["ano"] == ano), key=lambda l: l["area_km2"], reverse=True)
    if not dados:
        anos = [l["ano"] for l in DESMATAMENTO]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,                     # status.: nomes no lugar de números
            detail=f"O PRODES não tem a taxa de {ano}: a série vai de {min(anos)} a {max(anos)}.",
        )
    return {"linhas": len(dados), "dados": dados}


@app.get("/relatos")
def listar(uf: str | None = Query(None, min_length=2, max_length=2)):
    escolhidos = [r for r in RELATOS if uf is None or r["uf"] == uf]
    return {"linhas": len(escolhidos), "dados": escolhidos}            # AC -> 200, "linhas": 0 — certo


@app.get("/relatos/{id_relato}")
def um_relato(id_relato: int):
    for r in RELATOS:
        if r["id"] == id_relato:
            return r
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Não há relato nº {id_relato}.")
