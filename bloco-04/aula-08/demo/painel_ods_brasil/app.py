"""
Painel de Indicadores Sustentáveis do Brasil — v6 (Aula 8: arquivos, cache e estado)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v5 PARA A v6 (subcompetências 2.3 e 2.5):
  · UPLOAD (st.file_uploader): o usuário envia o CSV da coleta DELE e as linhas
    entram no painel, ao lado das nossas — com validação na borda;
  · DOWNLOAD (st.download_button): a base mesclada sai em CSV;
  · CACHE (@st.cache_data): o custo da coleta fica VISÍVEL na tela — duas
    medições lado a lado — e há um botão que limpa o cache para você ver a
    diferença ao vivo;
  · ESTADO (st.session_state): o que foi enviado sobrevive aos reruns e à troca
    de filtros. Sem isso, cada mexida apagaria o envio do usuário.

CACHE E ESTADO DE SESSÃO NÃO SÃO A MESMA COISA:
  @st.cache_data    guarda o RESULTADO DE UMA FUNÇÃO, é compartilhado entre os
                    usuários e existe para não repetir trabalho caro.
  st.session_state  guarda o que ESTE usuário fez, é privado da sessão dele e
                    existe para atravessar reruns.

Como rodar:
    pip install -r requirements.txt
    python -m src.coleta_web        # coleta as notícias -> data/processed/
    streamlit run app.py

Como publicar: ver DEPLOY.md (o mesmo repositório da Aula 5 — basta um git push).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from src.data_access import carregar_dados
from src.analise_texto import carregar_texto, estatisticas, frequencia
from src.noticias import (
    carregar_noticias,
    filtrar_noticias,
    ler_csv_enviado,
    mesclar,
    metadados,
    resumo_coleta,
    secoes_disponiveis,
)
from src.transformacoes import (
    CRITERIOS,
    comparar,
    faixa_populacao,
    filtrar,
    ordenar,
    para_csv,
    resumo,
)

VERSAO = "v6 — Aula 8 (arquivos, cache e estado de sessão)"

st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")
st.title("🌱 Painel de Indicadores Sustentáveis do Brasil")


# ---------------------------------------------------------------- dados (cache)
@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados():
    """A função cara: uma chamada de rede ao IBGE. O @st.cache_data guarda o
    RESULTADO — na segunda vez, o corpo desta função não roda.

    Devolvemos junto o tempo que a coleta levou DE VERDADE. Esse número também
    é cacheado, então ele preserva o custo do momento em que a coleta aconteceu
    — e é isso que permite compará-lo com o custo de agora, logo abaixo.
    """
    inicio = time.perf_counter()
    dados, fonte = carregar_dados()
    return dados, fonte, time.perf_counter() - inicio


relogio = time.perf_counter()
with st.spinner("Coletando dados do IBGE…"):
    dados, fonte, custo_original = obter_dados()
custo_agora = time.perf_counter() - relogio      # ~0 quando o cache respondeu

st.caption(f"Fonte: {fonte} · {len(dados)} UFs")

regioes_disponiveis = sorted({linha["regiao"] for linha in dados})
pop_minima, pop_maxima = faixa_populacao(dados)

# ---------------------------------------------------------------- memória de sessão
# Inicializar ANTES de usar: na primeira execução a chave ainda não existe.
if "favoritas" not in st.session_state:
    st.session_state.favoritas = []

# ---------------------------------------------------------------- formulário (1 rerun)
with st.sidebar:
    st.header("Filtros")
    with st.form("filtros"):
        regioes = st.multiselect("Regiões", regioes_disponiveis, default=regioes_disponiveis)
        populacao_minima = st.slider(
            "População mínima",
            min_value=pop_minima,
            max_value=pop_maxima,
            value=pop_minima,
            step=100_000,
        )
        criterio = st.radio("Ordenar por", list(CRITERIOS), index=0)
        mostrar_tabela = st.checkbox("Mostrar a tabela de dados", value=True)
        aplicar = st.form_submit_button("Aplicar filtros")

    if aplicar:
        st.success("Filtros aplicados.")

# ---------------------------------------------------------------- lógica (camada isolada)
filtrados = ordenar(filtrar(dados, regioes, populacao_minima), criterio)

# ---------------------------------------------------------------- controle de fluxo
if not filtrados:
    st.warning(
        "Nenhuma UF atende a esses filtros. Diminua a população mínima "
        "ou selecione mais regiões na barra lateral."
    )
    st.stop()          # interrompe o script aqui: nada abaixo é executado

# ---------------------------------------------------------------- métricas
numeros = resumo(filtrados)
col1, col2, col3 = st.columns(3)
col1.metric("UFs exibidas", numeros["ufs"], delta=numeros["ufs"] - len(dados))
col2.metric("Regiões", numeros["regioes"])
col3.metric("População somada", f"{numeros['populacao']:,}".replace(",", "."))

# ---------------------------------------------------------------- comparador (session_state)
st.markdown("### ⭐ Comparador de UFs")
st.caption(
    "As UFs marcadas continuam no comparador **mesmo quando você muda os filtros** — "
    "é isso que o st.session_state garante, e é o que uma variável comum não faria."
)

esq, dir_ = st.columns([4, 1])
uf_escolhida = esq.selectbox(
    "UF para comparar",
    [linha["uf"] for linha in filtrados],
    label_visibility="collapsed",
)
if dir_.button("Comparar"):
    if uf_escolhida not in st.session_state.favoritas:
        st.session_state.favoritas.append(uf_escolhida)

# comparar() recebe `dados` (base completa), não `filtrados`: uma UF marcada
# permanece na comparação ainda que o filtro atual a exclua.
comparadas = comparar(dados, st.session_state.favoritas)

if comparadas:
    st.dataframe(comparadas, hide_index=True)
    st.bar_chart(comparadas, x="uf", y="populacao_2025", height=240)

    fora_do_filtro = [
        uf for uf in st.session_state.favoritas
        if uf not in {linha["uf"] for linha in filtrados}
    ]
    if fora_do_filtro:
        st.info(
            "No comparador, mas fora do filtro atual: " + " · ".join(fora_do_filtro)
            + " — a comparação sobreviveu à mudança de filtro."
        )
    if st.button("Limpar comparador"):
        st.session_state.favoritas = []
else:
    st.caption("Escolha uma UF e clique em **Comparar** para montar a comparação.")

# ---------------------------------------------------------------- gráfico
st.markdown("### 📊 População por UF")
st.bar_chart(filtrados, x="uf", y="populacao_2025", height=380)

# ---------------------------------------------------------------- tabela + download
if mostrar_tabela:
    st.markdown("### 📋 Dados filtrados")
    st.dataframe(filtrados, hide_index=True)

st.download_button(
    "⬇ Baixar CSV do que está na tela",
    data=para_csv(filtrados),
    file_name="painel_ods_filtrado.csv",
    mime="text/csv",
)

# ---------------------------------------------------------------- cache, à vista
st.divider()
st.markdown("### ⚡ O que o cache está fazendo por você")

esq, meio, dir_ = st.columns(3)
esq.metric("Custo real da coleta", f"{custo_original * 1000:.0f} ms",
           help="Quanto a chamada à API do IBGE levou quando ela de fato aconteceu.")
meio.metric("Custo NESTE rerun", f"{custo_agora * 1000:.0f} ms",
            delta=f"{(custo_agora - custo_original) * 1000:.0f} ms", delta_color="inverse",
            help="Perto de zero significa que o cache respondeu e a rede nem foi tocada.")
if dir_.button("Limpar o cache e recoletar"):
    st.cache_data.clear()          # esvazia TODOS os @st.cache_data do app
    st.rerun()                     # era st.experimental_rerun() nas versões antigas

st.caption(
    "Mexa em qualquer filtro e olhe o número do meio: ele fica em zero. Clique em "
    "**Limpar o cache** e ele volta ao custo real, porque a coleta aconteceu de novo. "
    "O cache dura `ttl=3600` (uma hora) e é COMPARTILHADO entre os visitantes; "
    "`st.session_state`, logo abaixo, é só seu."
)

# ---------------------------------------------------------------- notícias: coleta + envio
st.divider()
st.markdown("### 📰 O que a imprensa está publicando")


@st.cache_data(ttl=600)
def obter_noticias():
    return carregar_noticias(), metadados()


coletadas, meta = obter_noticias()

# ESTADO: o que o usuário enviou precisa sobreviver a cada mexida em filtro.
# Numa variável comum, o envio dele sumiria no rerun seguinte — e ele teria de
# subir o arquivo de novo a cada clique. Esta é a razão de estado (Aula 6).
if "noticias_enviadas" not in st.session_state:
    st.session_state.noticias_enviadas = []

with st.expander("📤 Enviar um CSV de notícias (o resultado da SUA coleta)"):
    st.caption(
        "Formato esperado: as colunas `secao`, `titulo` e `url` (obrigatórias) e, se "
        "houver, `publicado_em`, `palavras` e `fonte`. É exatamente o arquivo que "
        "`python -m src.coleta_web` grava em `data/processed/noticias.csv`."
    )
    enviado = st.file_uploader("Arquivo CSV", type="csv", key="csv_noticias")
    if enviado is not None:
        # getvalue() devolve BYTES: o arquivo do usuário não tem codificação
        # garantida, e quem decide como lê-lo é a nossa função de validação.
        linhas, erro = ler_csv_enviado(enviado.getvalue())
        if erro:
            st.error(f"Não consegui usar este arquivo: {erro}")
        else:
            ja_tenho = {x["url"] for x in st.session_state.noticias_enviadas}
            novas = [linha for linha in linhas if linha["url"] not in ja_tenho]
            st.session_state.noticias_enviadas.extend(novas)
            # 🐛 Defeito real, encontrado testando: o multiselect de seções já
            # existe e já tem uma seleção guardada. A seção nova entra na lista
            # de OPÇÕES e nasce DESMARCADA — o usuário envia o arquivo, recebe
            # "3 acrescentadas" e não vê nada na tela. Não quebra: engana.
            # Por isso marcamos a seção nova explicitamente.
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
            "estão no painel — e continuam aqui quando você mexe nos filtros."
        )
        if st.button("Remover o que eu enviei"):
            st.session_state.noticias_enviadas = []
            st.rerun()

noticias = mesclar(coletadas, st.session_state.noticias_enviadas)

if not noticias:
    st.info(
        "Ainda não há notícias. No terminal, dentro da pasta do projeto, rode "
        "`python -m src.coleta_web` — ou envie um CSV no campo acima."
    )
else:
    numeros = resumo_coleta(noticias)
    st.caption(
        f"Coleta de {meta.get('coletado_em', '—')} · {numeros['noticias']} notícias em "
        f"{numeros['secoes']} seções "
        f"({len(st.session_state.noticias_enviadas)} enviadas por você)."
    )

    secoes_noticias = st.multiselect(
        "Seções",
        secoes_disponiveis(noticias),
        default=secoes_disponiveis(noticias),
        key="secoes_noticias",
    )
    recorte = filtrar_noticias(noticias, secoes_noticias)

    if not recorte:
        st.warning("Nenhuma seção selecionada. Escolha ao menos uma acima.")
    else:
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

# ---------------------------------------------------------------- palavras (o que o TP2 pede)
st.divider()
st.markdown("### 🔤 As palavras que dominam a cobertura")


@st.cache_data
def contar_palavras(texto: str, quantidade: int):
    """Cacheada PELOS ARGUMENTOS: mudar a quantidade recalcula; repetir a mesma
    pergunta não. É a diferença essencial para o session_state — o cache é
    indexado pelo que entra na função, não pelo usuário que perguntou."""
    return frequencia(texto, quantidade), estatisticas(texto)


texto = carregar_texto()
if not texto:
    st.info(
        "Sem texto coletado ainda. Rode `python -m src.coleta_web` para gerar "
        "`data/processed/noticias_texto.txt`."
    )
else:
    quantas = st.slider("Quantas palavras mostrar", 5, 40, 20, step=5)
    top, numeros_texto = contar_palavras(texto, quantas)

    a, b, c = st.columns(3)
    a.metric("Palavras no corpus", f"{numeros_texto['palavras']:,}".replace(",", "."))
    b.metric("Fora as palavras vazias", f"{numeros_texto['palavras_uteis']:,}".replace(",", "."))
    c.metric("Vocabulário distinto", f"{numeros_texto['vocabulario']:,}".replace(",", "."))

    st.bar_chart(top, x="palavra", y="ocorrencias", height=340)
    st.caption(
        "É a nuvem de palavras do enunciado do TP2 — só que com escala, que a nuvem não tem. "
        "As palavras vazias (de, para, pelo…) saem por uma lista mantida à mão em "
        "`src/analise_texto.py`: o que conta como palavra vazia é decisão editorial sua, "
        "não da biblioteca."
    )

st.divider()
st.caption(
    f"{VERSAO} · Fontes: IBGE — população residente estimada (2025), tabela 6579 (API) · "
    "Agência Brasil/EBC — manchetes (WebScraping) · CSV enviado pelo usuário. "
    "Próxima etapa: aplicações multipáginas (Etapa 5)."
)
