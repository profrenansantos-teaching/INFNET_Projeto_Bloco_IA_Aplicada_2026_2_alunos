"""
Painel de Indicadores Sustentáveis do Brasil — Aula 2 (coleta + visualização)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

Evolução da Aula 1: a amostra manual dá lugar à **coleta real via API do IBGE**
(Python puro: requests + json), com **cache em @st.cache_data** e visualizações.
A coleta fica isolada em src/data_access.py (interface de dados ≠ interface de usuário).

Como rodar:
    pip install -r requirements.txt
    streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from src.data_access import carregar_dados

st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")
st.title("🌱 Painel de Indicadores Sustentáveis do Brasil")
st.subheader("Coleta ao vivo via API de dados abertos do IBGE")


@st.cache_data(ttl=3600)
def obter_dados():
    return carregar_dados()


dados, fonte = obter_dados()
st.caption(f"Fonte: {fonte} · {len(dados)} UFs")

regioes = sorted({linha["regiao"] for linha in dados})
selecionadas = st.multiselect("Filtrar por região", regioes, default=regioes)
filtrados = [linha for linha in dados if linha["regiao"] in selecionadas]

col1, col2, col3 = st.columns(3)
col1.metric("UFs exibidas", len(filtrados))
col2.metric("Regiões", len({linha["regiao"] for linha in filtrados}))
col3.metric("População somada", f"{sum(l['populacao_2025'] for l in filtrados):,}".replace(",", "."))

st.markdown("### 📊 População por UF")
ordenados = sorted(filtrados, key=lambda linha: linha["populacao_2025"], reverse=True)
st.bar_chart(ordenados, x="uf", y="populacao_2025", height=380)

st.markdown("### 📋 Dados coletados")
st.dataframe(filtrados, use_container_width=True, hide_index=True)

st.caption(
    "Fonte: IBGE — População residente estimada (2025), tabela 6579. "
    "Próximas etapas: adicionar indicador de saneamento (ODS 6) e publicar o painel."
)
