"""
Painel de Indicadores Sustentáveis do Brasil — v3 (Aula 5: pronto para publicar)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v2 PARA A v3:
  · nada de novo na TELA — a mudança é de INFRAESTRUTURA;
  · o projeto ganhou .gitignore, requirements.txt completo, .streamlit/ e DEPLOY.md;
  · a coleta virou segura por padrão (ver src/data_access.py);
  · um rodapé mostra a VERSÃO e a origem dos dados — para dar para conferir,
    olhando o app publicado, se o último `git push` chegou lá.

Como rodar localmente:
    python -m venv .venv
    .venv\\Scripts\\activate        (Windows)   ·   source .venv/bin/activate (macOS/Linux)
    pip install -r requirements.txt
    streamlit run app.py

Como publicar: ver DEPLOY.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from src.data_access import carregar_dados

VERSAO = "v3 — Aula 5 (publicação)"

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
# Sem `use_container_width=` : o parâmetro foi descontinuado (o padrão de `width`
# já é "stretch"). Manter APIs vivas faz parte de preparar um app para publicar.
st.dataframe(filtrados, hide_index=True)

st.divider()
st.caption(
    f"{VERSAO} · Fonte: IBGE — População residente estimada (2025), tabela 6579. "
    "Próxima etapa: tornar o painel interativo (Aula 6)."
)
