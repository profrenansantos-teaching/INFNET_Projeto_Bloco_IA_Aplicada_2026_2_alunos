"""
Passo 5 — a rota do TP4: o contrato antes do motor (Aula 13 · TP4, itens 2 e 3).

    uvicorn passo05_contrato_do_motor:app --reload        e abra  http://127.0.0.1:8000/docs

O TP4 pede: "POST /processar_texto: Rota que recebe um texto enviado pelo usuário e retorna a
análise" (item 2) — e que ela "deve retornar um JSON estruturado com informações detalhadas, como
o texto processado, o tipo de análise realizada (resumo, classificação, etc.) e os resultados
gerados" (item 3).

Este arquivo é o ESQUELETO dessa rota, pronto para copiar para o seu projeto:
  · PedidoAnalise     — o que entra (Aula 12): o texto, com limites; nada a mais;
  · ResultadoAnalise  — o que sai (hoje): os seis campos, com tipos e descrições;
  · analisar()        — o MOTOR. Hoje, regras de palavras-chave (_motor.py). Na Etapa 8, um modelo
                        LLM local. Troque SÓ esta função: a rota e os dois modelos ficam.

Experimente no /docs:
  "O nível do rio baixou tanto que o barco não chega mais ao porto."  -> seca, 1.0
  "A água do arroio subiu durante a noite e alcançou as casas."       -> null, 0.0, []
       (uma enchente — e nenhuma palavra da lista: o limite das regras, o argumento da Etapa 8)
  "curto"                                                             -> 422
"""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from _motor import MOTOR, classificar

app = FastAPI(title="Passo 5 — POST /processar_texto: o contrato antes do motor")

Categoria = Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]


class PedidoAnalise(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    texto: str = Field(min_length=15, max_length=2000, description="O texto a analisar.")
    tipo_analise: Literal["classificacao"] = Field("classificacao", description="Hoje, só classificacao.")


class ResultadoAnalise(BaseModel):
    tipo_analise: Literal["classificacao"] = Field(description="A análise feita.")
    texto: str = Field(description="O texto analisado.")
    categoria_sugerida: Categoria | None = Field(description="A categoria mais provável, ou null.")
    confianca: float = Field(ge=0, le=1, description="De 0 a 1.")
    pistas: list[str] = Field(description="O que, no texto, levou à sugestão.")
    motor: str = Field(description="Quem analisou.")


def analisar(texto: str) -> dict:
    """O MOTOR — a única parte que muda na Etapa 8. Pode devolver o que quiser:
    o response_model deixa sair só o que está em ResultadoAnalise."""
    return {**classificar(texto), "motor": MOTOR}


@app.post("/processar_texto", response_model=ResultadoAnalise, summary="Analisar um texto (classificação)")
def processar_texto(pedido: PedidoAnalise):
    """Sugere a categoria do texto: o texto analisado, o tipo de análise, a categoria (ou null), a
    confiança, as pistas e o motor."""
    return {"tipo_analise": pedido.tipo_analise, "texto": pedido.texto, **analisar(pedido.texto)}
