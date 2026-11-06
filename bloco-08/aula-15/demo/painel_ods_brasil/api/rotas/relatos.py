"""
Rotas dos relatos de campo — Painel ODS Brasil, v12 (Aula 14; criadas na v10). A API RECEBE.

    POST /relatos        recebe um relato, VALIDA e grava — 201; repetido: 409
    GET  /relatos        os relatos recebidos, com filtros — 200 (vazio é uma resposta)
    GET  /relatos/{id}   UM relato, pelo número — 200; inexistente: 404              (v12)

Quem recebe, valida. O corpo do POST é declarado como `relato: Relato` — um modelo
Pydantic —, e não como `dict`. Com `dict` (o primeiro exemplo do livro [Adeshina, p37]),
a API aceitaria qualquer coisa: {"uf": 123}, {}, um texto vazio — e responderia 200.

v11 — o que SAI também tem contrato: POST responde 201 com RelatoRecebido; GET responde
RespostaRelatos. (🐛 v11: usar o modelo de ENTRADA na resposta derrubava o GET — 500.)

v12 — quando dá errado, o status diz O QUÊ:
  · 404 — "o que você pediu não existe": GET /relatos/99. O CAMINHO identifica um recurso
    (Aula 11); se ele não existe, 404. Já a CONSULTA recorta uma coleção: GET /relatos?uf=AC
    sem nenhum relato do Acre é 200 com lista vazia — a resposta certa para "quais?";
  · 409 — "o pedido está certo, mas conflita com o que já existe": o mesmo relato de novo,
    em menos de 10 minutos. O modelo não tem como saber disso (ele vê só o corpo); quem sabe
    é src/relatos.py, que levanta RelatoRepetido — e a rota traduz para HTTP;
  · 422 — continua automático: o corpo não cumpre o modelo.
"""

from fastapi import APIRouter, HTTPException, Path, Query, status

from api.erros import erro
from api.modelos import Categoria, Relato, SiglaUF
from api.respostas import RelatoGravado, RelatoRecebido, RespostaRelatos
from src.relatos import RelatoRepetido, buscar_relato, carregar_relatos, filtrar_relatos, gravar_relato

router = APIRouter(prefix="/relatos", tags=["relatos"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RelatoRecebido,
    responses={409: erro("O mesmo relato já chegou há menos de 10 minutos.")},
    summary="Enviar um relato",
)
def enviar_relato(relato: Relato):
    """Recebe um relato de campo e o grava.

    O corpo é validado contra o modelo **Relato** antes de qualquer coisa: UF entre as 27,
    categoria da lista, texto de 15 a 500 caracteres, **nenhum campo a mais** (422 se
    vier, por exemplo, `nome` ou `telefone`). Responde **201** com o relato gravado — o
    número e a data em que foi recebido. O mesmo relato (UF, categoria e texto) enviado de
    novo em menos de 10 minutos responde **409**, com o número do que já foi gravado.
    """
    try:
        gravado = gravar_relato(relato.uf, relato.categoria, relato.texto)
    except RelatoRepetido as repetido:
        anterior = repetido.anterior
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Este relato já foi recebido: nº {anterior['id']}, em {anterior['recebido_em']}. "
                   "Não é preciso enviar de novo.",
        )
    return {"mensagem": "Relato recebido.", "relato": gravado}


@router.get("", response_model=RespostaRelatos, summary="Listar os relatos recebidos")
def listar_relatos(
    uf: SiglaUF | None = Query(None, description="Só os relatos desta UF."),
    categoria: Categoria | None = Query(None, description="Só os desta categoria."),
    limite: int = Query(20, ge=1, le=100, description="Quantos, no máximo (os mais recentes)."),
):
    """Os relatos recebidos pela API, do mais recente para o mais antigo.

    Nenhum relato com esses filtros é uma resposta válida: **200**, `"linhas": 0`.
    """
    escolhidos = filtrar_relatos(carregar_relatos(), uf, categoria)
    mais_recentes = sorted(escolhidos, key=lambda r: r["id"], reverse=True)[:limite]
    return {
        "fonte": "relatos enviados à API do Painel ODS Brasil",
        "aviso": "conteúdo enviado por pessoas, não verificado pelo projeto",
        "linhas": len(mais_recentes),
        "dados": mais_recentes,
    }


@router.get(
    "/{id_relato}",
    response_model=RelatoGravado,
    responses={404: erro("Não há relato com este número.")},
    summary="Um relato, pelo número",
)
def um_relato(id_relato: int = Path(ge=1, description="O número do relato (o `id` devolvido no envio).")):
    """O relato com este número. Se não houver: **404** — e não 200 com uma resposta vazia."""
    relato = buscar_relato(id_relato)
    if relato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Não há relato nº {id_relato}.")
    return relato
