import streamlit as st

st.session_state.setdefault("indicadores_rodou", 0)
st.session_state.indicadores_rodou += 1

st.title("📊 Indicadores")
st.metric("Esta página rodou", st.session_state.indicadores_rodou)
st.caption("Ela só conta quando é a página aberta. O roteador conta sempre.")
