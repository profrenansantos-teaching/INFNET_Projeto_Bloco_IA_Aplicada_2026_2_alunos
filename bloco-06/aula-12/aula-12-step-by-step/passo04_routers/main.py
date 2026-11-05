"""
Passo 4 — o main.py vira ROTEADOR: cada assunto num APIRouter (Aula 12 · subcompetência 3.4).

COMO RODAR — da pasta aula-12-step-by-step/ (e não de dentro desta):
    uvicorn passo04_routers.main:app --reload
            ^^^^^^^^^^^^^^^ ^^^^
            o pacote        o módulo   — como no projeto: uvicorn api.main:app

"The APIRouter class encourages modularity and organization of application routing and
logic." [Adeshina, p36]  E o main.py só faz três coisas: cria a aplicação, diz o que ela é,
e INCLUI os routers — como o app.py do painel, desde a Aula 9, inclui as páginas.

⚠️ O livro diz que, numa instância FastAPI(), "the application will be unable to run both
   routes, as uvicorn can only run one entry point" [Adeshina, p36]. Não é assim: a API da
   Aula 11 servia sete rotas numa instância só. Router é ORGANIZAÇÃO, não necessidade.
"""

from fastapi import FastAPI

from passo04_routers.rotas import desmatamento, relatos

app = FastAPI(title="Passo 4 — routers")


@app.get("/", summary="O que esta API serve")
def apresentacao():
    return {"rotas": ["GET /desmatamento", "GET /desmatamento/total", "GET /desmatamento/{uf}",
                      "GET /relatos", "POST /relatos"]}


app.include_router(desmatamento.router)
app.include_router(relatos.router)
