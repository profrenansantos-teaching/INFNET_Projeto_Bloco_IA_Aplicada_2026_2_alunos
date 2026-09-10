"""
app_SIMPLES.py — MÍNIMO necessário (como no PDF §4).

Só tem o que o aluno PRECISA para rodar o painel:
  1) @st.cache_data  →  não recoletar a cada clique
  2) st.multiselect  →  filtrar por região
  3) st.metric       →  3 cards de resumo
  4) st.bar_chart    →  gráfico de barras ordenado
  5) st.dataframe    →  tabela com tudo

Como rodar:
  pip install streamlit requests
  streamlit run app_simples.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from data_access_simples import carregar_dados

st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")
st.title("🌱 Painel ODS Brasil")
st.subheader("Versão SIMPLES — como no PDF da Aula 2")


@st.cache_data(ttl=3600)            # guarda o resultado por 1 hora (nao recoletar)
def obter_dados():
    return carregar_dados()


dados, fonte = obter_dados()
st.caption(f"Fonte: {fonte} · {len(dados)} UFs")

# ---------- FILTRO por região ----------
regioes = sorted({l["regiao"] for l in dados})
sel = st.multiselect("Filtrar por região", regioes, default=regioes)
filtrados = [l for l in dados if l["regiao"] in sel]

# ---------- 3 MÉTRICAS ----------
c1, c2, c3 = st.columns(3)
c1.metric("UFs exibidas", len(filtrados))
c2.metric("Regiões", len({l["regiao"] for l in filtrados}))
c3.metric("População somada", f"{sum(l['populacao_2025'] for l in filtrados):,}".replace(",", "."))

# ---------- GRÁFICO de barras ----------
st.markdown("### População por UF")
ordenados = sorted(filtrados, key=lambda l: l["populacao_2025"], reverse=True)
st.bar_chart(ordenados, x="uf", y="populacao_2025", height=380)

# ---------- TABELA ----------
st.markdown("### Dados coletados")
st.dataframe(filtrados, use_container_width=True, hide_index=True)

st.caption("Fonte: IBGE — Tabela 6579 (população residente estimada).")
