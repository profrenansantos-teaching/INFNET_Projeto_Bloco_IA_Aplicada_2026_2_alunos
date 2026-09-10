"""
Passo 1 — O catálogo básico: o widget DEVOLVE UM VALOR.

A ideia que organiza o capítulo inteiro: em Streamlit um widget não "dispara um
evento" nem chama uma função de callback. Ele é uma EXPRESSÃO que devolve o valor
escolhido pelo usuário — e o script inteiro roda de novo com esse valor.

    escolha = st.radio("...", ["A", "B"])   # escolha JÁ É "A" ou "B"

Fonte: RAGHAVENDRA, cap. 5 "Buttons and Sliders" (p114-127).

Rodar:  streamlit run passo01_widgets_basicos.py
"""

import streamlit as st

st.title("Passo 1 · O widget devolve um valor")

# ---------------------------------------------------------------- st.button
# Devolve True SOMENTE no rerun causado pelo clique. No rerun seguinte volta a False.
st.header("1. st.button — um True passageiro")
if st.button("Clique aqui"):
    st.write("Você clicou. (Mexa em qualquer outra coisa e esta mensagem some.)")
else:
    st.write("Você ainda não clicou — ou já houve outro rerun depois do clique.")

# ---------------------------------------------------------------- st.radio
# Uma escolha entre várias. Devolve a opção escolhida.  [Raghavendra, p115-117]
st.header("2. st.radio — uma opção entre várias")
regiao = st.radio("Região do Brasil", ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
st.write("Você escolheu:", regiao)

# ---------------------------------------------------------------- st.checkbox
# Liga/desliga. Devolve True ou False.  [Raghavendra, p117-118]
st.header("3. st.checkbox — liga/desliga")
mostrar_detalhes = st.checkbox("Mostrar detalhes", value=True)
if mostrar_detalhes:
    st.info("O checkbox é o jeito mais simples de esconder/mostrar um pedaço da tela.")

# ---------------------------------------------------------------- st.selectbox
# Menu suspenso: UMA opção.  [Raghavendra, p119-120]
st.header("4. st.selectbox — menu suspenso (uma opção)")
indicador = st.selectbox("Indicador", ["População", "Saneamento", "Área"])
st.write("Indicador selecionado:", indicador)

# ---------------------------------------------------------------- st.multiselect
# Menu suspenso: VÁRIAS opções. Devolve uma LISTA.  [Raghavendra, p121-123]
st.header("5. st.multiselect — várias opções (devolve uma lista)")
regioes = st.multiselect(
    "Comparar regiões",
    ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
    default=["Sudeste", "Sul"],
)
st.write("Tipo do retorno:", type(regioes).__name__, "· conteúdo:", regioes)

st.divider()
st.caption(
    "Note que NENHUM widget acima precisou de callback. Cada um é uma expressão "
    "que devolve um valor — e o script roda de novo com ele."
)
