import streamlit as st

st.title("📄 Outra página")
st.write("Nesta página o multiselect de regiões NÃO é desenhado.")
st.write("Chave 'regioes' ainda está na memória durante ESTE rerun?", "regioes" in st.session_state)
st.caption("A limpeza acontece no FIM do rerun — por isso a resposta acima ainda pode ser 'True'.")
