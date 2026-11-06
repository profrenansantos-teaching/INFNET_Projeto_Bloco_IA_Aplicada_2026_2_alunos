"""
A rota que o TP4 pede — POST /processar_texto. Painel ODS Brasil, v14 (Aula 16; criada na v11).

    POST /processar_texto   recebe um texto e devolve a análise, num formato DECLARADO

v14 — O MOTOR DE VERDADE: o modelo de linguagem local que a Aula 15 escolheu
(src/analisador_llm.py). O CONTRATO NÃO MUDOU (PedidoAnalise → ResultadoAnalise, Aula 13): o
painel e quem mais usa a rota não mudaram uma linha. Mudaram três coisas, todas AQUI:

  1. QUANDO o modelo carrega — uma vez, quando a API sobe (carregar_na_subida(), chamada pelo
     lifespan de api/main.py), e não a cada pedido.
     🐛 Na primeira versão, como no exemplo 3-2 do livro [Parandeh, p92], a função da rota
        carregava o modelo: cada análise pagava a carga inteira de novo (ver o passo 1 da Aula 16).
  2. COMO a rota é declarada — `def`, e não `async def`.
     🐛 Com `async def`, enquanto o modelo pensava, a API INTEIRA parava: o desmatamento, os
        relatos e o /docs esperavam a análise acabar. Uma rota `def` o FastAPI roda numa thread à
        parte; uma `async def`, no laço principal — confiando que ela nunca bloqueia [Parandeh, p192].
        Pensar 2 s na CPU é bloquear (passo 3 da Aula 16).
  3. O 503 continua (v12), agora para o modelo: se ele não carregou — não foi baixado, o arquivo
     está corrompido, faltou memória —, a API sobe assim mesmo e só esta rota responde 503.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from api.erros import erro
from api.modelos import PedidoAnalise
from api.respostas import ResultadoAnalise
from src.analisador_llm import MODELO, carregar_motor, classificar_com_modelo

router = APIRouter(tags=["análise de texto"])
log = logging.getLogger("uvicorn.error")

# O modelo carregado mora aqui — num dicionário, como no exemplo 3-16 do livro [Parandeh, p129].
# Vazio até a API subir; vazio para sempre se a carga falhar (e então a rota responde 503).
MOTORES: dict = {}


def carregar_na_subida() -> None:
    """Chamada UMA vez pelo lifespan (api/main.py), antes do primeiro pedido."""
    try:
        motor = carregar_motor()
    # Aqui, sim, qualquer exceção: é a FRONTEIRA entre o modelo e a API. Seja qual for o motivo
    # (não baixado: OSError; tokens repetidos: ValueError; sem memória: RuntimeError…), a falha
    # vai para o log e a API sobe sem o modelo. Falhe em pedaços (v12).
    except Exception as falha:  # noqa: BLE001
        log.error("Modelo %s NÃO carregado — %s: %s → a rota /processar_texto vai responder 503. "
                  "Ele foi baixado? python -m src.baixar_modelo", MODELO, type(falha).__name__,
                  str(falha).splitlines()[0])
        return
    MOTORES["analise"] = motor
    log.info("Modelo %s carregado em %.1f s.", motor.nome, motor.segundos_para_carregar)


def liberar_na_descida() -> None:
    """Chamada pelo lifespan quando a API desce: devolve a memória."""
    MOTORES.clear()


@router.post(
    "/processar_texto",
    response_model=ResultadoAnalise,
    responses={503: erro("O modelo de linguagem não foi carregado.")},
    summary="Analisar um texto (classificação)",
)
def processar_texto(pedido: PedidoAnalise):     # def, não async def: o modelo bloqueia enquanto pensa
    """Sugere a **categoria** de um texto (queimada, desmatamento, enchente, seca, poluicao, lixo).

    Quem analisa é um **modelo de linguagem local** (`motor` diz qual), rodando na CPU da máquina
    da API — leva alguns segundos. Devolve o texto, o tipo de análise, a categoria sugerida, a
    confiança do modelo (0 a 1 — **não** é a chance de acerto) e o motor; `pistas` vem vazia
    (um modelo não aponta palavras).
    Se o modelo não foi carregado quando a API subiu: **503** — as outras rotas continuam no ar.
    """
    motor = MOTORES.get("analise")
    if motor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O analisador de texto está indisponível: o modelo de linguagem não foi carregado "
                   "quando a API subiu. As outras rotas funcionam normalmente.",
        )
    resultado = classificar_com_modelo(pedido.texto, motor)
    return {"tipo_analise": pedido.tipo_analise, "texto": pedido.texto, "motor": motor.nome, **resultado}
