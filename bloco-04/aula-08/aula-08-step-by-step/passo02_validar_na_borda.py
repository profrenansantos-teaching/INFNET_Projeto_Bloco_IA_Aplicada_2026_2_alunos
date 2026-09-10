"""
Passo 2 — Validar na borda: arquivo de fora é entrada NÃO CONFIÁVEL.

O uploader aceita qualquer coisa com extensão .csv. Pode vir vazio, em latin-1,
com as colunas erradas, ou ser uma planilha do Excel que alguém renomeou.

A regra: **validar na borda**. Uma função só, na entrada, que devolve
`(linhas, erro)` — e NÃO levanta exceção. Quem chama decide o que mostrar. Depois
dessa fronteira, a linha enviada é tratada exatamente como a que nós coletamos.

Rodar:  streamlit run passo02_validar_na_borda.py
"""

import csv
import io

import streamlit as st

COLUNAS_OBRIGATORIAS = ("secao", "titulo", "url")


def ler_csv_enviado(conteudo: bytes) -> tuple[list[dict], str]:
    """Devolve (linhas, mensagem_de_erro). Nunca levanta exceção."""
    if not conteudo:
        return [], "O arquivo está vazio."

    texto = None
    for codificacao in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            texto = conteudo.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    if texto is None:
        return [], "Não consegui ler o arquivo como texto. Ele é mesmo um CSV?"

    linhas = list(csv.DictReader(io.StringIO(texto)))
    if not linhas:
        return [], "O CSV não tem nenhuma linha de dados (só o cabeçalho, talvez)."

    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in linhas[0]]
    if faltando:
        return [], (
            "Faltam colunas obrigatórias: " + ", ".join(faltando)
            + ". O arquivo precisa de " + ", ".join(COLUNAS_OBRIGATORIAS) + "."
        )
    return linhas, ""


st.title("Passo 2 · A borda")
st.caption("Teste com os arquivos de exemplo abaixo — ou envie um dos seus.")

exemplos = {
    "✅ válido": b"secao,titulo,url\nMeio ambiente,Manchete de teste,https://exemplo.org/1\n",
    "⛔ vazio": b"",
    "⛔ só cabeçalho": b"secao,titulo,url\n",
    "⛔ falta a coluna url": b"secao,titulo\nMeio ambiente,Manchete sem link\n",
    "✅ latin-1 (acento fora do utf-8)": "secao,titulo,url\nSa\xfade,Not\xedcia com acento,https://exemplo.org/2\n".encode("latin-1"),
}

escolha = st.radio("Arquivo de exemplo", list(exemplos), index=0)
linhas, erro = ler_csv_enviado(exemplos[escolha])

if erro:
    st.error(f"Não consegui usar este arquivo: {erro}")
    st.caption("Repare: o app **avisou** e continuou de pé. Não houve exceção, não houve tela vermelha.")
else:
    st.success(f"{len(linhas)} linha(s) aceita(s).")
    st.dataframe(linhas, hide_index=True)

st.divider()
st.subheader("E com um arquivo seu")
enviado = st.file_uploader("CSV", type="csv")
if enviado is not None:
    linhas, erro = ler_csv_enviado(enviado.getvalue())
    if erro:
        st.error(erro)
    else:
        st.success(f"{len(linhas)} linha(s) aceita(s) de {enviado.name}.")
        st.dataframe(linhas, hide_index=True)

st.divider()
st.markdown(
    """
### As três decisões deste passo

1. **A função devolve o erro; não o levanta.** Erro de arquivo do usuário não é excepcional —
   é rotina. `try/except` espalhado pela interface fica ilegível.
2. **A mensagem diz o que fazer.** "Faltam colunas obrigatórias: url" é acionável;
   "arquivo inválido" não é. É o mesmo princípio do `st.stop` da Aula 6.
3. **Tentar mais de uma codificação.** `utf-8-sig` primeiro (é o que o Excel gera, com BOM),
   depois `utf-8`, depois `latin-1`. A ordem importa: `latin-1` **nunca falha**, então ela
   tem de ser a última — se viesse antes, aceitaria lixo silenciosamente.
"""
)
