"""
Passo 3 — O cache, com o custo à vista.

`@st.cache_data` costuma ser ensinado como "põe o decorador e fica rápido". Aqui
o número aparece na tela: quanto a função custou de verdade, e quanto custou
NESTE rerun. Um deles vai a zero.

O truque para medir: a função devolve o próprio tempo que levou. Esse número
também é cacheado — então ele preserva o custo do momento em que a função de
fato rodou, e pode ser comparado com o custo de agora, medido do lado de fora.

Rodar:  streamlit run passo03_cache.py
"""

import time

import streamlit as st

st.title("Passo 3 · O que o cache está fazendo por você")


@st.cache_data(ttl=60, show_spinner=False)
def tarefa_cara(tamanho: int):
    """Finge ser uma coleta de rede: dorme e devolve um resultado + o custo real."""
    inicio = time.perf_counter()
    time.sleep(1.2)                       # aqui estaria requests.get(...)
    resultado = sum(i * i for i in range(tamanho))
    return resultado, time.perf_counter() - inicio


tamanho = st.slider("Tamanho do trabalho", 10_000, 200_000, 50_000, step=10_000)

relogio = time.perf_counter()
resultado, custo_original = tarefa_cara(tamanho)
custo_agora = time.perf_counter() - relogio       # ~0 quando o cache respondeu

esq, meio, dir_ = st.columns(3)
esq.metric("Custo real quando rodou", f"{custo_original * 1000:.0f} ms")
meio.metric("Custo NESTE rerun", f"{custo_agora * 1000:.0f} ms",
            delta=f"{(custo_agora - custo_original) * 1000:.0f} ms", delta_color="inverse")
dir_.metric("Resultado", f"{resultado:.3e}")

if custo_agora < custo_original / 10:
    st.success("O cache respondeu: a função **não rodou**. O corpo dela nem foi executado.")
else:
    st.warning("Cache vazio para este argumento: a função rodou de verdade agora.")

st.divider()
st.subheader("Experimente, nesta ordem")
st.markdown(
    """
1. **Mexa em qualquer coisa sem mudar o slider** → o custo do meio vai a zero.
2. **Mude o slider** → volta a custar. O cache é indexado pelos **ARGUMENTOS**:
   `tamanho=50_000` e `tamanho=60_000` são duas entradas diferentes.
3. **Volte ao valor anterior** → zero de novo. A entrada antiga continua guardada.
4. **Clique em Limpar** (abaixo) → tudo volta a custar.
5. **Espere 60 segundos** → o `ttl=60` vence e a próxima chamada custa de novo.
"""
)

if st.button("🗑 Limpar o cache"):
    st.cache_data.clear()      # esvazia TODOS os @st.cache_data do app
    st.rerun()                 # era st.experimental_rerun() nas versões antigas

st.divider()
st.subheader("cache_data × cache_resource")
st.markdown(
    """
| | `@st.cache_data` | `@st.cache_resource` |
|---|---|---|
| Para que serve | **dados** (listas, dicionários, tabelas, JSON) | **conexões e modelos** |
| O que guarda | uma **cópia** do resultado | o **próprio objeto**, compartilhado |
| Exemplo do curso | a coleta do IBGE, a leitura do CSV | uma conexão de banco, um modelo carregado |
| Cuidado | — | todos os usuários mexem no **mesmo** objeto |

⚠️ **APIs que envelheceram** (você vai ver nos tutoriais antigos):
`@st.cache` → `@st.cache_data` · `@st.experimental_memo` → `@st.cache_data` ·
`@st.experimental_singleton` → `@st.cache_resource` · `st.experimental_rerun()` → `st.rerun()`.
"""
)
st.error(
    "**O cache é COMPARTILHADO entre os visitantes.** Nunca cacheie um resultado que dependa "
    "de quem está olhando — o próximo visitante receberia a resposta do anterior. "
    "Para o que é de um usuário só, o lugar é `st.session_state` (passo 4)."
)
