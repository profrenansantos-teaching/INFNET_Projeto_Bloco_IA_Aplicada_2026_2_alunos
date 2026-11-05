"""
Rotas dos relatos de campo — Painel ODS Brasil, v10 (Aula 12). A API passa a RECEBER.

    POST /relatos   recebe um relato, VALIDA contra o modelo e grava    (o desenho do POST /processar_texto do TP4)
    GET  /relatos   devolve os relatos recebidos, com filtros            (a "consulta")

Quem recebe, valida. O corpo do POST é declarado como `relato: Relato` — um modelo
Pydantic —, e não como `dict`. Com `dict` (o primeiro exemplo do livro [Adeshina, p37]),
a API aceitaria qualquer coisa: {"uf": 123}, {}, um texto vazio — e responderia 200.
"""

from fastapi import APIRouter, Query

from api.modelos import Categoria, Relato, SiglaUF
from src.relatos import carregar_relatos, filtrar_relatos, gravar_relato

router = APIRouter(prefix="/relatos", tags=["relatos"])


# 🐛 Tropeço da v10: na primeira versão os relatos ficavam numa lista em memória —
#    `relatos = []`, como o todo_list do livro ("a temporary in-app database" [Adeshina,
#    p37]). Com o `uvicorn --reload`, salvar QUALQUER arquivo .py reinicia o servidor — e a
#    lista volta vazia. Três relatos enviados, um arquivo salvo: zero relatos. Agora eles vão
#    para data/relatos/relatos.csv, por src/relatos.py.
@router.post("", summary="Enviar um relato")
def enviar_relato(relato: Relato):
    """Recebe um relato de campo e o grava.

    O corpo é validado contra o modelo **Relato** antes de qualquer coisa: UF entre as 27,
    categoria da lista, texto de 15 a 500 caracteres, **nenhum campo a mais** (422 se
    vier, por exemplo, `nome` ou `telefone`). Devolve o relato gravado, com o número e a
    data em que foi recebido.
    """
    gravado = gravar_relato(relato.uf, relato.categoria, relato.texto)
    return {"mensagem": "Relato recebido.", "relato": gravado}


@router.get("", summary="Listar os relatos recebidos")
def listar_relatos(
    uf: SiglaUF | None = Query(None, description="Só os relatos desta UF."),
    categoria: Categoria | None = Query(None, description="Só os desta categoria."),
    limite: int = Query(20, ge=1, le=100, description="Quantos, no máximo (os mais recentes)."),
):
    """Os relatos recebidos pela API, do mais recente para o mais antigo."""
    escolhidos = filtrar_relatos(carregar_relatos(), uf, categoria)
    mais_recentes = sorted(escolhidos, key=lambda r: r["id"], reverse=True)[:limite]
    return {
        "fonte": "relatos enviados à API do Painel ODS Brasil",
        "aviso": "conteúdo enviado por pessoas, não verificado pelo projeto",
        "linhas": len(mais_recentes),
        "dados": mais_recentes,
    }
