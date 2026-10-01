"""
O que TODAS as páginas usam — Painel ODS Brasil (v7, Aula 9).

Três coisas moram aqui, e pelo mesmo motivo: numa página, as outras não as
alcançariam — ou teriam de copiá-las.

1. As LEITURAS CARAS, cacheadas uma vez só (@st.cache_data).
   Uma função cacheada definida AQUI e importada por várias páginas tem UM
   cache. Copiada para cada página, ela funciona enquanto as cópias forem
   idênticas; na primeira edição de uma delas passam a existir dois caches, e
   a coleta roda duas vezes — sem erro nenhum. (Verificado com AppTest.)

2. A INICIALIZAÇÃO DA MEMÓRIA (st.session_state).
   O roteador (app.py) chama inicializar_estado() ANTES de qualquer página;
   por isso nenhuma página quebra quando alguém abre o link direto dela.

3. A PRESERVAÇÃO DOS FILTROS entre páginas.
   O Streamlit APAGA o valor de um widget com key no rerun em que esse widget
   não é desenhado. Trocar de página é um rerun sem os filtros da página
   anterior — e eles voltavam ao padrão. preservar_filtros() desliga essa limpeza.

Este arquivo usa Streamlit (cache e estado) mas não desenha nada na tela: é
a camada que as páginas compartilham. A lógica pura continua em src/.
"""

import time

import streamlit as st

from src.analise_texto import estatisticas, frequencia
from src.data_access import carregar_dados
from src.noticias import carregar_noticias, metadados

VERSAO = "v7 — Aula 9 (aplicação multipáginas)"

# Chaves de widgets que devem SOBREVIVER à troca de página.
# Só entra aqui o que o usuário escolheu e esperaria reencontrar ao voltar.
CHAVES_PRESERVADAS = (
    "regioes",            # página Indicadores
    "populacao_minima",   # página Indicadores
    "criterio",           # página Indicadores
    "mostrar_tabela",     # página Indicadores
    "secoes_noticias",    # página Notícias
    "qtd_palavras",       # página Palavras
)


# ---------------------------------------------------------------- 1. leituras caras
@st.cache_data(ttl=3600, show_spinner="Coletando dados do IBGE…")
def obter_dados():
    """A chamada ao IBGE. Devolve também quanto ela custou DE VERDADE —
    esse número é cacheado junto, e a página "Dados e método" o compara com o
    custo de agora (Aula 8)."""
    inicio = time.perf_counter()
    dados, fonte = carregar_dados()
    return dados, fonte, time.perf_counter() - inicio


@st.cache_data(ttl=600)
def obter_noticias():
    """O CSV que a coleta (Aula 7) gravou em data/processed/, e os metadados dela."""
    return carregar_noticias(), metadados()


@st.cache_data
def contar_palavras(texto: str, quantidade: int):
    """Cacheada PELOS ARGUMENTOS: mudar a quantidade recalcula; repetir não."""
    return frequencia(texto, quantidade), estatisticas(texto)


# ---------------------------------------------------------------- 2. memória
def inicializar_estado() -> None:
    """Toda chave de memória que MAIS DE UMA página usa nasce aqui.

    setdefault() só grava se a chave ainda não existe — então chamar isto em
    todo rerun é seguro: não apaga o que o usuário já fez.
    """
    st.session_state.setdefault("favoritas", [])           # Comparador (e Início lê)
    st.session_state.setdefault("noticias_enviadas", [])   # Notícias (e Dados lê)


# ---------------------------------------------------------------- 3. filtros entre páginas
def preservar_filtros() -> None:
    """Impede que os filtros voltem ao padrão quando o usuário troca de página.

    Por que acontece: no rerun em que um widget com key NÃO é desenhado, o
    Streamlit apaga a chave dele do st.session_state. Ao sair de Indicadores,
    o multiselect "regioes" não é desenhado — e o valor escolhido some.

    Por que isto resolve: regravar a chave pelo próprio st.session_state faz o
    Streamlit tratá-la como valor NOSSO, e não mais como estado do widget; ela
    deixa de ser limpa. Tem de rodar em TODA página — por isso é chamada pelo
    roteador, antes de pagina.run().
    """
    for chave in CHAVES_PRESERVADAS:
        if chave in st.session_state:
            st.session_state[chave] = st.session_state[chave]
