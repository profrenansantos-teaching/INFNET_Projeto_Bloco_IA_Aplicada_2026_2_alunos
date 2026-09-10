"""
Painel de Indicadores Sustentáveis do Brasil — Aula 1 (versão demo)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

Nesta primeira versão usamos SÓ Python puro + Streamlit (sem pandas):
os dados são uma AMOSTRA lida do CSV com o módulo `csv` da biblioteca padrão,
representada como uma LISTA DE DICIONÁRIOS (cada linha = um dicionário).
Na Aula 2 automatizaremos a coleta via API do IBGE (também em Python puro, com `json`).

Como rodar:
    1) crie e ative o ambiente virtual:  python -m venv .venv
       Windows:  .venv\\Scripts\\activate
       Linux/Mac: source .venv/bin/activate
    2) instale as dependências:          pip install -r requirements.txt
    3) execute:                          streamlit run app.py
"""

import csv
from pathlib import Path

import streamlit as st

# ----------------------------------------------------------------------
# 1) Configuração da página (sempre a PRIMEIRA chamada Streamlit do script)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")

# ----------------------------------------------------------------------
# 2) Cabeçalho: título e descrição do problema (TP1 - Parte 4)
# ----------------------------------------------------------------------
st.title("🌱 Painel de Indicadores Sustentáveis do Brasil")
st.subheader("Dados abertos a serviço da Agenda 2030")

st.markdown(
    """
    **Problema de negócio.** Gestores públicos e organizações do terceiro setor
    precisam **comparar indicadores socioambientais entre as Unidades da Federação**
    para priorizar ações alinhadas aos **Objetivos de Desenvolvimento Sustentável (ODS)**.

    **Nossa solução.** Um painel interativo com indicadores públicos do **IBGE** por UF,
    começando pela população e evoluindo para saneamento e meio ambiente (ODS 6 e 11).

    **Público-alvo.** Gestores municipais/estaduais e ONGs de impacto socioambiental.
    """
)

st.markdown(
    "**Links úteis:** &nbsp; "
    "[Agenda 2030 / ODS (ONU)](https://brasil.un.org/pt-br/sdgs) · "
    "[API de dados do IBGE](https://servicodados.ibge.gov.br/api/docs) · "
    "[Conecta Brasil](https://www.conectabrasil.org/)"
)

st.divider()

# ----------------------------------------------------------------------
# 3) Carregar a amostra em PYTHON PURO (lista de dicionários)
#    (na Aula 2 esta função dará lugar à coleta via API do IBGE)
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
CSV_AMOSTRA = BASE_DIR / "data" / "sample" / "populacao_amostra.csv"


def carregar_amostra(caminho: Path) -> list[dict]:
    """Lê o CSV e devolve uma LISTA DE DICIONÁRIOS (uma linha = um dicionário)."""
    linhas: list[dict] = []
    with open(caminho, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            # o CSV traz tudo como texto; convertemos a população para inteiro
            linha["populacao_2025"] = int(linha["populacao_2025"])
            linhas.append(linha)
    return linhas


dados = carregar_amostra(CSV_AMOSTRA)  # ex.: [{"uf": "AM", "estado": "Amazonas", ...}, ...]

# ----------------------------------------------------------------------
# 4) Indicadores-resumo com Python puro (len, set, sum)
# ----------------------------------------------------------------------
qtd_ufs = len({linha["uf"] for linha in dados})           # conjunto de UFs distintas
qtd_regioes = len({linha["regiao"] for linha in dados})   # conjunto de regiões distintas
pop_total = sum(linha["populacao_2025"] for linha in dados)

col1, col2, col3 = st.columns(3)
col1.metric("UFs na amostra", qtd_ufs)
col2.metric("Regiões cobertas", qtd_regioes)
col3.metric("População somada (2025)", f"{pop_total:,}".replace(",", "."))

# ----------------------------------------------------------------------
# 5) Tabela de amostra — st.dataframe aceita a lista de dicionários direto
# ----------------------------------------------------------------------
st.markdown("### 📋 Amostra dos dados que usaremos no projeto")
st.dataframe(dados, use_container_width=True, hide_index=True)

st.caption(
    "Fonte: IBGE — População residente estimada (2025), tabela 6579. "
    "Amostra de 8 UFs coletada manualmente. Na Aula 2 automatizaremos a coleta das 27 UFs."
)
