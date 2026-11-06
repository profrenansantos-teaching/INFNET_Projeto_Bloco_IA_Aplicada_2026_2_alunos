"""
O que a API PROMETE devolver — os modelos de resposta. Painel ODS Brasil, v11 (Aula 13).

api/modelos.py diz o que a API ACEITA (a entrada, Aula 12). Este arquivo diz o que ela
DEVOLVE. São dois contratos, e por isso moram em dois arquivos: um assunto, um arquivo.

"Response models serve as templates for returning data from an API route path."
[Adeshina, p60]

O QUE O response_model FAZ COM O QUE A FUNÇÃO DEVOLVE (verificado, FastAPI 0.142):
  · FILTRA — só os campos declarados saem; o resto fica no servidor. A função pode
    calcular o que quiser; a resposta é a vitrine, não o estoque;
  · CONFERE — se o que a função devolve não cumpre o modelo, a rota responde 500
    (ResponseValidationError no terminal). Quem quebrou a promessa foi a API, não o
    cliente: por isso 500, e não 422;
  · DOCUMENTA — o /docs deixa de mostrar "string" e passa a mostrar o formato exato.

🐛 Dois tropeços reais da v11:
  · o GET /relatos usou primeiro o modelo de ENTRADA (Relato, com extra="forbid") como
    resposta. As linhas gravadas têm "id" e "recebido_em", que a entrada proíbe — e a
    rota passou a responder 500. Entrada e saída são contratos diferentes: Relato entra,
    RelatoGravado sai;
  · "publicado_em" foi declarado primeiro como datetime. O CSV da coleta grava
    "02/09/2026 08:16" — que não é uma data que o Pydantic reconheça — e a rota
    /noticias inteira passou a responder 500. Prometa só o que o seu dado cumpre: aqui,
    texto no formato dd/mm/aaaa hh:mm.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.modelos import Categoria, SiglaUF

UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]


# ---------------------------------------------------------------- os envelopes (v9)
class Envelope(BaseModel):
    """O que toda resposta de consulta traz: de onde vem e quantas linhas tem."""

    fonte: str = Field(description="De onde vêm os dados.")
    linhas: int = Field(description="Quantos itens há em `dados`.")


class EnvelopeColeta(Envelope):
    """Os dados que o projeto COLETOU: a licença viaja com o dado (v9)."""

    licenca: str = Field(description="A licença da fonte — cite-a ao reutilizar.")
    coletado_em: str = Field(description="Quando a coleta rodou: dd/mm/aaaa hh:mm.")


# ---------------------------------------------------------------- desmatamento
class LinhaDesmatamento(BaseModel):
    uf: UfAmazonia
    estado: str
    ano: int
    area_km2: float = Field(description="Taxa anual de desmatamento, em km².")


class TotalAno(BaseModel):
    ano: int
    area_km2: float = Field(description="Soma das nove UFs da Amazônia Legal, em km².")


class PosicaoRanking(BaseModel):
    uf: UfAmazonia
    estado: str
    area_km2: float


class RespostaDesmatamento(EnvelopeColeta):
    dados: list[LinhaDesmatamento]


class RespostaTotais(EnvelopeColeta):
    dados: list[TotalAno]


class RespostaRanking(EnvelopeColeta):
    dados: list[PosicaoRanking]


# ---------------------------------------------------------------- notícias
class Noticia(BaseModel):
    secao: str
    titulo: str
    # 🐛 Era `publicado_em: datetime`. O CSV grava "02/09/2026 08:16" e a rota inteira
    #    respondia 500. A promessa é a do dado: texto, neste formato.
    publicado_em: str = Field(description="Data e hora de publicação: dd/mm/aaaa hh:mm.")
    palavras: int = Field(description="Tamanho do texto da notícia, em palavras.")
    url: str


class RespostaNoticias(EnvelopeColeta):
    dados: list[Noticia]


# ---------------------------------------------------------------- relatos (v10)
class RelatoGravado(BaseModel):
    """Um relato como a API o GUARDOU — a entrada (Relato) mais o número e a hora."""

    id: int = Field(description="Número do relato, dado pela API.")
    recebido_em: str = Field(description="Quando a API o recebeu: dd/mm/aaaa hh:mm.")
    uf: SiglaUF
    categoria: Categoria
    texto: str


class RelatoRecebido(BaseModel):
    """A resposta do POST /relatos (201)."""

    mensagem: str
    relato: RelatoGravado


class RespostaRelatos(Envelope):
    aviso: str = Field(description="Conteúdo enviado por pessoas, não verificado pelo projeto.")
    dados: list[RelatoGravado]


# ---------------------------------------------------------------- sobre a API
class Apresentacao(BaseModel):
    api: str
    versao: str
    documentacao: str
    rotas: list[str]


class Fonte(BaseModel):
    """Um conjunto de dados: o mesmo formato para os três, seja qual for o JSON da coleta."""

    conjunto: str
    site: str | None = Field(None, description="De onde o conjunto vem (ausente nos relatos).")
    licenca: str | None = Field(None, description="Licença da fonte (ausente nos relatos).")
    coletado_em: str | None = Field(None, description="Data da coleta: dd/mm/aaaa hh:mm.")
    aviso: str | None = Field(None, description="Ressalva sobre o conjunto, quando houver.")


# ---------------------------------------------------------------- análise de texto (TP4)
class ResultadoAnalise(BaseModel):
    """A resposta do POST /processar_texto — o formato que o TP4 pede (item 3).

    O CONTRATO VEM ANTES DO MOTOR: hoje quem analisa é um conjunto de regras
    (src/analisador.py); na Etapa 8 será um modelo LLM local. Este formato não muda — e
    quem já usa a rota não precisa mudar nada.
    """

    # O exemplo que o /docs mostra na resposta 200 — o mesmo recurso do modelo de entrada (Aula 12).
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tipo_analise": "classificacao",
                    "texto": "O nível do rio baixou tanto que o barco da comunidade não chega mais ao porto.",
                    "categoria_sugerida": "seca",
                    "confianca": 1.0,
                    "pistas": ["nível do rio", "baixou"],
                    "motor": "regras-v1 (palavras-chave)",
                }
            ]
        }
    )

    tipo_analise: Literal["classificacao"] = Field(description="A análise feita.")
    texto: str = Field(description="O texto analisado (sem os espaços das pontas).")
    categoria_sugerida: Categoria | None = Field(
        description="A categoria mais provável — null se o motor não achou nenhuma pista."
    )
    confianca: float = Field(ge=0, le=1, description="De 0 a 1: quanto o motor confia na sugestão.")
    pistas: list[str] = Field(description="O que, no texto, levou à sugestão.")
    motor: str = Field(description="Quem analisou: hoje, regras; na Etapa 8, o nome do modelo.")
