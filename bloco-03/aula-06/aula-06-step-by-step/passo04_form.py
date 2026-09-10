"""
Passo 4 — st.form: enviar os filtros em LOTE, não um por um.

O problema, nas palavras do autor do livro:

    "When input form data is changed by the user, the application needs to rerun,
     causing a bad user experience. To solve this issue of the application rerunning
     every time the user makes changes in the data, we can use the
     form_submit_button() function"        [Raghavendra, p157]

Este passo conta os reruns dos dois lados para você VER a diferença.

Regra, verificada nesta versão do Streamlit (não copiada do livro):
  · st.button comum DENTRO de um form            -> exceção
  · st.form_submit_button FORA de um form        -> exceção  [Raghavendra, p157]
  · st.form SEM submit                           -> NÃO levanta erro: o form
    aparece e simplesmente nunca envia nada. Versões antigas mostravam
    "Missing Submit Button"; hoje o defeito é silencioso — o pior tipo.

Rodar:  streamlit run passo04_form.py
"""

import streamlit as st

st.title("Passo 4 · Widgets soltos × formulário")

# Contador de reruns (usa session_state — passo 3).
if "reruns" not in st.session_state:
    st.session_state.reruns = 0
st.session_state.reruns += 1
st.metric("Reexecuções desta sessão", st.session_state.reruns)

esquerda, direita = st.columns(2)

# ------------------------------------------------------------------ sem formulário
with esquerda:
    st.subheader("❌ Sem formulário")
    st.caption("Cada mexida em um destes dispara um rerun na hora.")
    regiao_a = st.selectbox("Região", ["Todas", "Norte", "Sudeste", "Sul"], key="a1")
    minimo_a = st.slider("População mínima", 0, 50_000_000, 0, 1_000_000, key="a2")
    ordem_a = st.radio("Ordenar por", ["População", "Nome"], key="a3")
    so_capitais_a = st.checkbox("Só capitais", key="a4")
    st.write("Valores:", regiao_a, minimo_a, ordem_a, so_capitais_a)

# ------------------------------------------------------------------ com formulário
with direita:
    st.subheader("✅ Com st.form")
    st.caption("Mexa nos quatro à vontade: o app só reexecuta quando você clica.")
    with st.form("filtros"):
        regiao_b = st.selectbox("Região", ["Todas", "Norte", "Sudeste", "Sul"], key="b1")
        minimo_b = st.slider("População mínima", 0, 50_000_000, 0, 1_000_000, key="b2")
        ordem_b = st.radio("Ordenar por", ["População", "Nome"], key="b3")
        so_capitais_b = st.checkbox("Só capitais", key="b4")
        enviado = st.form_submit_button("Aplicar filtros")   # obrigatório
    if enviado:
        st.success("Filtros aplicados (1 rerun).")
    st.write("Valores:", regiao_b, minimo_b, ordem_b, so_capitais_b)

st.divider()
st.markdown(
    """
**Experimento (faça agora):** anote o contador; mexa nos **quatro** widgets da
esquerda e veja o contador subir de 4. Recarregue, mexa nos **quatro** da direita
e clique em *Aplicar*: o contador sobe **1**.

**Quando usar formulário:** quando os filtros só fazem sentido **juntos**, ou
quando cada rerun custa caro (coleta, modelo, consulta).
**Quando não usar:** quando você quer resposta imediata a cada mexida (um único
seletor, uma busca ao vivo).
"""
)
