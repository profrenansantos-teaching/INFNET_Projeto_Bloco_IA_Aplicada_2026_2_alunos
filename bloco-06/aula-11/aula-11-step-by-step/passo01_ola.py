"""
Passo 1 — a menor API que existe (Aula 11 · subcompetência 3.3).

É o primeiro exemplo do livro [Adeshina, p32], com duas diferenças, de propósito:
  · `def` em vez de `async def` (o livro usa async em tudo, sem explicar por quê;
    sem saber, use `def` — ver o README);
  · em português.

COMO RODAR (desta pasta, com o ambiente da API ativo):
    uvicorn passo01_ola:app --reload
            ^^^^^^^^^^^ ^^^
            o MÓDULO    a VARIÁVEL que guarda a aplicação  ("arquivo:instância" [Adeshina, p33])

e abra no navegador:
    http://127.0.0.1:8000/          -> o JSON que a função devolve
    http://127.0.0.1:8000/docs      -> a documentação interativa, gerada sozinha

⚠️  `python passo01_ola.py` NÃO sobe nada. Experimente: o Python lê o arquivo,
    cria a variável `app`… e termina, sem erro e sem mensagem. Este arquivo só
    DEFINE a aplicação. Quem a SERVE — fica escutando a porta 8000 e entrega cada
    pedido à função certa — é o uvicorn.
"""

from fastapi import FastAPI

app = FastAPI()


# O decorador diz QUAL pedido esta função atende: o método GET, no caminho "/".
# O que ela devolve (um dicionário) o FastAPI transforma em JSON.
@app.get("/")
def ola():
    return {"mensagem": "Olá! Esta é a API do Painel ODS Brasil."}
