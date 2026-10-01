"""
Passo 3 — O estado entre páginas: os DOIS tropeços da v7, com o botão de liga/desliga.

Tropeço 1 · O FILTRO QUE ESQUECIA
    Escolha regiões na página Filtros, vá a "Outra página", volte.
    Com a preservação DESLIGADA, o filtro volta ao padrão.
    Por quê: no rerun em que um widget com key não é desenhado, o Streamlit
    apaga a chave dele do st.session_state. Trocar de página é esse rerun.

Tropeço 2 · O LINK DIRETO QUE QUEBRAVA
    Mude INICIALIZAR_NO_ROTEADOR para False (logo abaixo dos imports), salve, abra
    uma aba NOVA do navegador e digite o endereço direto da página Memória:
        http://localhost:8501/memoria
    Ela lê st.session_state.marcadas, que só a página Filtros criava — e quebra.
    (Na aba antiga, onde você já passou por Filtros, ela funciona. É isso que
    esconde o defeito: quem desenvolve sempre entra pela porta da frente.)

Rodar (de dentro desta pasta):
    streamlit run app.py
"""

import streamlit as st

# Tropeço 2: mude para False, salve e abra /memoria numa aba NOVA.
# (É uma constante, e não um botão, de propósito: uma aba nova é uma sessão
# nova, e um botão voltaria ao valor padrão justamente no teste que importa.)
INICIALIZAR_NO_ROTEADOR = True

st.set_page_config(page_title="Passo 3 · Estado entre páginas", page_icon="🧠")

# O interruptor fica no ROTEADOR: como ele é desenhado em todo rerun, nunca some
# da tela — e, por isso, nunca é "esquecido".
with st.sidebar:
    st.header("Interruptor")
    preservar = st.toggle("Preservar os filtros", value=False)

if INICIALIZAR_NO_ROTEADOR:
    # Correção do tropeço 2: a memória que mais de uma página usa nasce AQUI,
    # antes de qualquer página — venha o usuário de onde vier.
    st.session_state.setdefault("marcadas", [])

if preservar:
    # Correção do tropeço 1: regravar a chave a faz ser tratada como valor NOSSO,
    # e não mais como estado do widget — o Streamlit deixa de limpá-la.
    for chave in ("regioes",):
        if chave in st.session_state:
            st.session_state[chave] = st.session_state[chave]

pagina = st.navigation(
    [
        st.Page("paginas/filtros.py", title="Filtros", icon="🔎", default=True),
        st.Page("paginas/outra.py", title="Outra página", icon="📄"),
        st.Page("paginas/memoria.py", title="Memória", icon="🧠"),
    ]
)
pagina.run()
