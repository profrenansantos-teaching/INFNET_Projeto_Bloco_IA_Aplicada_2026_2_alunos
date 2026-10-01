import streamlit as st

st.session_state.setdefault("inicio_rodou", 0)
st.session_state.inicio_rodou += 1

st.title("🏠 Início")
st.metric("Esta página rodou", st.session_state.inicio_rodou)
st.caption("Clique no botão abaixo algumas vezes e compare com o contador do roteador.")
st.button("Um botão qualquer (só provoca rerun)")

st.markdown("#### Dois jeitos de levar o usuário a outra página")
st.page_link("paginas/indicadores.py", label="st.page_link — um link, como no menu", icon="📊")
if st.button("st.switch_page — ir por código, depois de um clique"):
    st.switch_page("paginas/sobre.py")
