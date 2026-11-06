"""
A rota que o TP4 pede — POST /processar_texto. Painel ODS Brasil, v12 (Aula 14; criada na v11).

    POST /processar_texto   recebe um texto e devolve a análise, num formato DECLARADO

O TP4 (item 2) pede "uma rota que receba um texto enviado pelo usuário e retorne a
análise"; o item 3 pede que a resposta seja "um JSON estruturado com... o texto
processado, o tipo de análise realizada... e os resultados gerados". Esta é ela — com um
motor de regras provisório (src/analisador.py) no lugar do LLM da Etapa 8.

O CONTRATO VEM ANTES DO MOTOR (v11). classificar() devolve mais do que a rota promete; o
response_model=ResultadoAnalise deixa passar só o que está no contrato.

v12 — QUANDO O MOTOR NÃO CARREGA: 503, e o resto da API no ar.
  O TP4 (item 4): "Se o modelo LLM não estiver carregado corretamente... a aplicação deve
  retornar um código de erro adequado (ex: 503 Serviço Indisponível) e uma mensagem
  explicativa."
  🐛 Na v11, as regras eram lidas quando a API subia — sem try. Um colega clonou o
     repositório num computador onde data/analisador/regras.json não veio (e um JSON com
     uma vírgula a mais dá no mesmo): FileNotFoundError ao importar este arquivo, e a API
     INTEIRA não subia — nem o desmatamento, nem os relatos. Uma peça quebrada derrubava
     todas. Agora a falha é guardada, a API sobe, e só esta rota responde 503 — dizendo o
     quê. O motivo técnico vai para o terminal. Falhe em pedaços, não inteira.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from api.erros import erro
from api.modelos import PedidoAnalise
from api.respostas import ResultadoAnalise
from src.analisador import MOTOR, carregar_regras, classificar

router = APIRouter(tags=["análise de texto"])
log = logging.getLogger("uvicorn.error")

# As regras são lidas uma vez, quando a API sobe — como se carrega um modelo (Etapa 8).
# Se a leitura falhar, a API sobe assim mesmo; a falha fica guardada para o 503.
try:
    REGRAS = carregar_regras()
    FALHA_AO_CARREGAR = None
except (OSError, ValueError) as falha:          # arquivo ausente/ilegível · JSON inválido
    REGRAS = None
    FALHA_AO_CARREGAR = f"{type(falha).__name__}: {falha}"
    log.error("Analisador NÃO carregado — %s. A rota /processar_texto vai responder 503.", FALHA_AO_CARREGAR)


@router.post(
    "/processar_texto",
    response_model=ResultadoAnalise,
    responses={503: erro("O motor de análise não foi carregado.")},
    summary="Analisar um texto (classificação)",
)
def processar_texto(pedido: PedidoAnalise):
    """Sugere a **categoria** de um texto (queimada, desmatamento, enchente, seca, poluicao, lixo).

    Devolve o texto analisado, o tipo de análise, a categoria sugerida (ou `null`, se não
    houver pista), a confiança (0 a 1), as pistas que decidiram e o motor que analisou.
    Se o motor não foi carregado quando a API subiu: **503** — as outras rotas continuam no ar.
    """
    if REGRAS is None:
        # Ao cliente: o que aconteceu e o que continua funcionando. O motivo técnico (o
        # caminho do arquivo, a linha do JSON) foi para o terminal quando a API subiu.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O analisador de texto está indisponível: o motor não foi carregado quando a API "
                   "subiu. As outras rotas funcionam normalmente.",
        )
    resultado = classificar(pedido.texto, REGRAS)
    return {"tipo_analise": pedido.tipo_analise, "texto": pedido.texto, "motor": MOTOR, **resultado}
