"""Página Início — o problema, e o que cada página do painel responde.

É a porta de entrada: quem chega pela primeira vez precisa saber POR QUE o
painel existe e ONDE está cada resposta. Os links usam st.page_link, que leva
à página sem recarregar o navegador (o estado da sessão vai junto).
"""

import streamlit as st

from comum import obter_dados, obter_noticias
from src.transformacoes import resumo

st.title("🌱 Painel de Indicadores Sustentáveis do Brasil")
st.markdown(
    "Indicadores socioambientais brasileiros estão espalhados por portais diferentes. "
    "Este painel reúne **dados oficiais do IBGE** e **o que a imprensa pública está "
    "noticiando** para comparar as Unidades da Federação — alinhado aos **ODS 6** "
    "(água e saneamento), **ODS 11** (cidades sustentáveis) e, com os dados do PRODES/INPE, "
    "**ODS 15** (vida terrestre) da Agenda 2030."
)

dados, fonte, _ = obter_dados()
noticias, meta = obter_noticias()
numeros = resumo(dados)

a, b, c = st.columns(3)
a.metric("UFs com dado", numeros["ufs"])
b.metric("População coberta", f"{numeros['populacao']:,}".replace(",", "."))
c.metric("Notícias coletadas", len(noticias))

st.markdown("### O que cada página responde")

# Uma pergunta, uma página. Se duas páginas respondem à mesma pergunta, uma
# delas sobra; se uma página responde a três, ela deveria ser três.
st.page_link("paginas/indicadores.py", label="Indicadores por UF", icon="📊")
st.caption("Quais UFs concentram a população, dentro dos filtros que eu escolher?")

st.page_link("paginas/comparador.py", label="Comparador de UFs", icon="⭐")
st.caption("Como estas UFs específicas se comparam entre si?")

st.page_link("paginas/desmatamento.py", label="Desmatamento (PRODES)", icon="🌳")
st.caption("Quanto a Amazônia Legal perdeu de floresta, UF a UF, ano a ano?")

st.page_link("paginas/noticias.py", label="Notícias", icon="📰")
st.caption("O que a imprensa pública está publicando — e o que eu mesmo coletei?")

st.page_link("paginas/palavras.py", label="Palavras", icon="🔤")
st.caption("Quais assuntos dominam a cobertura?")

st.page_link("paginas/sobre.py", label="Dados e método", icon="ℹ️")
st.caption("De onde vem cada número, sob qual licença, e quanto custa buscá-lo?")

if st.session_state.favoritas:
    st.info(
        "Você já marcou no comparador: " + " · ".join(st.session_state.favoritas)
        + " — a marcação atravessa as páginas."
    )

st.caption(f"Fonte dos indicadores: {fonte}.")
