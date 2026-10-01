import streamlit as st

REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

st.title("🔎 Filtros")

# Padrão da v7: o valor inicial mora no st.session_state; o widget só aponta para ele.
# (Passar TAMBÉM default=... ao widget faz o Streamlit reclamar no terminal quando a
# chave é regravada pelo roteador.)
st.session_state.setdefault("regioes", REGIOES)
regioes = st.multiselect("Regiões", REGIOES, key="regioes")
st.write(f"Você está vendo **{len(regioes)}** região(ões).")

# Esta página CRIA 'marcadas' — se o roteador não criar antes.
st.session_state.setdefault("marcadas", [])
if st.button("Marcar SP"):
    if "SP" not in st.session_state.marcadas:
        st.session_state.marcadas.append("SP")
st.write("Marcadas:", st.session_state.marcadas)

st.info("Agora escolha só 'Nordeste', vá a 'Outra página' e volte. O filtro ficou?")
