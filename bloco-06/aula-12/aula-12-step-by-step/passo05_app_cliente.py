"""
Passo 5 — o app Streamlit como CLIENTE da API (Aula 12 · a integração app ↔ API, base do TP4).

COMO RODAR — dois terminais, os dois na pasta aula-12-step-by-step/:
    terminal 1:  uvicorn passo04_routers.main:app --reload     (a API, porta 8000)
    terminal 2:  streamlit run passo05_app_cliente.py           (o app, porta 8501)

Depois, DESLIGUE a API (Ctrl+C no terminal 1) e dê F5 no app: ele avisa, em vez de quebrar.

Três decisões — cada uma evita um defeito que só aparece no pior momento:
  · `json=` (e não `data=`): com data=, a API responde 422 "Input should be a valid
    dictionary or object to extract fields from";
  · `timeout=` sempre, e a API desligada tratada (o plano B da Aula 2). Sem o try, o app
    mostraria um ConnectionError com o traceback inteiro;
  · o app NÃO valida o relato por conta própria e NÃO grava no arquivo: quem valida e grava
    é a API. O app mostra o que ela respondeu — inclusive o 422.
"""

import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.title("Passo 5 — o app fala com a API")

try:
    no_ar = requests.get(f"{API}/", timeout=2).ok
except requests.exceptions.RequestException:
    no_ar = False

if not no_ar:
    st.warning(f"A API não está no ar em {API}. Suba-a noutro terminal: "
               "`uvicorn passo04_routers.main:app --reload`")
    st.stop()

with st.form("relato", clear_on_submit=True):
    uf = st.selectbox("UF", ["PA", "AM", "MT", "AC", "RO", "RR", "AP", "TO", "MA", "SP", "RJ", "RS", "BA", "PE"])
    categoria = st.selectbox("Categoria", ["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"])
    texto = st.text_area("O que você observou?")
    enviado = st.form_submit_button("Enviar")

if enviado:
    r = requests.post(f"{API}/relatos", json={"uf": uf, "categoria": categoria, "texto": texto}, timeout=10)
    if r.status_code == 422:                       # a API recusou — e disse por quê
        for erro in r.json()["detail"]:
            st.error(f"{erro['loc'][-1]}: {erro['msg']}")
    else:
        r.raise_for_status()
        st.success(f"{r.json()['mensagem']} Total na API: {r.json()['total']}.")

st.subheader("O que a API tem")
st.dataframe(requests.get(f"{API}/relatos", timeout=10).json()["dados"], hide_index=True)
