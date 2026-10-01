import time

import streamlit as st

from comum import carregar_base

st.title("📊 Gráfico")
relogio = time.perf_counter()
base = carregar_base()        # a MESMA função -> o MESMO cache da página Tabela
st.metric("Custo desta leitura", f"{(time.perf_counter() - relogio) * 1000:.0f} ms")
st.bar_chart(base, x="uf", y="valor")
