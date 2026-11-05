"""Página Palavras — as estatísticas do texto coletado (a "nuvem de palavras" do TP2)."""

import streamlit as st

from comum import contar_palavras
from src.analise_texto import carregar_texto

st.title("🔤 As palavras que dominam a cobertura")

texto = carregar_texto()
if not texto:
    st.info(
        "Sem texto coletado ainda. Rode `python -m src.coleta_web` para gerar "
        "`data/processed/noticias_texto.txt`."
    )
    st.stop()

st.session_state.setdefault("qtd_palavras", 20)
quantas = st.slider("Quantas palavras mostrar", 5, 40, step=5, key="qtd_palavras")
top, numeros = contar_palavras(texto, quantas)

a, b, c = st.columns(3)
a.metric("Palavras no corpus", f"{numeros['palavras']:,}".replace(",", "."))
b.metric("Fora as palavras vazias", f"{numeros['palavras_uteis']:,}".replace(",", "."))
c.metric("Vocabulário distinto", f"{numeros['vocabulario']:,}".replace(",", "."))

st.bar_chart(top, x="palavra", y="ocorrencias", height=340)
st.caption(
    "É a nuvem de palavras do TP2 — com escala, que a nuvem não tem. As palavras vazias "
    "(de, para, pelo…) saem por uma lista mantida à mão em `src/analise_texto.py`: o que "
    "conta como palavra vazia é decisão editorial sua."
)
