"""
API do Painel ODS Brasil — v9 (Aula 11: a API do projeto, subcompetências 3.3 e 3.4)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

POR QUE UMA API, SE O PAINEL JÁ MOSTRA TUDO:
  o painel é para PESSOAS. Um programa que quisesse os nossos números teria de
  raspá-lo — e o painel é uma página dinâmica: o `requests` recebe uma casca
  ("You need to enable JavaScript to run this app.", 0 tabelas). Seria o degrau 4
  da escada da Aula 10. A API é o degrau 1 que nós oferecemos: um endereço por
  pergunta, resposta em JSON, documentação gerada do próprio código.

O QUE ELA SERVE:
  o que a COLETA já gravou em data/processed/. Ela não coleta nada e não abre
  navegador: lê os mesmos CSVs que o painel lê, com as mesmas funções de src/.
  Uma leitura, dois clientes — o painel (pessoas) e a API (programas).

COMO O FASTAPI LÊ UMA ROTA (a ideia que organiza a aula):
  @app.get("/desmatamento/{uf}")          o MÉTODO e o CAMINHO
  def serie_da_uf(uf: UfAmazonia,         o que está entre { } vem do CAMINHO
                  desde: int = 1988):     o resto vem da CONSULTA (?desde=2010)
  Os TIPOS dos parâmetros não são enfeite: o FastAPI converte o texto da URL
  para o tipo declarado e recusa (422) o que não converte — antes de a função
  rodar. O que a função devolve (dicionários e listas) vira JSON.

Como rodar (da pasta painel_ods_brasil/, com o ambiente de requirements-api.txt):
    pip install -r requirements-api.txt
    uvicorn api.main:app --reload
    -> http://127.0.0.1:8000/docs       (a documentação interativa)

O painel continua rodando à parte, noutro terminal:  streamlit run app.py
"""

from typing import Literal

from fastapi import FastAPI, Path, Query

from src.desmatamento import (
    carregar_desmatamento,
    faixa_de_anos,
    metadados_desmatamento,
    ranking_do_ano,
    total_por_ano,
)
from src.noticias import carregar_noticias, metadados

VERSAO = "v9 — Aula 11"

# As 9 UFs da Amazônia Legal: as únicas que o PRODES publica. Declarar o tipo
# assim faz o FastAPI recusar "ZZ" (e "pa", minúsculo) com 422 e a lista do que
# vale — e faz o /docs mostrar um menu com as nove.
UfAmazonia = Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]

app = FastAPI(
    title="API do Painel ODS Brasil",
    version=VERSAO,
    description=(
        "Os dados que o **Painel ODS Brasil** coleta, para outros programas: o desmatamento "
        "anual por UF da Amazônia Legal (INPE/PRODES, **CC BY-SA 4.0**) e as notícias de meio "
        "ambiente da Agência Brasil (**CC BY 3.0 BR**). Toda resposta traz a fonte e a licença "
        "— quem reutilizar deve citá-las (e, no caso do INPE, compartilhar igual)."
    ),
)


# ---------------------------------------------------------------- envelope
def _desmatamento(dados: list[dict]) -> dict:
    """Embrulha as linhas com a fonte, a licença e a data da coleta.

    A licença viaja COM o dado: CC BY-SA obriga a citar e a compartilhar igual,
    e quem recebe só uma lista de números não teria como saber disso.
    """
    meta = metadados_desmatamento()
    return {
        "fonte": meta.get("site", "INPE/PRODES"),
        "licenca": meta.get("licenca", ""),
        "coletado_em": meta.get("coletado_em", ""),
        "linhas": len(dados),
        "dados": dados,
    }


# ---------------------------------------------------------------- sobre a API
@app.get("/", tags=["sobre"])
def apresentacao():
    """O que esta API serve, e onde está a documentação."""
    return {
        "api": "Painel ODS Brasil",
        "versao": VERSAO,
        "documentacao": "/docs",
        "rotas": [
            "/fontes",
            "/desmatamento",
            "/desmatamento/total",
            "/desmatamento/ranking/{ano}",
            "/desmatamento/{uf}",
            "/noticias",
        ],
    }


@app.get("/fontes", tags=["sobre"])
def fontes():
    """De onde vem cada conjunto de dados, quando foi coletado e sob qual licença."""
    return [
        {"conjunto": "desmatamento", **metadados_desmatamento()},
        {"conjunto": "noticias", **metadados()},
    ]


# ---------------------------------------------------------------- desmatamento
@app.get("/desmatamento", tags=["desmatamento"])
def desmatamento(
    desde: int = Query(1988, ge=1988, description="Primeiro ano (o PRODES começa em 1988)."),
    ate: int | None = Query(None, description="Último ano. Sem ele, até o mais recente."),
):
    """Taxa anual de desmatamento (km²) de todas as UFs da Amazônia Legal, no período pedido."""
    linhas = carregar_desmatamento()
    ate = ate if ate is not None else faixa_de_anos(linhas)[1]
    return _desmatamento([l for l in linhas if desde <= l["ano"] <= ate])


# 🐛 Tropeço da v9: esta rota vinha DEPOIS de /desmatamento/{uf}. Um pedido a
#    /desmatamento/total casava primeiro com {uf} — e "total" não é uma das nove
#    UFs: 422, "Input should be 'AC', 'AM', …". O FastAPI testa as rotas NA ORDEM
#    em que foram declaradas. Caminho fixo antes de caminho com parâmetro.
@app.get("/desmatamento/total", tags=["desmatamento"])
def desmatamento_total(
    desde: int = Query(1988, ge=1988),
    ate: int | None = Query(None),
):
    """Soma das nove UFs em cada ano: a taxa da Amazônia Legal inteira."""
    linhas = carregar_desmatamento()
    ate = ate if ate is not None else faixa_de_anos(linhas)[1]
    return _desmatamento([t for t in total_por_ano(linhas) if desde <= t["ano"] <= ate])


# 🐛 Tropeço da v9: a primeira versão era `def ranking(ano):`, sem o tipo. O ano
#    chegava como TEXTO ("2024"), a comparação com o ano do CSV (o número 2024)
#    dava falso em todas as linhas — e a rota respondia 200 com uma lista vazia.
#    Sem erro nenhum. O tipo `int` é a guarda: converte, e recusa o que não é número.
@app.get("/desmatamento/ranking/{ano}", tags=["desmatamento"])
def ranking(ano: int = Path(ge=1988, description="Ano do ranking.")):
    """As UFs no ano escolhido, da que mais desmatou para a que menos desmatou."""
    return _desmatamento(ranking_do_ano(carregar_desmatamento(), ano))


@app.get("/desmatamento/{uf}", tags=["desmatamento"])
def serie_da_uf(
    uf: UfAmazonia,
    desde: int = Query(1988, ge=1988),
    ate: int | None = Query(None),
):
    """A série anual de uma UF — o QUE vem no caminho (a UF); o recorte, na consulta."""
    linhas = carregar_desmatamento()
    ate = ate if ate is not None else faixa_de_anos(linhas)[1]
    return _desmatamento([l for l in linhas if l["uf"] == uf and desde <= l["ano"] <= ate])


# ---------------------------------------------------------------- notícias
@app.get("/noticias", tags=["noticias"])
def noticias(
    secao: str | None = Query(None, description='Ex.: "Meio ambiente". Sem ela, todas.'),
    limite: int = Query(10, ge=1, le=50, description="Quantas notícias, no máximo."),
):
    """As notícias da última coleta da Agência Brasil (título, seção, data, link)."""
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
