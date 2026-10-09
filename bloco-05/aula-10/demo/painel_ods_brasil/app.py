"""
Painel de Indicadores Sustentáveis do Brasil — v8 (Aula 10: página dinâmica com Selenium)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v7 PARA A v8 (subcompetência 3.2):
  · uma QUARTA fonte: a taxa anual de desmatamento por UF do PRODES/INPE, tirada
    de uma página que só mostra a tabela depois que o JavaScript roda;
  · a coleta usa Selenium e roda À PARTE (src/coleta_dinamica.py), com o
    ambiente de requirements-coleta.txt. O app NÃO importa o Selenium — o
    Community Cloud nem tem Chrome;
  · no app, isso custou UMA linha no menu (a página Desmatamento) e uma leitura
    cacheada em comum.py. É o que a divisão em páginas da v7 comprou.

O QUE MUDOU DA v6 PARA A v7 (subcompetência 3.1):
  · o app.py de 360 linhas virou um ROTEADOR de ~50. Ele não desenha nenhuma
    análise: configura a página, prepara a memória comum e diz ao Streamlit
    quais páginas existem (st.navigation);
  · cada PERGUNTA do usuário virou uma página em paginas/ — uma pergunta,
    uma página;
  · o que TODAS as páginas usam (leituras cacheadas, inicialização do estado,
    preservação dos filtros) mora em comum.py, e não copiado em cada página.

COMO O STREAMLIT RODA UM APP MULTIPÁGINAS (o modelo de execução da Aula 6,
estendido — e é a ideia que organiza a aula):
  a cada rerun roda ESTE arquivo inteiro, de cima para baixo; quando ele chega
  em `pagina.run()`, roda a página escolhida — e SÓ ela. Trocar de página é um
  rerun como outro qualquer. Por isso:
    · o que está aqui, ANTES do .run(), acontece em TODA página;
    · o que está numa página só acontece quando ela é a escolhida.

O arquivo principal continua sendo app.py: o contrato de quatro itens do
Community Cloud (Aula 5) não muda, e a v7 vai ao ar com um `git push`.

Como rodar:
    pip install -r requirements.txt
    python -m src.coleta_web        # coleta as notícias -> data/processed/ (Aula 7)
    streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from comum import VERSAO, inicializar_estado, preservar_filtros

# Uma vez, no roteador — vale para todas as páginas.
st.set_page_config(page_title="Painel ODS Brasil", page_icon="🌱", layout="wide")

# ---------------------------------------------------------------- memória comum
# As duas linhas abaixo rodam ANTES de qualquer página, em todo rerun.
# 🐛 Tropeço 2 da v7: com a inicialização dentro de uma página, abrir o link
#    direto de OUTRA página quebrava (AttributeError: st.session_state has no
#    attribute "favoritas"). Aqui ela acontece sempre, venha o usuário de onde vier.
inicializar_estado()
# 🐛 Tropeço 1 da v7: o filtro da página Indicadores voltava ao padrão toda vez
#    que o usuário ia a outra página e voltava. Ver preservar_filtros() em comum.py.
preservar_filtros()

# ---------------------------------------------------------------- as páginas
# Cada st.Page é um arquivo; o título e o ícone são o que o MENU mostra.
# O dicionário agrupa as páginas em seções do menu.
pagina = st.navigation(
    {
        "Painel": [
            st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
            st.Page("paginas/indicadores.py", title="Indicadores por UF", icon="📊"),
            st.Page("paginas/comparador.py", title="Comparador de UFs", icon="⭐"),
            st.Page("paginas/desmatamento.py", title="Desmatamento (PRODES)", icon="🌳"),
        ],
        "Fontes e texto": [
            st.Page("paginas/noticias.py", title="Notícias", icon="📰"),
            st.Page("paginas/palavras.py", title="Palavras", icon="🔤"),
        ],
        "Sobre o projeto": [
            st.Page("paginas/sobre.py", title="Dados e método", icon="ℹ️"),
        ],
    }
)

# O que o roteador desenha aparece em TODA página — aqui, só um rodapé na barra lateral.
st.sidebar.caption(
    f"{VERSAO}\n\nFontes: IBGE (API) · Agência Brasil/EBC (WebScraping) · INPE/PRODES (Selenium)"
)

pagina.run()
