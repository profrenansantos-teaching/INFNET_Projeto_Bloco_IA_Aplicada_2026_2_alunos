"""
Passo 4 — Onde mora a leitura cara num app de várias páginas.

    comum.py                 carregar_base(), cacheada, definida UMA vez
    paginas/tabela.py        importa de comum        -> usa O MESMO cache
    paginas/grafico.py       importa de comum        -> usa O MESMO cache
    paginas/copia.py         COPIOU a função e mudou um comentário
                             -> é OUTRA função para o cache: paga de novo

Roteiro: abra Tabela (1,2 s), depois Gráfico (instantâneo: mesmo cache), depois
Cópia (1,2 s de novo). Olhe o contador na barra lateral.

Rodar (de dentro desta pasta):
    streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

import comum

st.set_page_config(page_title="Passo 4 · Cache compartilhado", page_icon="⚡")

pagina = st.navigation(
    [
        st.Page("paginas/tabela.py", title="Tabela", icon="📋", default=True),
        st.Page("paginas/grafico.py", title="Gráfico", icon="📊"),
        st.Page("paginas/copia.py", title="Cópia (anti-padrão)", icon="⚠️"),
    ]
)
pagina.run()

# Depois da página, para o número já incluir o que ela acabou de fazer.
st.sidebar.metric("A leitura cara rodou de verdade", comum.CONTAGEM["execucoes"])
if st.sidebar.button("Limpar o cache"):
    st.cache_data.clear()
    st.rerun()
