"""
Passo 3 · `async def` ou `def`? O modelo que travava a API inteira (Aula 16 · B4)

Até aqui, toda rota do curso foi `def`. A internet está cheia de exemplos com `async def` — "é mais
rápido". Para o modelo, NÃO é:

  · uma rota `async def` roda no LAÇO PRINCIPAL do servidor — o mesmo que atende TODOS os pedidos. O
    FastAPI confia que ela nunca bloqueia (que ela espera com `await`);
  · uma rota `def` o FastAPI roda numa THREAD À PARTE — o laço principal continua atendendo os outros.
  "when you declare handlers with async def, FastAPI trusts you with performing only nonblocking
   operations. When you break that trust… the event loop will be blocked" [Parandeh, p192]

O modelo pensando na CPU é bloquear: não há `await` nenhum ali.

🐛 Rode como está (TRAVAR = True) e use o modo "junto" do cronômetro: o GET /saude — que não tem nada a
   ver com o modelo — espera a análise acabar. Troque para False, suba de novo e repita.

(O próprio livro escorrega nisso: os exemplos 5-7 e 5-14 declaram `async def` e chamam a inferência
 local, síncrona, lá dentro [Parandeh, p197 e p215] — o contrário do aviso da p192.)

Rodar:  uvicorn passo03_async_trava:app               (terminal 1)
        python cronometro.py junto                    (terminal 2)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from _motor import carregar, classificar

TRAVAR = True         # True: a rota da análise é `async def` · False: `def`

MOTORES = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    MOTORES["analise"] = carregar()
    yield
    MOTORES.clear()


app = FastAPI(title="Passo 3 — async def × def", lifespan=lifespan)


class Pedido(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


@app.get("/saude")
def saude():
    return {"ok": True}


if TRAVAR:
    @app.post("/processar_texto")
    async def processar_texto(pedido: Pedido):            # 🐛 no laço principal: bloqueia TUDO
        return classificar(pedido.texto, MOTORES["analise"])
else:
    @app.post("/processar_texto")
    def processar_texto(pedido: Pedido):                  # numa thread à parte: os outros seguem
        return classificar(pedido.texto, MOTORES["analise"])
