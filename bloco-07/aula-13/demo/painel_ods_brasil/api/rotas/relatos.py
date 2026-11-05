"""
Rotas dos relatos de campo — Painel ODS Brasil, v11 (Aula 13; criadas na v10). A API RECEBE.

    POST /relatos   recebe um relato, VALIDA contra o modelo e grava    (o desenho do POST /processar_texto do TP4)
    GET  /relatos   devolve os relatos recebidos, com filtros            (a "consulta")

Quem recebe, valida. O corpo do POST é declarado como `relato: Relato` — um modelo
Pydantic —, e não como `dict`. Com `dict` (o primeiro exemplo do livro [Adeshina, p37]),
a API aceitaria qualquer coisa: {"uf": 123}, {}, um texto vazio — e responderia 200.

v11 — o que SAI também tem contrato:
  · POST /relatos responde 201 (Created), e não 200: criou algo [Adeshina, p68]. O corpo é
    RelatoRecebido — a mensagem e o relato como foi GRAVADO (com número e hora);
  · GET /relatos responde RespostaRelatos, com uma lista de RelatoGravado.
  🐛 O primeiro GET da v11 usou o modelo de ENTRADA (Relato) na resposta. Relato tem
     extra="forbid" — e cada linha gravada tem "id" e "recebido_em". Resultado: 500 em
     toda consulta. Entrada e saída são contratos diferentes.
"""

from fastapi import APIRouter, Query, status

from api.modelos import Categoria, Relato, SiglaUF
from api.respostas import RelatoRecebido, RespostaRelatos
from src.relatos import carregar_relatos, filtrar_relatos, gravar_relato

router = APIRouter(prefix="/relatos", tags=["relatos"])


# 🐛 Tropeço da v10: na primeira versão os relatos ficavam numa lista em memória —
#    `relatos = []`, como o todo_list do livro ("a temporary in-app database" [Adeshina,
#    p37]). Com o `uvicorn --reload`, salvar QUALQUER arquivo .py reinicia o servidor — e a
#    lista volta vazia. Três relatos enviados, um arquivo salvo: zero relatos. Agora eles vão
#    para data/relatos/relatos.csv, por src/relatos.py.
@router.post("", status_code=status.HTTP_201_CREATED, response_model=RelatoRecebido, summary="Enviar um relato")
def enviar_relato(relato: Relato):
    """Recebe um relato de campo e o grava.

    O corpo é validado contra o modelo **Relato** antes de qualquer coisa: UF entre as 27,
    categoria da lista, texto de 15 a 500 caracteres, **nenhum campo a mais** (422 se
    vier, por exemplo, `nome` ou `telefone`). Responde **201** com o relato gravado — o
    número e a data em que foi recebido.
    """
    gravado = gravar_relato(relato.uf, relato.categoria, relato.texto)
    return {"mensagem": "Relato recebido.", "relato": gravado}


@router.get("", response_model=RespostaRelatos, summary="Listar os relatos recebidos")
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
