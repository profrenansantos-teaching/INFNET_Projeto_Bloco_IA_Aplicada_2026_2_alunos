"""
Passo 2 — Slider e entradas numéricas/textuais.

⚠️ NOTA DE FONTE (honestidade intelectual, exigida pelo curso):
o capítulo 5 do Raghavendra chama-se "Buttons and Sliders", mas NÃO traz nenhum
exemplo de st.slider fora do contexto de barra lateral — o próprio resumo do
capítulo (p127) lista apenas botão, rádio, checkbox, drop-down, multiselect,
download, barra de progresso e spinner. O que está aqui sobre st.slider vem da
documentação oficial do Streamlit e foi verificado nesta versão (>= 1.40).
As entradas de texto/número seguem o cap. 6 ("Forms", p128-134).

Rodar:  streamlit run passo02_slider_e_entradas.py
"""

import streamlit as st

st.title("Passo 2 · Slider e entradas")

# ---------------------------------------------------------------- st.slider
st.header("1. st.slider — escolher dentro de uma faixa")
populacao_minima = st.slider(
    "População mínima",
    min_value=50_000_000,
    max_value=50_000_000,
    value=1_000_000,
    step=100_000,
)
st.write(f"Filtrar UFs com pelo menos {populacao_minima:,} habitantes".replace(",", "."))

st.warning(
    "Armadilha real: se min_value == max_value o st.slider levanta exceção. "
    "Quando os limites vêm dos dados (min/max de uma coluna), garanta uma faixa "
    "de largura mínima — é o que faz faixa_populacao() em src/transformacoes.py."
)

# Slider de INTERVALO: passe uma tupla em value e ele devolve uma tupla.
faixa = st.slider("Faixa de população", 0, 50_000_000, (1_000_000, 20_000_000), step=100_000)
st.write("Retorno do slider de intervalo:", faixa, "· tipo:", type(faixa).__name__)

# ---------------------------------------------------------------- st.number_input
# Ordem posicional: mínimo, máximo, valor padrão, passo.  [Raghavendra, p133-134]
st.header("2. st.number_input — um número exato")
quantidade = st.number_input("Quantas UFs mostrar no ranking", 1, 27, 10, 1)
st.write("Top", quantidade)

# ---------------------------------------------------------------- st.text_input
# max_chars limita; type="password" esconde.  [Raghavendra, p129-131]
st.header("3. st.text_input — texto (e senha)")
busca = st.text_input("Buscar estado pelo nome", max_chars=40, placeholder="ex.: Bahia")
if busca:
    st.write("Buscando por:", busca)

senha = st.text_input("Campo de senha (só para ver o comportamento)", type="password")
st.caption(
    "Nunca compare com uma senha escrita no código: use st.secrets — "
    "foi o que vimos na Aula 5. [Richards, p191]"
)

# ---------------------------------------------------------------- st.date_input / st.color_picker
st.header("4. Outras entradas do cap. 6")
data = st.date_input("Data de referência do indicador")
cor = st.color_picker("Cor das barras do gráfico", "#4F81BD")
st.write("Data:", data, "· Cor:", cor)

st.divider()
st.caption("Todos devolvem valores Python comuns: int, str, date, tuple. Nada de mágica.")
