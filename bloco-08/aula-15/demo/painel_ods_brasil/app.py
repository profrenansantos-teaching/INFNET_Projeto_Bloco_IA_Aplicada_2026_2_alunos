"""
Painel de Indicadores Sustentáveis do Brasil — v13 (Aula 15: qual modelo de linguagem — e por quê)
Projeto de Bloco: Inteligência Artificial Aplicada — INFNET

O QUE MUDOU DA v12 PARA A v13 (subcompetência 4.3 — escolher o modelo):
  · o projeto escolheu, MEDINDO, o modelo de linguagem que vai substituir as regras do
    analisador: src/ficha_modelo.py lê no Hub o que dá para saber antes de baixar
    (licença, gated, línguas, tamanho); src/bancada.py mede cada candidato no banco de
    provas (data/analisador/banco_de_provas.csv) — acertos, segundos, memória;
  · a página Escolha do modelo mostra as medidas e a justificativa (docs/escolha_do_modelo.md,
    o item 1 do TP4). De novo, UMA linha no menu. Ela só LÊ arquivos: funciona no
    Community Cloud, onde não há API nem modelo;
  · a API não muda nesta versão: o modelo escolhido entra atrás do POST /processar_texto na
    Aula 16 (v14).

O QUE MUDOU DA v11 PARA A v12 (subcompetência 4.2 — exceções HTTP):
  · a API responde 404, 409 e 503 com uma frase em `detail`, e um 500 em JSON, com código;
  · o painel lê a resposta PELO STATUS (src/cliente_api.py): 422 é uma lista a traduzir; os
    outros erros, uma frase para mostrar. Toda falha chega às páginas como FalhaDaAPI;
  · as páginas mostram o que a API disse, no tom certo: um relato repetido (409) é um aviso;
    o analisador fora (503) é um aviso, e o resto do painel continua funcionando.

O QUE MUDOU DA v10 PARA A v11 (subcompetência 4.1 — a resposta também tem contrato):
  · a API declara o formato de TODA resposta (response models); o /docs deixou de mostrar
    "string" e mostra os campos — e o que a função calcula a mais fica no servidor;
  · a rota do TP4, POST /processar_texto, sugere a categoria de um texto. O painel ganhou a
    página Analisador, que a usa — de novo, UMA linha no menu. O motor é provisório
    (regras); o formato da resposta, não: na Etapa 8 um LLM entra atrás da mesma rota;
  · sem a API no ar, a página avisa e não analisa (o analisador mora na API).

O QUE MUDOU DA v9 PARA A v10 (subcompetência 3.4 — a base do TP4):
  · a API passou a RECEBER: POST /relatos, validado por um modelo Pydantic;
  · o painel ganhou a página Relatos de campo — que ENVIA cada relato à API e lista os
    que chegaram. Ela não escreve no arquivo: PEDE à API, que valida e grava (um dono
    para cada escrita). Custou, de novo, UMA linha no menu;
  · sem a API no ar (no Community Cloud ela não está), a página avisa, desliga o envio
    e mostra relatos de exemplo — o plano B da Aula 2.

O QUE MUDOU DA v8 PARA A v9 (subcompetências 3.3 e 3.4):
  · o projeto ganhou uma API — api/main.py, com FastAPI —, para que OUTROS
    PROGRAMAS usem os nossos dados sem raspar o painel (que, para o `requests`,
    é uma casca: "You need to enable JavaScript to run this app.");
  · a API roda À PARTE, noutro terminal (uvicorn api.main:app --reload), com o
    ambiente de requirements-api.txt. ESTE arquivo quase não muda: o app não
    importa o FastAPI, e o Community Cloud continua instalando só o requirements.txt;
  · a API e o painel leem os MESMOS arquivos de data/processed/, com as MESMAS
    funções de src/. Uma leitura, dois clientes.

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
            st.Page("paginas/relatos.py", title="Relatos de campo", icon="🗣️"),
            st.Page("paginas/analisador.py", title="Analisador de relatos", icon="🔎"),
        ],
        "Sobre o projeto": [
            st.Page("paginas/sobre.py", title="Dados e método", icon="ℹ️"),
            st.Page("paginas/modelo.py", title="Escolha do modelo", icon="🧪"),   # v13
        ],
    }
)

# O que o roteador desenha aparece em TODA página — aqui, só um rodapé na barra lateral.
st.sidebar.caption(
    f"{VERSAO}\n\nFontes: IBGE (API) · Agência Brasil/EBC (WebScraping) · INPE/PRODES (Selenium)"
    "\n\nAPI própria (FastAPI), à parte: `uvicorn api.main:app --reload` → /docs · recebe relatos"
    " · analisa textos"
)

pagina.run()
