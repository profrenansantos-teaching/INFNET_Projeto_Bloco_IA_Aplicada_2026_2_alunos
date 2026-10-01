"""O anti-padrão: copiar a função cacheada para dentro da página.

Enquanto a cópia for IDÊNTICA ao original, o Streamlit até a reconhece como a
mesma. Basta alguém editá-la — um comentário que seja — e ela vira OUTRA função
para o cache: a leitura cara roda de novo, e ninguém recebe erro nenhum.
"""

import time

import streamlit as st


@st.cache_data(show_spinner="Lendo a base cara (cópia)…")
def carregar_base() -> list[dict]:
    """Finge ser uma coleta demorada (1,2 s) e devolve 27 linhas."""
    import comum
    comum.CONTAGEM["execucoes"] += 1   # cópia "melhorada" por alguém, meses depois
    time.sleep(1.2)
    return [{"uf": f"UF{i:02d}", "valor": i * 10} for i in range(1, 28)]


st.title("⚠️ Cópia (anti-padrão)")
relogio = time.perf_counter()
base = carregar_base()
st.metric("Custo desta leitura", f"{(time.perf_counter() - relogio) * 1000:.0f} ms")
st.warning(
    "Mesma base, mesmo resultado — e a leitura cara rodou de novo. A cópia divergiu "
    "do original, e para o cache ela é outra função."
)
