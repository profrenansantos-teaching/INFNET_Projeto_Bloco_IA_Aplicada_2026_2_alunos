"""
Passo 1 — Multipáginas do jeito do livro: a pasta pages/.

É o mecanismo que RAGHAVENDRA mostra no cap. 7 [Raghavendra, p171–173] e que
RICHARDS usa no cap. 6: o arquivo principal é a primeira página, e cada .py
dentro da pasta pages/ vira uma página a mais, descoberta sozinha pelo Streamlit.

    home.py                 <- o arquivo que você passa ao `streamlit run`
    pages/
        page2.py             <- como no livro [Raghavendra, p173]
        1_📊_Indicadores.py  <- o prefixo numérico ORDENA; o emoji vira ícone

(O prefixo e o emoji NÃO estão nos livros — Richards atribui emojis e seções a
uma biblioteca de terceiros, st-pages [Richards, p224–225]. É convenção do
próprio Streamlit, verificada rodando no 1.61.)

Rodar (de dentro desta pasta):
    streamlit run home.py

Olhe o menu da barra lateral e repare em três coisas:
  1. a primeira página se chama "home" — o NOME DO ARQUIVO;
  2. "page2" também — para renomear uma página, só renomeando o arquivo;
  3. não há seções nem título por página: o menu é a listagem da pasta.

Funciona (e continua funcionando no Streamlit 1.61). O passo 2 mostra o jeito
atual, st.navigation, em que o menu é CÓDIGO, e não a listagem de uma pasta.
"""

import streamlit as st

st.title("Main page")
st.write("This is Main Page")
st.info(
    "Olhe o menu na barra lateral: 'home', 'Indicadores' (com o ícone tirado do nome "
    "do arquivo) e 'page2'. Os nomes vêm dos ARQUIVOS."
)
