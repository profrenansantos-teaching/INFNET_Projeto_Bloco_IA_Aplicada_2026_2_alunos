"""O que todas as páginas usam — a leitura cara, UMA vez."""

import time

import streamlit as st

# Contador do PROCESSO (não da sessão): quantas vezes a leitura cara rodou de
# verdade neste servidor. Serve só para enxergar o cache funcionando.
CONTAGEM = {"execucoes": 0}


@st.cache_data(show_spinner="Lendo a base cara…")
def carregar_base() -> list[dict]:
    """Finge ser uma coleta demorada (1,2 s) e devolve 27 linhas."""
    CONTAGEM["execucoes"] += 1
    time.sleep(1.2)
    return [{"uf": f"UF{i:02d}", "valor": i * 10} for i in range(1, 28)]
