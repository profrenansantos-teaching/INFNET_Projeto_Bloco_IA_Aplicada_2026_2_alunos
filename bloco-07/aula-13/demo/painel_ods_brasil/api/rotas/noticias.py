"""Rotas das notícias (Agência Brasil) — Painel ODS Brasil, v11 (Aula 13; criada na v9).

v11: response_model=RespostaNoticias. 🐛 O primeiro modelo declarou `publicado_em: datetime`;
o CSV grava "02/09/2026 08:16", e esta rota inteira passou a responder 500 — ver api/respostas.py.
"""

from fastapi import APIRouter, Query

from api.respostas import RespostaNoticias

from src.noticias import carregar_noticias, metadados

router = APIRouter(prefix="/noticias", tags=["noticias"])


@router.get("", response_model=RespostaNoticias, summary="Notícias da última coleta")
def noticias(
    secao: str | None = Query(None, description='Ex.: "Meio ambiente". Sem ela, todas.'),
    limite: int = Query(10, ge=1, le=50, description="Quantas notícias, no máximo."),
):
    """Título, seção, data e link das notícias que a coleta (Aula 7) gravou. CC BY 3.0 BR: cite."""
    meta = metadados()
    lista = carregar_noticias()
    if secao is not None:
        lista = [n for n in lista if n["secao"] == secao]
    return {
        "fonte": "Agência Brasil (EBC)",
        "licenca": meta.get("licenca", ""),
        "coletado_em": meta.get("coletado_em", ""),
        "linhas": len(lista[:limite]),
        "dados": lista[:limite],
    }
