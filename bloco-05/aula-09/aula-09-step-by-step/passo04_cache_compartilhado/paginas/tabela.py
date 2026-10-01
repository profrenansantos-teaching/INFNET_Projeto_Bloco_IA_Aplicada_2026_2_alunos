import time

import streamlit as st

from comum import carregar_base

st.title("📋 Tabela")
relogio = time.perf_counter()
base = carregar_base()
st.metric("Custo desta leitura", f"{(time.perf_counter() - relogio) * 1000:.0f} ms")
st.dataframe(base, hide_index=True)
