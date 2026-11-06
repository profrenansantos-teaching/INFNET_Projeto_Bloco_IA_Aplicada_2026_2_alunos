"""Rotas das notícias (Agência Brasil) — Painel ODS Brasil, v12 (Aula 14; criada na v9).

v11: response_model=RespostaNoticias. 🐛 O primeiro modelo declarou `publicado_em: datetime`;
o CSV grava "02/09/2026 08:16", e esta rota inteira passou a responder 500 — ver api/respostas.py.

v12: sem a coleta nesta máquina, 503 — o mesmo critério do desmatamento. Uma seção sem
notícias continua sendo 200 com lista vazia: a consulta recorta.
"""

from fastapi import APIRouter, HTTPException, Query, status

from api.erros import erro
from api.respostas import RespostaNoticias
from src.noticias import carregar_noticias, metadados

router = APIRouter(prefix="/noticias", tags=["noticias"])


@router.get(
    "",
    response_model=RespostaNoticias,
    responses={503: erro("As notícias não foram coletadas nesta máquina.")},
    summary="Notícias da última coleta",
)
def noticias(
    secao: str | None = Query(None, description='Ex.: "Meio ambiente". Sem ela, todas.'),
    limite: int = Query(10, ge=1, le=50, description="Quantas notícias, no máximo."),
):
    """Título, seção, data e link das notícias que a coleta (Aula 7) gravou. CC BY 3.0 BR: cite."""
    lista = carregar_noticias()
    if not lista:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="As notícias não foram coletadas nesta máquina. "
                   "Rode a coleta (python -m src.coleta_web) e tente de novo.",
        )
    meta = metadados()
    if secao is not None:
        lista = [n for n in lista if n["secao"] == secao]
    return {
        "fonte": "Agência Brasil (EBC)",
        "licenca": meta.get("licenca", ""),
        "coletado_em": meta.get("coletado_em", ""),
        "linhas": len(lista[:limite]),
        "dados": lista[:limite],
    }
