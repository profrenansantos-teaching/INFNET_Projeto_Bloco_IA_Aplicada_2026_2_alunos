import streamlit as st

st.session_state.setdefault("sobre_rodou", 0)
st.session_state.sobre_rodou += 1

st.title("ℹ️ Dados e método")
st.metric("Esta página rodou", st.session_state.sobre_rodou)
st.write("Contadores de todas as páginas (vêm do st.session_state, que é da SESSÃO):")
st.json({k: v for k, v in st.session_state.items() if k.endswith("_rodou")})
