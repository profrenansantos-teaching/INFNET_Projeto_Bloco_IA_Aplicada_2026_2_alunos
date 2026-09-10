"""
Passo 6 — Controle de fluxo e feedback: quando NÃO desenhar a tela.

Interatividade não é só oferecer controles: é responder bem quando a escolha do
usuário não produz resultado. Um filtro vazio deve AVISAR, não quebrar.

    "Flow control can be understood as thinking carefully through all the steps of
     your application because Streamlit will try to run the entire app at once if
     we're not explicit about things"                              [Richards, p73]

    "No other script will run when st.stop() occurs."           [Raghavendra, p178]

Rodar:  streamlit run passo06_fluxo_e_feedback.py
"""

import time

import streamlit as st

st.title("Passo 6 · Fluxo e feedback")

DADOS = [
    {"uf": "SP", "regiao": "Sudeste", "populacao": 46_081_801},
    {"uf": "MG", "regiao": "Sudeste", "populacao": 21_393_441},
    {"uf": "RJ", "regiao": "Sudeste", "populacao": 17_219_679},
    {"uf": "BA", "regiao": "Nordeste", "populacao": 14_850_513},
    {"uf": "PR", "regiao": "Sul", "populacao": 11_824_665},
    {"uf": "RS", "regiao": "Sul", "populacao": 11_229_915},
]

# ------------------------------------------------------------------ 1. caixas de alerta
st.header("1. Caixas de alerta")
st.info("st.info — contexto neutro.")
st.success("st.success — deu certo (ex.: filtros aplicados).")
st.warning("st.warning — atenção, mas o app continua (ex.: usando o cache).")
st.error("st.error — algo falhou e o usuário precisa agir.")
st.caption("[Raghavendra, p176]")

st.divider()

# ------------------------------------------------------------------ 2. st.stop
st.header("2. st.stop — interromper com elegância")
minimo = st.slider("População mínima", 0, 50_000_000, 0, 1_000_000)
filtrados = [linha for linha in DADOS if linha["populacao"] >= minimo]

if not filtrados:
    st.warning(
        "Nenhuma UF atende a esse filtro. Diminua a população mínima. "
        "(O script parou aqui — nada abaixo foi executado.)"
    )
    st.stop()

st.write(f"{len(filtrados)} UF(s) no filtro:")
st.dataframe(filtrados, hide_index=True)

st.caption(
    "Arraste o slider até o fim: em vez de um gráfico vazio (ou de uma exceção), "
    "o usuário recebe uma instrução do que fazer."
)

st.divider()

# ------------------------------------------------------------------ 3. espera visível
st.header("3. Feedback de espera")
if st.button("Simular uma coleta demorada"):
    with st.spinner("Coletando dados do IBGE…"):     # [Raghavendra, p126]
        time.sleep(1.5)
    st.success("Coleta concluída.")

if st.button("Simular um processamento em etapas"):
    barra = st.progress(0)                            # [Raghavendra, p125]
    for i in range(100):
        time.sleep(0.005)
        barra.progress(i + 1)
    st.success("Processamento concluído.")

st.divider()

# ------------------------------------------------------------------ 4. levar o dado embora
st.header("4. st.download_button — o usuário leva o resultado")
import csv
import io

buffer = io.StringIO()
escritor = csv.DictWriter(buffer, fieldnames=list(DADOS[0].keys()))
escritor.writeheader()
escritor.writerows(filtrados)

st.download_button(
    "⬇ Baixar CSV do que está na tela",
    data=buffer.getvalue(),
    file_name="ufs_filtradas.csv",
    mime="text/csv",
)
st.caption(
    "O livro passa um arquivo aberto em data= [Raghavendra, p123]; aqui geramos o "
    "CSV em memória com o módulo csv, para exportar exatamente o que está filtrado."
)
