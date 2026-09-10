"""
Painel de Indicadores Sustentáveis do Brasil — v5 (Aula 7: extração de conteúdo web)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v4 PARA A v5 (subcompetência 2.4):
  · SEGUNDA FONTE: notícias raspadas da Agência Brasil (EBC), que não tem API;
  · src/coleta_web.py — o raspador, executado SEPARADAMENTE (não pelo app);
  · src/noticias.py — leitura do CSV produzido pela coleta (Python puro);
  · o painel passa a mostrar DUAS origens: API (IBGE) e WebScraping (EBC).

POR QUE O APP NÃO RASPA: o robots.txt da Agência Brasil pede 10 segundos entre
requisições. Um app que raspasse a cada rerun quebraria esse pedido na primeira
interação — e amarraria o painel publicado à saúde de um site de terceiros.
Raspagem é etapa de COLETA (roda antes, grava arquivo); o app é etapa de USO.

Como rodar:
    pip install -r requirements.txt
    python -m src.coleta_web        # coleta as notícias -> data/processed/
    streamlit run app.py

Como publicar: ver DEPLOY.md (o mesmo repositório da Aula 5 — basta um git push).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from src.data_access import carregar_dados
from src.noticias import (
    carregar_noticias,
    filtrar_noticias,
    metadados,
    resumo_coleta,
    secoes_disponiveis,
)
from src.transformacoes import (
    CRITERIOS,
    comparar,
    faixa_populacao,
    filtrar,
    ordenar,
    para_csv,
    resumo,
)

VERSAO = "v5 — Aula 7 (extração de conteúdo web)"

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

# ---------------------------------------------------------------- notícias (WebScraping)
# Segunda fonte do painel. Nenhuma linha abaixo acessa a internet: o arquivo já
# foi produzido por `python -m src.coleta_web`, que rodou ANTES e à parte.
st.divider()
st.markdown("### 📰 O que a imprensa está publicando")


@st.cache_data(ttl=600)
def obter_noticias():
    return carregar_noticias(), metadados()


noticias, meta = obter_noticias()

if not noticias:
    st.info(
        "Ainda não há notícias coletadas. No terminal, dentro da pasta do projeto, rode:  "
        "`python -m src.coleta_web`  — e recarregue esta página."
    )
else:
    numeros = resumo_coleta(noticias)
    st.caption(
        f"Coleta de {meta.get('coletado_em', '—')} · {numeros['noticias']} notícias em "
        f"{numeros['secoes']} seções · {numeros['palavras']:,} palavras de texto "
        f"({numeros['com_texto']} matérias abertas).".replace(",", ".")
    )

    secoes_noticias = st.multiselect(
        "Seções",
        secoes_disponiveis(noticias),
        default=secoes_disponiveis(noticias),
        key="secoes_noticias",
    )
    recorte = filtrar_noticias(noticias, secoes_noticias)

    if not recorte:
        st.warning("Nenhuma seção selecionada. Escolha ao menos uma acima.")
    else:
        st.dataframe(
            [
                {
                    "Seção": linha["secao"],
                    "Manchete": linha["titulo"],
                    "Publicado em": linha["publicado_em"] or "—",
                    "Palavras": linha["palavras"],
                    "Link": linha["url"],
                }
                for linha in recorte
            ],
            hide_index=True,
            column_config={"Link": st.column_config.LinkColumn("Link", display_text="abrir")},
        )
        st.download_button(
            "⬇ Baixar CSV das notícias",
            data=para_csv(recorte),
            file_name="noticias_coletadas.csv",
            mime="text/csv",
        )

    st.caption(
        f"Fonte: {meta.get('site', 'Agência Brasil (EBC)')} · "
        f"{meta.get('licenca', 'Creative Commons Atribuição 3.0 Brasil')}. "
        "Conteúdo reutilizado com atribuição, como a licença exige."
    )

st.divider()
st.caption(
    f"{VERSAO} · Fontes: IBGE — população residente estimada (2025), tabela 6579 (API) · "
    "Agência Brasil/EBC — manchetes (WebScraping). "
    "Próxima aula: upload/download de arquivos, cache e estado de sessão."
)
