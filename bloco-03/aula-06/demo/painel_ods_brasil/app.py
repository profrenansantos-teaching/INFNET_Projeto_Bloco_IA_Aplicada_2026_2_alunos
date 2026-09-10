"""
Painel de Indicadores Sustentáveis do Brasil — v4 (Aula 6: interação dinâmica)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v3 PARA A v4 (subcompetência 2.2):
  · FORMULÁRIO (st.form): quatro filtros enviados em LOTE — um rerun, não quatro;
  · WIDGETS: multiselect, slider, radio, checkbox, button, download_button;
  · MEMÓRIA (st.session_state): a lista de UFs favoritas sobrevive aos reruns;
  · CONTROLE DE FLUXO (st.stop): filtro sem resultado avisa em vez de quebrar;
  · lógica de filtrar/ordenar/exportar isolada em src/transformacoes.py.

A regra que explica tudo: A CADA INTERAÇÃO o Streamlit reexecuta este arquivo
inteiro, de cima para baixo. Variável comum é zerada; só o que está em
st.session_state (e no cache) sobrevive.

Como rodar:
    pip install -r requirements.txt
    streamlit run app.py

Como publicar: ver DEPLOY.md (o mesmo repositório da Aula 5 — basta um git push).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from src.data_access import carregar_dados
from src.transformacoes import (
    CRITERIOS,
    comparar,
    faixa_populacao,
    filtrar,
    ordenar,
    para_csv,
    resumo,
)

VERSAO = "v4 — Aula 6 (interatividade)"

st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")
st.title("🌱 Painel de Indicadores Sustentáveis do Brasil")


# ---------------------------------------------------------------- dados (cache)
@st.cache_data(ttl=3600)
def obter_dados():
    return carregar_dados()


with st.spinner("Coletando dados do IBGE…"):
    dados, fonte = obter_dados()

st.caption(f"Fonte: {fonte} · {len(dados)} UFs")

regioes_disponiveis = sorted({linha["regiao"] for linha in dados})
pop_minima, pop_maxima = faixa_populacao(dados)

# ---------------------------------------------------------------- memória de sessão
# Inicializar ANTES de usar: na primeira execução a chave ainda não existe.
if "favoritas" not in st.session_state:
    st.session_state.favoritas = []

# ---------------------------------------------------------------- formulário (1 rerun)
with st.sidebar:
    st.header("Filtros")
    with st.form("filtros"):
        regioes = st.multiselect("Regiões", regioes_disponiveis, default=regioes_disponiveis)
        populacao_minima = st.slider(
            "População mínima",
            min_value=pop_minima,
            max_value=pop_maxima,
            value=pop_minima,
            step=100_000,
        )
        criterio = st.radio("Ordenar por", list(CRITERIOS), index=0)
        mostrar_tabela = st.checkbox("Mostrar a tabela de dados", value=True)
        aplicar = st.form_submit_button("Aplicar filtros")

    if aplicar:
        st.success("Filtros aplicados.")

# ---------------------------------------------------------------- lógica (camada isolada)
filtrados = ordenar(filtrar(dados, regioes, populacao_minima), criterio)

# ---------------------------------------------------------------- controle de fluxo
if not filtrados:
    st.warning(
        "Nenhuma UF atende a esses filtros. Diminua a população mínima "
        "ou selecione mais regiões na barra lateral."
    )
    st.stop()          # interrompe o script aqui: nada abaixo é executado

# ---------------------------------------------------------------- métricas
numeros = resumo(filtrados)
col1, col2, col3 = st.columns(3)
col1.metric("UFs exibidas", numeros["ufs"], delta=numeros["ufs"] - len(dados))
col2.metric("Regiões", numeros["regioes"])
col3.metric("População somada", f"{numeros['populacao']:,}".replace(",", "."))

# ---------------------------------------------------------------- comparador (session_state)
st.markdown("### ⭐ Comparador de UFs")
st.caption(
    "As UFs marcadas continuam no comparador **mesmo quando você muda os filtros** — "
    "é isso que o st.session_state garante, e é o que uma variável comum não faria."
)

esq, dir_ = st.columns([4, 1])
uf_escolhida = esq.selectbox(
    "UF para comparar",
    [linha["uf"] for linha in filtrados],
    label_visibility="collapsed",
)
if dir_.button("Comparar"):
    if uf_escolhida not in st.session_state.favoritas:
        st.session_state.favoritas.append(uf_escolhida)

# comparar() recebe `dados` (base completa), não `filtrados`: uma UF marcada
# permanece na comparação ainda que o filtro atual a exclua.
comparadas = comparar(dados, st.session_state.favoritas)

if comparadas:
    st.dataframe(comparadas, hide_index=True)
    st.bar_chart(comparadas, x="uf", y="populacao_2025", height=240)

    fora_do_filtro = [
        uf for uf in st.session_state.favoritas
        if uf not in {linha["uf"] for linha in filtrados}
    ]
    if fora_do_filtro:
        st.info(
            "No comparador, mas fora do filtro atual: " + " · ".join(fora_do_filtro)
            + " — a comparação sobreviveu à mudança de filtro."
        )
    if st.button("Limpar comparador"):
        st.session_state.favoritas = []
else:
    st.caption("Escolha uma UF e clique em **Comparar** para montar a comparação.")

# ---------------------------------------------------------------- gráfico
st.markdown("### 📊 População por UF")
st.bar_chart(filtrados, x="uf", y="populacao_2025", height=380)

# ---------------------------------------------------------------- tabela + download
if mostrar_tabela:
    st.markdown("### 📋 Dados filtrados")
    st.dataframe(filtrados, hide_index=True)

st.download_button(
    "⬇ Baixar CSV do que está na tela",
    data=para_csv(filtrados),
    file_name="painel_ods_filtrado.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    f"{VERSAO} · Fonte: IBGE — População residente estimada (2025), tabela 6579. "
    "Próxima etapa: extração de conteúdo web (Etapa 4)."
)
