"""Página Notícias — a coleta da Aula 7 + o envio e o download da Aula 8.

O código é o da v6, quase sem mudança: a página herdou a seção inteira.
As duas diferenças são de multipágina:
  · noticias_enviadas é inicializada no ROTEADOR (Dados e método também a lê);
  · o multiselect de seções segue o padrão dos filtros preservados: valor
    inicial no st.session_state, widget só com key.
"""

import streamlit as st

from comum import obter_noticias
from src.noticias import filtrar_noticias, ler_csv_enviado, mesclar, resumo_coleta, secoes_disponiveis
from src.transformacoes import para_csv

st.title("📰 O que a imprensa está publicando")

coletadas, meta = obter_noticias()

with st.expander("📤 Enviar um CSV de notícias (o resultado da SUA coleta)"):
    st.caption(
        "Formato esperado: as colunas `secao`, `titulo` e `url` (obrigatórias) e, se "
        "houver, `publicado_em`, `palavras` e `fonte`. É o arquivo que "
        "`python -m src.coleta_web` grava em `data/processed/noticias.csv`."
    )
    enviado = st.file_uploader("Arquivo CSV", type="csv", key="csv_noticias")
    if enviado is not None:
        linhas, erro = ler_csv_enviado(enviado.getvalue())       # a borda (Aula 8)
        if erro:
            st.error(f"Não consegui usar este arquivo: {erro}")
        else:
            ja_tenho = {x["url"] for x in st.session_state.noticias_enviadas}
            novas = [linha for linha in linhas if linha["url"] not in ja_tenho]
            st.session_state.noticias_enviadas.extend(novas)
            # 🐛 Aula 8: a seção nova nascia DESMARCADA no multiselect. Marcamos.
            for linha in novas:
                selecionadas = st.session_state.get("secoes_noticias")
                if selecionadas is not None and linha["secao"] not in selecionadas:
                    selecionadas.append(linha["secao"])
            st.success(
                f"{enviado.name}: {len(linhas)} linhas lidas, {len(novas)} acrescentadas."
                if novas
                else f"{enviado.name}: nada novo — essas notícias já estavam no painel."
            )
    if st.session_state.noticias_enviadas:
        st.info(
            f"{len(st.session_state.noticias_enviadas)} notícias enviadas por você "
            "estão no painel — e continuam aqui quando você muda de página."
        )
        if st.button("Remover o que eu enviei"):
            secoes_enviadas = {x["secao"] for x in st.session_state.noticias_enviadas}
            st.session_state.noticias_enviadas = []
            # A seleção guardada não pode apontar para uma seção que deixou de existir.
            if "secoes_noticias" in st.session_state:
                st.session_state.secoes_noticias = [
                    s for s in st.session_state.secoes_noticias if s not in secoes_enviadas
                ]
            st.rerun()

noticias = mesclar(coletadas, st.session_state.noticias_enviadas)

if not noticias:
    st.info(
        "Ainda não há notícias. No terminal, dentro da pasta do projeto, rode "
        "`python -m src.coleta_web` — ou envie um CSV no campo acima."
    )
    st.stop()

numeros = resumo_coleta(noticias)
st.caption(
    f"Coleta de {meta.get('coletado_em', '—')} · {numeros['noticias']} notícias em "
    f"{numeros['secoes']} seções ({len(st.session_state.noticias_enviadas)} enviadas por você)."
)

opcoes = secoes_disponiveis(noticias)
st.session_state.setdefault("secoes_noticias", opcoes)
secoes_noticias = st.multiselect("Seções", opcoes, key="secoes_noticias")
recorte = filtrar_noticias(noticias, secoes_noticias)

if not recorte:
    st.warning("Nenhuma seção selecionada. Escolha ao menos uma acima.")
    st.stop()

st.dataframe(
    [
        {
            "Origem": "enviada" if linha.get("origem") == "enviado" else "coletada",
            "Seção": linha["secao"],
            "Manchete": linha["titulo"],
            "Publicado em": linha["publicado_em"] or "—",
            "Link": linha["url"],
        }
        for linha in recorte
    ],
    hide_index=True,
    column_config={"Link": st.column_config.LinkColumn("Link", display_text="abrir")},
)
st.download_button(
    "⬇ Baixar CSV das notícias (coletadas + enviadas)",
    data=para_csv(recorte),
    file_name="noticias_painel.csv",
    mime="text/csv",
)
st.caption(
    f"Fonte da coleta: {meta.get('site', 'Agência Brasil (EBC)')} · "
    f"{meta.get('licenca', 'Creative Commons Atribuição 3.0 Brasil')}."
)
