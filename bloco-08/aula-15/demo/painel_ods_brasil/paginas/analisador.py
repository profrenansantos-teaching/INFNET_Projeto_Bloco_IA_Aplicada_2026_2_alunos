"""Página Analisador — o painel pede uma análise de texto à API (v12, Aula 14; criada na v11).

É a interface da rota que o TP4 pede: POST /processar_texto. A página manda o texto e
mostra os campos que a API DECLAROU no contrato (ResultadoAnalise): a categoria sugerida, a
confiança, as pistas e o motor. Ela não sabe COMO a análise é feita — hoje, regras de
palavras-chave; na Etapa 8, um modelo LLM local. Quando o motor mudar, esta página não muda.

v12: quando o analisador está fora (503 — o motor não carregou), a página diz isso, no tom
de AVISO, e lembra que o resto do painel funciona. É o "feedback útil para o usuário final"
do TP4 (item 4): o que aconteceu, e o que ainda dá para fazer.

Sem a API no ar (no Community Cloud, por exemplo), a página avisa e não analisa: o
analisador mora na API, que roda na sua máquina.
"""

import streamlit as st

from src.cliente_api import FalhaDaAPI, analisar_texto, api_no_ar, endereco_api, listar_relatos
from src.relatos import carregar_exemplos

st.title("🔎 Analisador de relatos")
st.caption(
    "Cole um relato (ou escolha um que já chegou) e peça à API uma **sugestão de categoria**. "
    "A análise é feita pela rota `POST /processar_texto` — a rota do TP4."
)

url = endereco_api()
if not api_no_ar(url):
    st.info(
        f"A API do painel não está no ar em `{url}` — e é ela que analisa. "
        "Suba-a à parte: `uvicorn api.main:app --reload`, na pasta do projeto."
    )
    st.stop()

# ---------------------------------------------------------------- o texto
try:
    recebidos = listar_relatos(url, limite=20)
except FalhaDaAPI:
    recebidos = []
opcoes = {"(escrever um texto)": ""}
for r in recebidos or carregar_exemplos():
    opcoes[f"nº {r['id']} · {r['uf']} · {r['categoria']} — {r['texto'][:50]}…"] = r["texto"]

escolha = st.selectbox("Um relato que já chegou", list(opcoes), key="analise_origem")
with st.form("analisar"):
    texto = st.text_area("Texto a analisar", value=opcoes[escolha], height=120, max_chars=2000)
    pedir = st.form_submit_button("Analisar", type="primary")

# ---------------------------------------------------------------- a análise
if pedir:
    try:
        resposta = analisar_texto(url, texto)
    except FalhaDaAPI as falha:
        if falha.status == 503:
            # O analisador está fora — não é culpa de quem pediu, e o resto funciona.
            st.warning(" ".join(falha.mensagens))
            st.page_link("paginas/relatos.py", label="Enquanto isso: os relatos de campo", icon="🗣️")
        else:
            for mensagem in falha.mensagens:
                st.error(mensagem)
        st.stop()

    # Os campos abaixo são os do contrato (ResultadoAnalise, no /docs). Nada além deles.
    a, b = st.columns(2)
    a.metric("Categoria sugerida", resposta["categoria_sugerida"] or "— (sem pista)")
    b.metric("Confiança", f"{resposta['confianca']:.0%}")
    if resposta["pistas"]:
        st.write("**Pistas no texto:** " + " · ".join(resposta["pistas"]))
    else:
        st.warning(
            "O motor não encontrou nenhuma palavra das regras neste texto. Um motor de regras "
            "só reconhece o que está na lista — um modelo de linguagem (Etapa 8) entenderia o sentido."
        )
    st.caption(f"Análise: {resposta['tipo_analise']} · motor: {resposta['motor']}")
