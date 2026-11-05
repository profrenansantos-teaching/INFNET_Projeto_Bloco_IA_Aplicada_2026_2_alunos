"""Rotas das notícias (Agência Brasil) — Painel ODS Brasil, v10 (Aula 12; criada na v9)."""

from fastapi import APIRouter, Query

from src.noticias import carregar_noticias, metadados

router = APIRouter(prefix="/noticias", tags=["noticias"])


@router.get("", summary="Notícias da última coleta")
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
