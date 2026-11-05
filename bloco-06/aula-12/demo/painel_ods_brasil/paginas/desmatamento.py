"""Página Desmatamento — a quarta fonte: uma página DINÂMICA, coletada com Selenium.

O que esta página NÃO faz, por escolha: abrir navegador. A coleta
(src/coleta_dinamica.py) roda à parte, no seu terminal, com o ambiente de
requirements-coleta.txt. Esta página só lê o CSV que ela gravou — leve, rápida, e
de pé mesmo quando o site do INPE não está. (Selenium no app publicado é possível,
com preço: ver DEPLOY.md §10.1.)
"""

import streamlit as st

from comum import obter_desmatamento
from src.desmatamento import comparar_anos, faixa_de_anos, filtrar, ranking_do_ano, ufs_disponiveis
from src.transformacoes import para_csv

st.title("🌳 Desmatamento na Amazônia Legal")
st.caption(
    "Taxa anual de desmatamento por UF — PRODES/INPE. Os dados vêm de uma página que "
    "só mostra a tabela depois que o JavaScript roda; foram coletados com Selenium, à parte."
)

dados, meta = obter_desmatamento()
if not dados:
    st.info(
        "Ainda não há coleta. No terminal, com o ambiente da coleta, rode:\n\n"
        "`pip install -r requirements-coleta.txt`  e depois  `python -m src.coleta_dinamica`"
    )
    st.stop()

todas = ufs_disponiveis(dados)
primeiro, ultimo = faixa_de_anos(dados)

# Filtros desta página, no padrão da Aula 9: valor inicial no session_state,
# widget só com key, e o roteador os preserva (CHAVES_PRESERVADAS em comum.py).
st.session_state.setdefault("ufs_prodes", todas)
st.session_state.setdefault("anos_prodes", (2004, ultimo))
ufs = st.multiselect("UFs da Amazônia Legal", todas, key="ufs_prodes")
ano_inicial, ano_final = st.slider("Período", primeiro, ultimo, key="anos_prodes")

if not ufs:
    st.warning("Escolha ao menos uma UF acima.")
    st.stop()

recorte = filtrar(dados, ufs, ano_inicial, ano_final)
c = comparar_anos(recorte, ano_final)

a, b, d = st.columns(3)
a.metric(f"Desmatado em {ano_final} (UFs escolhidas)", f"{c['total']:,.0f} km²".replace(",", "."),
         delta=(f"{c['variacao_pct']:+.1f}% sobre {ano_final - 1}" if c["variacao_pct"] is not None else None),
         delta_color="inverse")       # aqui, subir é ruim
b.metric("UFs no recorte", len(ufs))
d.metric("Anos no recorte", ano_final - ano_inicial + 1)

st.markdown("### Evolução por UF")
# Ano como TEXTO no gráfico: como número, o eixo mostrava "2,004" (separador de milhar).
serie = [{"ano": str(l["ano"]), "uf": l["uf"], "area_km2": l["area_km2"]} for l in recorte]
st.line_chart(serie, x="ano", y="area_km2", color="uf", x_label="Ano",
              y_label="km² desmatados", height=360)

st.markdown(f"### Quem mais desmatou em {ano_final}")
st.bar_chart(ranking_do_ano(recorte, ano_final), x="uf", y="area_km2", x_label="UF",
             y_label="km² desmatados", height=280)

with st.expander("Ver a tabela e baixar o CSV"):
    st.dataframe(recorte, hide_index=True)
    st.download_button(
        "⬇ Baixar CSV do recorte",
        data=para_csv(recorte),
        file_name="desmatamento_prodes_recorte.csv",
        mime="text/csv",
    )

# A licença é CC BY-SA 4.0: citar a fonte E manter a mesma licença no que derivar.
st.caption(
    f"Fonte: {meta.get('site', 'INPE/PRODES — TerraBrasilis')} · {meta.get('licenca', 'CC BY-SA 4.0')} · "
    f"coletado em {meta.get('coletado_em', '—')} com {meta.get('ferramenta', 'Selenium')}. "
    "O CSV baixado aqui herda a mesma licença (CompartilhaIgual)."
)
