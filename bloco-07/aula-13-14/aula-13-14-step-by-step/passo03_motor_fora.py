"""
Passo 3 — o motor não carregou: 503, e o resto da API no ar (Aula 14 · TP4, item 4).

    uvicorn passo03_motor_fora:app --reload        e abra  http://127.0.0.1:8000/docs

O TP4: "Se o modelo LLM não estiver carregado corretamente…, a aplicação deve retornar um código de
erro adequado (ex: 503 Serviço Indisponível) e uma mensagem explicativa."

O "modelo" daqui são as regras de regras_passo03.json, lidas quando a API sobe — como se carrega um
modelo de verdade. Faça, nesta ordem:

  1. Suba e teste: POST /processar_texto → 200; GET /saude → 200.
  2. RENOMEIE regras_passo03.json (para regras_passo03.json.bak) e salve este .py — o --reload reinicia:
       no terminal: "Motor NÃO carregado — FileNotFoundError…"
       POST /processar_texto → 503, com a frase;   GET /saude → 200 — o resto continua no ar.
  3. 🐛 Mude CARREGAR_COM_SEGURANCA para False e salve: a API NEM SOBE. O terminal mostra o
     FileNotFoundError, e nenhuma rota responde — nem a /saude, que não tem nada a ver com o motor.
     Foi o que aconteceu na v11, na máquina de um colega: uma peça quebrada derrubou todas.
  4. Volte o nome do arquivo e CARREGAR_COM_SEGURANCA = True.

Falhe em pedaços, não inteira.
"""

import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

CARREGAR_COM_SEGURANCA = True     # 🐛 mude para False (passo 3 do roteiro acima)

app = FastAPI(title="Passo 3 — o motor fora: 503")
log = logging.getLogger("uvicorn.error")
ARQ_REGRAS = Path(__file__).parent / "regras_passo03.json"


def carregar_motor() -> dict:
    return json.loads(ARQ_REGRAS.read_text(encoding="utf-8"))


if CARREGAR_COM_SEGURANCA:
    try:
        MOTOR = carregar_motor()
    except (OSError, ValueError) as falha:          # arquivo ausente/ilegível · JSON inválido
        MOTOR = None
        log.error("Motor NÃO carregado — %s: %s", type(falha).__name__, falha)
else:
    MOTOR = carregar_motor()                         # sem try: se falhar, a API inteira não sobe


class PedidoAnalise(BaseModel):
    texto: str = Field(min_length=15, max_length=2000)


class Erro(BaseModel):
    detail: str


@app.get("/saude")
def saude():
    """Nada a ver com o motor: diz só que a API está no ar."""
    return {"api": "no ar", "motor_carregado": MOTOR is not None}


@app.post("/processar_texto", responses={503: {"model": Erro, "description": "O motor não foi carregado."}})
def processar_texto(pedido: PedidoAnalise):
    if MOTOR is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O analisador está indisponível: o motor não foi carregado quando a API subiu. "
                   "As outras rotas funcionam normalmente.",
        )
    texto = pedido.texto.lower()
    achadas = {cat: [p for p in palavras if p in texto] for cat, palavras in MOTOR.items()}
    melhor = max(achadas, key=lambda cat: len(achadas[cat]))
    return {"categoria_sugerida": melhor if achadas[melhor] else None, "pistas": achadas[melhor]}
