"""
Passo 2 — O jeito atual: um ROTEADOR com st.navigation.

    app.py          <- o roteador: roda em TODO rerun, em toda página
    paginas/
        inicio.py
        indicadores.py
        sobre.py

O que observar (os contadores estão na barra lateral e no topo de cada página):
  1. o contador do ROTEADOR sobe a cada clique, em qualquer página;
  2. o contador de uma PÁGINA só sobe quando ela é a página aberta;
  3. trocar de página é um rerun como outro qualquer (o modelo da Aula 6);
  4. o menu mostra o `title` e o `icon` de cada st.Page, agrupados por seção —
     e a URL de cada página vem do nome do arquivo (/indicadores, /sobre).

Rodar (de dentro desta pasta):
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Passo 2 · Roteador", page_icon="🧭")

# Tudo o que está ANTES de pagina.run() acontece em TODA página.
st.session_state.setdefault("roteador_rodou", 0)
st.session_state.roteador_rodou += 1

pagina = st.navigation(
    {
        "Painel": [
            st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
            st.Page("paginas/indicadores.py", title="Indicadores", icon="📊"),
        ],
        "Sobre o projeto": [
            st.Page("paginas/sobre.py", title="Dados e método", icon="ℹ️"),
        ],
    }
)

st.sidebar.metric("O roteador rodou", st.session_state.roteador_rodou)
st.sidebar.caption(f"Página escolhida neste rerun: **{pagina.title}**")

pagina.run()          # só a página escolhida roda — as outras, não
