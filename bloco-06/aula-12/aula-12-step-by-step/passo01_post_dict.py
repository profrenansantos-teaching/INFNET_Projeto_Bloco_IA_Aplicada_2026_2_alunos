"""
Passo 1 — o primeiro POST: o corpo como `dict` (Aula 12 · subcompetência 3.4).

    uvicorn passo01_post_dict:app --reload        e abra  http://127.0.0.1:8000/docs

É o primeiro POST do livro [Adeshina, p37]: `async def add_todo(todo: dict)`. Funciona —
e aceita QUALQUER coisa. Experimente no /docs (POST /relatos → Try it out):

    {"uf": "PA", "texto": "Fumaça na estrada"}      -> 200
    {"uf": 123}                                     -> 200   (UF número?)
    {}                                              -> 200   (relato vazio?)
    {"nome": "Maria", "telefone": "91 9999-0000"}   -> 200   (dado pessoal, guardado)

O próprio livro diz o problema: "an empty dictionary could've also been sent without
returning any error" [Adeshina, p41]. O passo 2 resolve.
"""

from fastapi import FastAPI

app = FastAPI(title="Passo 1 — POST com dict (aceita tudo)")

relatos = []   # na memória, como o todo_list do livro — o passo 3 mostra o problema disto


@app.post("/relatos")
def receber(relato: dict):
    relatos.append(relato)
    return {"mensagem": "Relato recebido.", "total": len(relatos)}


@app.get("/relatos")
def listar():
    return relatos
