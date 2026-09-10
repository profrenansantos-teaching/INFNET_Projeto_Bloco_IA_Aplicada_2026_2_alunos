"""
Passo 5 — st.session_state: dar memória ao app.

O exemplo canônico do livro é uma lista de tarefas que "esquece" o item anterior
[Richards, p87-90]. Aqui ele vira o COMPARADOR do Painel ODS: uma lista de UFs
favoritas que precisa acumular entre cliques.

    "Session State is a Streamlit feature that is a global dictionary that persists
     through a user's session."                                    [Richards, p91]

    "The session state holds the value of only the current session, and after
     refreshing, a new session state is created."               [Raghavendra, p183]

Rodar:  streamlit run passo05_session_state.py
"""

import streamlit as st

st.title("Passo 5 · A lista que lembra")

UFS = ["SP", "RJ", "MG", "BA", "PR", "RS", "PE", "CE", "PA", "AM"]

# ------------------------------------------------------------------ o jeito errado
st.header("❌ Sem memória")
favoritas_erradas = []                      # zerada em todo rerun
uf_a = st.selectbox("UF", UFS, key="sel_a")
if st.button("Favoritar (sem memória)"):
    favoritas_erradas.append(uf_a)
st.write("Favoritas:", favoritas_erradas or "—")
st.caption("Adicione duas UFs seguidas: a primeira desaparece. [Richards, p90]")

st.divider()

# ------------------------------------------------------------------ o jeito certo
st.header("✅ Com st.session_state")

# 1. INICIALIZAR — só na primeira execução da sessão.
if "favoritas" not in st.session_state:
    st.session_state.favoritas = []

# 2. LER e ESCREVER — como num dicionário comum.
uf_b = st.selectbox("UF", UFS, key="sel_b")
adicionar, limpar = st.columns(2)

if adicionar.button("Favoritar"):
    if uf_b in st.session_state.favoritas:
        st.info(f"{uf_b} já estava na lista.")
    else:
        st.session_state.favoritas.append(uf_b)

if limpar.button("Limpar lista"):
    st.session_state.favoritas = []

if st.session_state.favoritas:
    st.success("Favoritas: " + " · ".join(st.session_state.favoritas))
else:
    st.caption("Nenhuma favorita ainda.")

st.divider()

# ------------------------------------------------------------------ olhando por dentro
st.subheader("O session_state por dentro")
st.write("É um dicionário. Estas são as chaves desta sessão:")
st.json({chave: str(valor)[:60] for chave, valor in st.session_state.items()})

st.markdown(
    """
**As três regras:**

1. **Inicialize antes de usar** — `if "chave" not in st.session_state: ...`
   Sem isso, o primeiro rerun quebra com `KeyError`.
2. **`st.session_state.favoritas` e `st.session_state["favoritas"]`** são a mesma coisa.
3. **É memória de SESSÃO, não banco de dados.** Recarregar a página (F5) começa uma
   sessão nova e apaga tudo; e cada usuário do app publicado tem a sua.
"""
)
