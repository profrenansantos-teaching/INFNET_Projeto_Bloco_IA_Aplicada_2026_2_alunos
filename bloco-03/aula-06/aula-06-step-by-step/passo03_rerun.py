"""
Passo 3 — A regra que explica tudo: o script roda INTEIRO a cada interação.

Este passo não ensina um widget novo: ensina o MODELO DE EXECUÇÃO. Sem ele, o
comportamento do Streamlit parece aleatório; com ele, tudo faz sentido.

    "1. By default, information is not stored across reruns of the app.
     2. On user input, Streamlits are rerun top-to-bottom."   [Richards, p87]

Rode e clique várias vezes no botão. O contador COMUM nunca passa de 1.

Rodar:  streamlit run passo03_rerun.py
"""

import time

import streamlit as st

st.title("Passo 3 · Cada clique reexecuta o arquivo inteiro")

# Esta linha roda A CADA interação — é a prova visível do rerun.
st.caption(f"Este script foi executado às {time.strftime('%H:%M:%S')}")

st.header("Contador com variável comum")
contador = 0                      # nasce zerado em TODO rerun
if st.button("Somar 1 (variável comum)"):
    contador += 1
st.metric("Valor", contador)
st.error(
    "Clique quantas vezes quiser: nunca passa de 1. A linha `contador = 0` é "
    "reexecutada antes do `if`, então o valor anterior já foi perdido."
)

st.divider()

st.header("Contador com st.session_state")
# A inicialização só acontece na PRIMEIRA execução da sessão.
if "contador_estado" not in st.session_state:
    st.session_state.contador_estado = 0

if st.button("Somar 1 (session_state)"):
    st.session_state.contador_estado += 1
st.metric("Valor", st.session_state.contador_estado)
st.success(
    "Aqui o valor sobrevive: st.session_state é um dicionário global que persiste "
    "durante a sessão do usuário. [Richards, p91]"
)

st.divider()
st.subheader("O que sobrevive a um rerun?")
st.markdown(
    """
| Sobrevive | Não sobrevive |
|-----------|---------------|
| `st.session_state` | variáveis comuns do script |
| resultado de `@st.cache_data` | resultado de função sem cache |
| valor do widget (ligado à sua chave) | qualquer coisa recalculada no topo |
"""
)
st.caption("Recarregar a página (F5) começa uma sessão nova — e apaga o session_state.")
