"""
Passo 1 — st.file_uploader: o que ele realmente devolve.

Duas surpresas esperam quem usa o uploader pela primeira vez, e as duas vêm da
mesma regra da Aula 6 — o script roda INTEIRO a cada interação:

  1. `st.file_uploader` devolve `None` enquanto ninguém enviou nada;
  2. depois do envio, ele devolve o MESMO arquivo em TODO rerun. Se você
     acrescenta as linhas dele a uma lista, elas entram de novo a cada clique
     em qualquer outro widget do app.

Rodar:  streamlit run passo01_upload.py
"""

import streamlit as st

st.title("Passo 1 · O arquivo que entra")
st.caption("Envie qualquer CSV. Depois clique no botão de baixo várias vezes e observe.")

enviado = st.file_uploader("Escolha um arquivo CSV", type="csv")

st.subheader("1. O que o widget devolve")
if enviado is None:
    st.info("Devolveu **None** — ninguém enviou nada ainda.")
else:
    st.success("Devolveu um objeto de arquivo (UploadedFile).")
    st.write(
        {
            "name": enviado.name,
            "type": enviado.type,
            "size (bytes)": enviado.size,
        }
    )

    st.subheader("2. Ler o conteúdo")
    st.markdown(
        "`enviado.getvalue()` devolve **bytes** — não texto. E é assim mesmo: o "
        "arquivo veio de fora, ninguém garantiu a codificação dele, e quem decide "
        "como lê-lo é o **seu** código, na borda (passo 2)."
    )
    bruto = enviado.getvalue()
    st.code(repr(bruto[:120]) + ("…" if len(bruto) > 120 else ""), language="python")

st.divider()

st.subheader("3. A armadilha do rerun")
if "quantas_vezes" not in st.session_state:
    st.session_state.quantas_vezes = 0

if st.button("Clique aqui algumas vezes (é só um botão qualquer)"):
    st.session_state.quantas_vezes += 1

st.metric("Reruns causados pelo botão", st.session_state.quantas_vezes)

if enviado is not None:
    st.warning(
        f"Repare: mesmo depois de {st.session_state.quantas_vezes} clique(s) num botão que "
        "nada tem a ver com o upload, o uploader **continua devolvendo o mesmo arquivo**. "
        "Se o seu código fizer `lista.extend(linhas_do_arquivo)` aqui em cima, as linhas "
        "entram de novo a cada rerun — e a tabela cresce sozinha."
    )
    st.markdown(
        "**A correção** (é a mesma da Aula 6, com o comparador): não empilhe cegamente — "
        "verifique se aquilo já está lá.\n\n"
        "```python\n"
        'ja_tenho = {x["url"] for x in st.session_state.enviadas}\n'
        'novas = [linha for linha in linhas if linha["url"] not in ja_tenho]\n'
        "st.session_state.enviadas.extend(novas)\n"
        "```"
    )
