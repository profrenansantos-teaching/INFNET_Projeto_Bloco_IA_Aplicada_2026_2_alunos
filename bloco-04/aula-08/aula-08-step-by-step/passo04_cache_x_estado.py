"""
Passo 4 — Cache e estado de sessão lado a lado.

São as duas "memórias" do Streamlit, e trocá-las uma pela outra dá dois bugs
opostos e igualmente ruins:

  · estado no lugar de cache  ->  cada usuário refaz o trabalho caro;
  · cache no lugar de estado  ->  um usuário vê o resultado do OUTRO.

Este passo mostra as duas funcionando ao mesmo tempo, com contadores visíveis.

Rodar:  streamlit run passo04_cache_x_estado.py
"""

import time

import streamlit as st

st.title("Passo 4 · Duas memórias diferentes")


# ------------------------------------------------------------------ cache
@st.cache_data(show_spinner=False)
def quadrado_caro(n: int) -> tuple[int, str]:
    """Devolve o resultado e a HORA em que foi calculado de verdade."""
    time.sleep(0.8)
    return n * n, time.strftime("%H:%M:%S")


# ------------------------------------------------------------------ estado
if "meus_numeros" not in st.session_state:
    st.session_state.meus_numeros = []

col_a, col_b = st.columns(2)

with col_a:
    st.header("@st.cache_data")
    st.caption("guarda o RESULTADO DE UMA FUNÇÃO, indexado pelos argumentos")
    numero = st.number_input("Número", 1, 50, 7, key="n_cache")
    valor, calculado_em = quadrado_caro(int(numero))
    st.metric(f"{int(numero)}²", valor)
    st.info(f"Calculado de verdade às **{calculado_em}**")
    st.markdown(
        "Troque o número e volte: a hora **não muda** para um número já visto — "
        "a função não rodou de novo.\n\n"
        "E se um colega abrir este mesmo app e pedir o mesmo número, ele recebe "
        "**este** resultado: o cache é **compartilhado**."
    )

with col_b:
    st.header("st.session_state")
    st.caption("guarda o que ESTE usuário fez, privado da sessão dele")
    if st.button("Guardar o número atual"):
        st.session_state.meus_numeros.append(int(numero))
    st.metric("Números guardados", len(st.session_state.meus_numeros))
    st.write(st.session_state.meus_numeros or "— nada guardado ainda —")
    st.markdown(
        "A lista sobrevive aos reruns, mas é **só sua**. Um colega que abrir o "
        "app tem a lista dele, vazia.\n\nF5 começa uma sessão nova e apaga tudo."
    )

st.divider()

st.subheader("A tabela que resolve a dúvida")
st.markdown(
    """
| | `@st.cache_data` | `st.session_state` |
|---|---|---|
| **Guarda** | o resultado de uma função | o que este usuário fez |
| **Indexado por** | os argumentos da chamada | a chave que você escolher |
| **Alcance** | **compartilhado** entre visitantes | **privado** da sessão |
| **Dura** | até o `ttl` vencer ou `.clear()` | a sessão (F5 começa outra) |
| **Some quando** | o servidor reinicia | a aba fecha |
| **Serve para** | não repetir trabalho **caro** | **atravessar** reruns |
"""
)

st.warning(
    "**Os dois erros simétricos.** Guardar a coleta do IBGE em `session_state` faz cada "
    "visitante pagar a chamada de rede outra vez. Cachear o CSV que o usuário enviou faz o "
    "próximo visitante ver o arquivo do anterior — que é, além de errado, um vazamento."
)

st.success(
    "**O teste que decide:** *esse valor depende de QUEM está olhando?* "
    "Se sim, é `session_state`. Se não, e é caro de calcular, é `@st.cache_data`. "
    "Se não é nem uma coisa nem outra, é uma variável comum — e não precisa de memória nenhuma. "
    "(É o mesmo teste da 'razão de estado' da Aula 6.)"
)
