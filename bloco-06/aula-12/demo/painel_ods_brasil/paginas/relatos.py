"""Página Relatos de campo — o painel ENVIA dados à API e mostra o que ela devolve (v10, Aula 12).

A página não grava nada: ela PEDE à API (POST /relatos), e a API — que valida — grava.
Um dono para cada escrita. Quando a API não está no ar (no Community Cloud, por exemplo,
ela não está: roda na sua máquina), a página avisa, desliga o envio e mostra os relatos
de EXEMPLO de data/sample/ — o plano B da Aula 2.

Esta página não é cacheada de propósito: depois de enviar, a lista tem de mostrar o envio.
"""

import requests
import streamlit as st

from src.cliente_api import api_no_ar, endereco_api, enviar_relato, listar_relatos
from src.relatos import carregar_exemplos, filtrar_relatos

UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
       "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
CATEGORIAS = ["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]

st.title("🗣️ Relatos de campo")
st.caption(
    "Equipes de campo e moradores contam o que estão vendo. O painel envia cada relato à API "
    "do projeto, que confere e guarda. **Não escreva nomes, telefones nem e-mails.**"
)

url = endereco_api()
no_ar = api_no_ar(url)

# ---------------------------------------------------------------- enviar
if no_ar:
    with st.form("novo_relato", clear_on_submit=True):
        esq, dir_ = st.columns(2)
        uf = esq.selectbox("UF", UFS, index=UFS.index("PA"))
        categoria = dir_.selectbox("Categoria", CATEGORIAS)
        texto = st.text_area("O que você observou?", max_chars=500,
                             placeholder="Ex.: fumaça densa na beira da estrada desde cedo…")
        if st.form_submit_button("Enviar relato", type="primary"):
            try:
                ok, resposta = enviar_relato(url, uf, categoria, texto)
            except requests.exceptions.RequestException as erro:
                ok, resposta = False, [f"A API não respondeu ({type(erro).__name__}). Tente de novo."]
            if ok:
                st.success(f"Relato nº {resposta['id']} recebido em {resposta['recebido_em']}.")
            else:
                # A API recusou (422) — e disse por quê. Mostramos, traduzido.
                for mensagem in resposta:
                    st.error(mensagem)
else:
    st.info(
        f"A API do painel não está no ar em `{url}` — por isso o envio está desligado. "
        "Ela roda à parte: `uvicorn api.main:app --reload`, na pasta do projeto. "
        "Abaixo, relatos de **exemplo** (fictícios)."
    )

# ---------------------------------------------------------------- consultar
st.markdown("### Relatos recebidos")
f1, f2 = st.columns(2)
filtro_uf = f1.selectbox("Filtrar por UF", ["(todas)"] + UFS, key="relatos_uf")
filtro_cat = f2.selectbox("Filtrar por categoria", ["(todas)"] + CATEGORIAS, key="relatos_cat")
uf_escolhida = None if filtro_uf == "(todas)" else filtro_uf
cat_escolhida = None if filtro_cat == "(todas)" else filtro_cat

if no_ar:
    try:
        relatos = listar_relatos(url, uf_escolhida, cat_escolhida)   # o filtro, a API aplica
        origem = f"API do painel ({url}) — ao vivo"
    except requests.exceptions.RequestException as erro:
        relatos = filtrar_relatos(carregar_exemplos(), uf_escolhida, cat_escolhida)
        origem = f"exemplos fictícios — a API falhou ({type(erro).__name__})"
else:
    relatos = filtrar_relatos(carregar_exemplos(), uf_escolhida, cat_escolhida)
    origem = "exemplos fictícios (data/sample/relatos_exemplo.csv)"

if relatos:
    st.dataframe(
        [{"nº": r["id"], "recebido em": r["recebido_em"], "UF": r["uf"],
          "categoria": r["categoria"], "relato": r["texto"]} for r in relatos],
        hide_index=True,
    )
else:
    st.write("Nenhum relato com esses filtros.")
st.caption(f"Fonte: {origem}. Conteúdo enviado por pessoas, não verificado pelo projeto.")
