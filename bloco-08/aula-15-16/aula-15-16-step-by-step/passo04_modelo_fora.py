"""
Passo 4 · O modelo que não carrega: a API sobe, e a análise responde 503 (Aula 16 · B5)

O TP4 (item 4): "Se o modelo LLM não estiver carregado corretamente… a aplicação deve retornar um código
de erro adequado (ex: 503 Serviço Indisponível) e uma mensagem explicativa." É o 503 da Aula 14 — agora
com um modelo de verdade, que tem mais jeitos de falhar: não foi baixado; o nome tem um erro de
digitação; o arquivo veio pela metade; falta memória.

🐛 Rode com PROTEGER = False e o nome errado: uvicorn escreve o OSError e "Application startup failed.
   Exiting." — a API INTEIRA não sobe; o /saude também não responde. Uma exceção no lifespan derruba a
   subida. Troque para True: a falha vai para o log, a API sobe, e só a análise responde 503.

E por que local_files_only=True (em _motor.py)? Sem ele, com o modelo ausente e SEM INTERNET, a carga
tenta o Hub 5 vezes, com espera crescente, e só desiste depois de ~80 s (medido). Com ele, o OSError
vem em menos de 1 s: o modelo ou está no disco, ou não está.

Rodar:  uvicorn passo04_modelo_fora:app               (terminal 1)
        python cronometro.py analisar 1               (terminal 2) — e abra http://127.0.0.1:8000/saude
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from _motor import carregar, classificar

PROTEGER = True
NOME = "Qwen/Qwen2.5-0.5B-Instrukt"       # 🐛 um "k" no lugar do "c" — corrija depois: "Qwen/Qwen2.5-0.5B-Instruct"

log = logging.getLogger("uvicorn.error")
MOTORES = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if PROTEGER:
        try:
            MOTORES["analise"] = carregar(NOME)
        except Exception as falha:   # noqa: BLE001 — a fronteira: qualquer falha na carga vira 503
            log.error("Modelo NÃO carregado — %s: %s", type(falha).__name__, str(falha).splitlines()[0])
    else:
        MOTORES["analise"] = carregar(NOME)
    yield
    MOTORES.clear()


app = FastAPI(title="Passo 4 — o modelo que não carrega", lifespan=lifespan)


class Pedido(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


@app.get("/saude")
def saude():
    return {"ok": True, "modelo_carregado": "analise" in MOTORES}


@app.post("/processar_texto")
def processar_texto(pedido: Pedido):
    if "analise" not in MOTORES:
        # Ao cliente: o que aconteceu e o que continua funcionando. O motivo técnico, no log.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="O analisador de texto está indisponível: o modelo de linguagem não foi "
                                   "carregado quando a API subiu. As outras rotas funcionam normalmente.")
    return classificar(pedido.texto, MOTORES["analise"])
