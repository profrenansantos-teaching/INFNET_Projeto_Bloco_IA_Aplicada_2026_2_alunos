"""
A rota que o TP4 pede — POST /processar_texto. Painel ODS Brasil, v11 (Aula 13).

    POST /processar_texto   recebe um texto e devolve a análise, num formato DECLARADO

O TP4 (item 2) pede "uma rota que receba um texto enviado pelo usuário e retorne a
análise"; o item 3 pede que a resposta seja "um JSON estruturado com... o texto
processado, o tipo de análise realizada... e os resultados gerados". Esta é ela — com um
motor de regras provisório (src/analisador.py) no lugar do LLM da Etapa 8.

O CONTRATO VEM ANTES DO MOTOR. classificar() devolve mais do que a rota promete (as
pontuações de todas as categorias, o texto normalizado): o response_model=ResultadoAnalise
deixa passar só o que está no contrato. Na Etapa 8, o modelo LLM devolverá outros detalhes
— e a resposta continuará com estes seis campos.

Status 200 (e não 201): a análise não CRIA nada no servidor; ela calcula e responde.
"""

from fastapi import APIRouter

from api.modelos import PedidoAnalise
from api.respostas import ResultadoAnalise
from src.analisador import MOTOR, carregar_regras, classificar

router = APIRouter(tags=["análise de texto"])

# As regras são lidas uma vez, quando a API sobe — como se carrega um modelo.
REGRAS = carregar_regras()


@router.post("/processar_texto", response_model=ResultadoAnalise, summary="Analisar um texto (classificação)")
def processar_texto(pedido: PedidoAnalise):
    """Sugere a **categoria** de um texto (queimada, desmatamento, enchente, seca, poluicao, lixo).

    Devolve o texto analisado, o tipo de análise, a categoria sugerida (ou `null`, se não
    houver pista), a confiança (0 a 1), as pistas que decidiram e o motor que analisou.
    Hoje o motor é um conjunto de regras; na Etapa 8, um modelo LLM local — no mesmo formato.
    """
    resultado = classificar(pedido.texto, REGRAS)
    return {"tipo_analise": pedido.tipo_analise, "texto": pedido.texto, "motor": MOTOR, **resultado}
