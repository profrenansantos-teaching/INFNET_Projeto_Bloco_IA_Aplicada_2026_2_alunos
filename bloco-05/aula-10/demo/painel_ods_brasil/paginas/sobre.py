"""Página Dados e método — de onde vem cada número, e o que o app guarda.

Três blocos que na v6 estavam espalhados, ou nem existiam na tela:
  · as FONTES, com licença e procedência (é o Data Summary Report, visível);
  · o CACHE medido (a demonstração da Aula 8, agora com endereço fixo);
  · a MEMÓRIA DESTA SESSÃO: o que está no st.session_state agora. Marque UFs no
    Comparador, filtre em Indicadores, envie um CSV em Notícias — e volte aqui.
    É a prova, na tela, de que a memória é da sessão e não de uma página.
"""

import time

import streamlit as st

from comum import obter_dados, obter_desmatamento, obter_noticias

st.title("ℹ️ Dados e método")

# ---------------------------------------------------------------- fontes
relogio = time.perf_counter()
dados, fonte, custo_original = obter_dados()
custo_agora = time.perf_counter() - relogio          # ~0 quando o cache respondeu
coletadas, meta = obter_noticias()
prodes, meta_prodes = obter_desmatamento()

st.markdown("### De onde vem cada número")
st.dataframe(
    [
        {
            "Fonte": "IBGE — população estimada 2025 (tabela 6579)",
            "Como chega": "API REST pública (Aula 2)",
            "Licença / termos": "dados públicos oficiais",
            "Neste painel": f"{len(dados)} UFs · {fonte}",
        },
        {
            "Fonte": meta.get("site", "Agência Brasil (EBC)"),
            "Como chega": "WebScraping à parte, grava CSV (Aula 7)",
            "Licença / termos": meta.get("licenca", "Creative Commons Atribuição 3.0 Brasil"),
            "Neste painel": f"{len(coletadas)} notícias · coleta de {meta.get('coletado_em', '—')}",
        },
        {
            "Fonte": meta_prodes.get("site", "INPE/PRODES — TerraBrasilis"),
            "Como chega": "página DINÂMICA, Selenium à parte, grava CSV (Aula 10)",
            "Licença / termos": "CC BY-SA 4.0 (cite e compartilhe igual)",
            "Neste painel": f"{len(prodes)} linhas · coleta de {meta_prodes.get('coletado_em', '—')}",
        },
        {
            "Fonte": "CSV enviado pelo usuário",
            "Como chega": "upload validado na borda (Aula 8)",
            "Licença / termos": "responsabilidade de quem envia",
            "Neste painel": f"{len(st.session_state.noticias_enviadas)} notícias nesta sessão",
        },
    ],
    hide_index=True,
)

# ---------------------------------------------------------------- cache medido (Aula 8)
st.markdown("### ⚡ O que o cache está fazendo por você")
esq, meio, dir_ = st.columns(3)
esq.metric("Custo real da coleta do IBGE", f"{custo_original * 1000:.0f} ms")
meio.metric(
    "Custo NESTE rerun",
    f"{custo_agora * 1000:.0f} ms",
    delta=f"{(custo_agora - custo_original) * 1000:.0f} ms",
    delta_color="inverse",
)
if dir_.button("Limpar o cache e recoletar"):
    st.cache_data.clear()          # esvazia TODOS os @st.cache_data — de todas as páginas
    st.rerun()
st.caption(
    "As funções cacheadas moram em `comum.py` e servem a TODAS as páginas: a coleta do "
    "IBGE acontece uma vez, não uma vez por página."
)

# ---------------------------------------------------------------- memória desta sessão
st.markdown("### 🧠 A memória desta sessão")
st.caption(
    "Tudo o que está em st.session_state agora. Mexa nas outras páginas e volte: "
    "o que você fez lá aparece aqui."
)
memoria = []
for chave in sorted(st.session_state.keys()):
    valor = st.session_state[chave]
    if isinstance(valor, list):
        resumo_valor = f"lista com {len(valor)} item(ns)" + (
            ": " + ", ".join(map(str, valor[:6])) if valor and not isinstance(valor[0], dict) else ""
        )
    else:
        resumo_valor = repr(valor)
    memoria.append({"chave": chave, "valor": resumo_valor})
st.dataframe(memoria, hide_index=True)

# ---------------------------------------------------------------- arquitetura
st.markdown("### Como o app está organizado")
st.code(
    "app.py            ROTEADOR   configura, prepara a memória, define o menu\n"
    "comum.py          COMUM      leituras cacheadas + estado + filtros preservados\n"
    "paginas/*.py      PÁGINAS    uma pergunta do usuário por arquivo\n"
    "src/coleta_web.py COLETA     raspa a Agência Brasil (roda À PARTE)\n"
    "src/coleta_dinamica.py       Selenium no PRODES (À PARTE; requirements-coleta.txt)\n"
    "src/*.py          DADOS e LÓGICA  sem Streamlit — testáveis sozinhos",
    language="text",
)
