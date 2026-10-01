import streamlit as st

st.title("🧠 Memória")
# Esta linha supõe que 'marcadas' já existe. Com 'Inicializar no roteador'
# desligado e o link direto aberto numa aba nova, ela não existe.
st.write("UFs marcadas:", len(st.session_state.marcadas))
st.write("Tudo o que a sessão guarda agora:")
st.json(dict(st.session_state))
