"""Página Comparador de UFs — a razão de estado da Aula 6, agora ENTRE páginas.

As UFs marcadas moram em st.session_state.favoritas, que o roteador inicializa.
Por isso a marcação:
  · sobrevive à troca de filtro (já era assim na v6);
  · sobrevive à troca de PÁGINA (novo): marque aqui, vá a Notícias, volte;
  · não quebra quem abre o link direto desta página.
"""

import streamlit as st

from comum import obter_dados
from src.transformacoes import comparar, filtrar

st.title("⭐ Comparador de UFs")
st.caption(
    "As UFs marcadas continuam aqui quando você muda de página — é o st.session_state, "
    "que é da SESSÃO, e não de uma página."
)

dados, _, _ = obter_dados()

esq, dir_ = st.columns([4, 1])
uf_escolhida = esq.selectbox(
    "UF para comparar",
    sorted(linha["uf"] for linha in dados),
    label_visibility="collapsed",
)
if dir_.button("Comparar"):
    if uf_escolhida not in st.session_state.favoritas:
        st.session_state.favoritas.append(uf_escolhida)

comparadas = comparar(dados, st.session_state.favoritas)

if not comparadas:
    st.info("Escolha uma UF e clique em **Comparar** para montar a comparação.")
    st.stop()

st.dataframe(comparadas, hide_index=True)
st.bar_chart(comparadas, x="uf", y="populacao_2025", height=260)

# Os filtros da página Indicadores também estão na memória da sessão — então
# esta página pode LER o que o usuário escolheu lá. É estado atravessando páginas.
regioes = st.session_state.get("regioes")
if regioes is not None:
    no_filtro = {
        linha["uf"]
        for linha in filtrar(dados, regioes, st.session_state.get("populacao_minima", 0))
    }
    fora = [uf for uf in st.session_state.favoritas if uf not in no_filtro]
    if fora:
        st.info(
            "Marcadas aqui, mas fora do filtro que você deixou na página Indicadores: "
            + " · ".join(fora)
        )

if st.button("Limpar comparador"):
    st.session_state.favoritas = []
    st.rerun()
