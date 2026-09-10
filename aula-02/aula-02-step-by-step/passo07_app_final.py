"""
PASSO 7 — App Streamlit FINAL (igual ao demo/painel_ods_brasil/app.py)
Corresponde a: §4 completo.

Diferenças em relação ao Passo 6:
  • @st.cache_data(ttl=3600)  — não recoletar a cada clique
  • st.multiselect           — filtro por região
  • st.bar_chart             — gráfico de barras ordenado por população

Rode:  streamlit run passo07_app_final.py
"""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import streamlit as st
from src.data_access import carregar_dados

st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")
st.title("🌱 Painel de Indicadores Sustentáveis do Brasil")
st.subheader("Coleta ao vivo via API de dados abertos do IBGE")

# -------- §4.1 CACHE: NÃO recoletar a cada interação! --------
# Sem cache: toda vez que mudar o filtro, refaz 2 requests → LENTO e martela a API
# Com cache: coleta UMA VEZ, reusa por 1 hora.
@st.cache_data(ttl=3600)                    # ttl = time to live (3600s = 1h)
def obter_dados():
    return carregar_dados()

dados, fonte = obter_dados()
st.caption(f"Fonte: {fonte} · {len(dados)} UFs")

# -------- §4.2 FILTRO: st.multiselect por região --------
# sorted(set(...)) = valores únicos de "regiao" em ordem alfabética
regioes = sorted({linha["regiao"] for linha in dados})
selecionadas = st.multiselect("Filtrar por região", regioes, default=regioes)

# list comprehension para manter só as linhas cuja região está selecionada
filtrados = [linha for linha in dados if linha["regiao"] in selecionadas]

# -------- MÉTRICAS (3 cards) --------
chave_pop = [k for k in dados[0].keys() if "populacao" in k][0]

col1, col2, col3 = st.columns(3)
col1.metric("UFs exibidas", len(filtrados))
col2.metric("Regiões selecionadas", len({linha["regiao"] for linha in filtrados}))
col3.metric(
    "População somada",
    f"{sum(linha[chave_pop] for linha in filtrados):,}".replace(",", ".")
)

# -------- §4.3 GRÁFICO: st.bar_chart (SEM PANDAS!) --------
# Ponto importante: sorted(filtrados, key=lambda l: l[chave_pop], reverse=True)
# → ordena do MAIS populoso para o MENOS populoso
st.markdown("### 📊 População por UF")
ordenados = sorted(filtrados, key=lambda linha: linha[chave_pop], reverse=True)
st.bar_chart(ordenados, x="uf", y=chave_pop, height=400)

# -------- TABELA completa filtrada --------
st.markdown("### 📋 Dados coletados")
st.dataframe(filtrados, use_container_width=True, hide_index=True)

st.caption(
    "Fonte: IBGE — População residente estimada, tabela 6579. "
    "Próximas etapas: plugar seu ODS/indicador e publicar o painel."
)

st.markdown("---")
with st.expander("📖 O que aprendemos neste app final (7 passos)"):
    st.markdown("""
| Passo | Assunto | Conceito novo |
|-------|---------|---------------|
| 1 | Chamada básica `requests.get` | `raise_for_status()`, `.json()` |
| 2 | Lista → Dicionário `por_id` | Dict comprehension, busca O(1) |
| 3 | JSON aninhado | Navegar `[0]["resultados"][0]["series"]` |
| 4 | Montar tabela final | `int()` em ids/valores (tipos!), loop for |
| 5 | `src/data_access.py` | Separação de camadas + fallback/cache |
| 6 | Streamlit inicial | `set_page_config`, `st.metric`, `st.dataframe` |
| 7 | App completo | `@st.cache_data`, `st.multiselect`, `st.bar_chart` |
    """)
