"""Página Indicadores por UF — filtros, métricas, gráfico, tabela e download.

É o corpo da v6, com uma diferença que parece pequena e não é: os filtros
agora precisam SOBREVIVER à troca de página. Por isso:
  · cada widget tem uma key;
  · o valor inicial vem do st.session_state (setdefault), e NÃO do parâmetro
    default/value do widget — passar os dois faz o Streamlit reclamar;
  · o roteador chama preservar_filtros() antes desta página rodar.
"""

import streamlit as st

from comum import obter_dados
from src.transformacoes import CRITERIOS, faixa_populacao, filtrar, ordenar, para_csv, resumo

st.title("📊 Indicadores por UF")

dados, fonte, _ = obter_dados()
st.caption(f"Fonte: {fonte} · {len(dados)} UFs")

regioes_disponiveis = sorted({linha["regiao"] for linha in dados})
pop_minima, pop_maxima = faixa_populacao(dados)

# Valores iniciais — só na primeira visita; depois vale o que o usuário escolheu.
st.session_state.setdefault("regioes", regioes_disponiveis)
st.session_state.setdefault("populacao_minima", pop_minima)
st.session_state.setdefault("criterio", list(CRITERIOS)[0])
st.session_state.setdefault("mostrar_tabela", True)

# ---------------------------------------------------------------- filtros (desta página)
# A barra lateral tem uma parte COMUM (o menu e o rodapé, vindos do roteador) e
# uma parte DESTA PÁGINA (o formulário abaixo). Nas outras páginas ele não aparece —
# e é assim que deve ser: um filtro que não filtra nada ali só confunde.
with st.sidebar:
    st.header("Filtros")
    with st.form("filtros"):
        regioes = st.multiselect("Regiões", regioes_disponiveis, key="regioes")
        populacao_minima = st.slider(
            "População mínima",
            min_value=pop_minima,
            max_value=pop_maxima,
            step=100_000,
            key="populacao_minima",
        )
        criterio = st.radio("Ordenar por", list(CRITERIOS), key="criterio")
        mostrar_tabela = st.checkbox("Mostrar a tabela de dados", key="mostrar_tabela")
        st.form_submit_button("Aplicar filtros")

filtrados = ordenar(filtrar(dados, regioes, populacao_minima), criterio)

if not filtrados:
    st.warning(
        "Nenhuma UF atende a esses filtros. Diminua a população mínima "
        "ou selecione mais regiões na barra lateral."
    )
    st.stop()

numeros = resumo(filtrados)
col1, col2, col3 = st.columns(3)
col1.metric("UFs exibidas", numeros["ufs"], delta=numeros["ufs"] - len(dados))
col2.metric("Regiões", numeros["regioes"])
col3.metric("População somada", f"{numeros['populacao']:,}".replace(",", "."))

st.markdown("### População por UF")
st.bar_chart(filtrados, x="uf", y="populacao_2025", height=380)

if mostrar_tabela:
    st.markdown("### Dados filtrados")
    st.dataframe(filtrados, hide_index=True)

st.download_button(
    "⬇ Baixar CSV do que está na tela",
    data=para_csv(filtrados),
    file_name="painel_ods_filtrado.csv",
    mime="text/csv",
)

st.page_link("paginas/comparador.py", label="Comparar UFs específicas", icon="⭐")
