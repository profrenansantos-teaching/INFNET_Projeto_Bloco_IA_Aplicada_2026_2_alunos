"""Página Escolha do modelo — como o projeto escolheu o seu modelo de linguagem (v13, Aula 15).

É o item 1 do TP4 NA TELA: "Justifique a escolha do modelo, detalhando os critérios de
desempenho, custo computacional local e acessibilidade que levaram à sua decisão."

A página não roda modelo nenhum. Ela LÊ:
  · data/analisador/avaliacao.json — o que a bancada (src/bancada.py) mediu NA NOSSA MÁQUINA:
    acertos no banco de provas, segundos por relato, tempo de carga, memória dos pesos;
  · docs/escolha_do_modelo.md — a justificativa, o mesmo arquivo que vai no TP4.
Um dono para cada valor (Aula 9): o número mora na avaliação; o argumento, no documento; a
página só os mostra. Por isso ela funciona no Community Cloud, onde não há API nem modelo.
"""

import json

import streamlit as st

from src.bancada import ARQ_AVALIACAO, ARQ_JUSTIFICATIVA, ESCOLHA, carregar_banco

FAMILIA = {"—": "— (palavras-chave)", "encoder": "encoder · família BERT",
           "decoder": "decoder · família GPT", "encoder-decoder": "encoder-decoder · família T5/BART"}

st.title("🧪 Escolha do modelo")
st.caption(
    "Qual modelo de linguagem analisa os relatos — e por quê. Os números vêm da **bancada de provas** "
    "(`python -m src.bancada`), rodada na máquina onde a API roda. É o item 1 do TP4."
)

if not ARQ_AVALIACAO.exists():
    st.info("Ainda não há medidas. Rode a bancada: `python -m src.bancada regras` e um modelo, por exemplo "
            "`python -m src.bancada Qwen/Qwen2.5-1.5B-Instruct --tarefa gerar`.")
    st.stop()

medidas = json.loads(ARQ_AVALIACAO.read_text(encoding="utf-8"))
escolhido = next((m for m in medidas if all(m[k] == v for k, v in ESCOLHA.items())), None)
regras = next((m for m in medidas if m["tarefa"] == "regras"), None)

# ---------------------------------------------------------------- a decisão
if escolhido:
    st.success(f"**Escolhido:** `{escolhido['modelo']}` — {escolhido['dtype']}, na CPU, com o prompt de definições.")
    a, b, c, d = st.columns(4)
    a.metric("Acertos no banco de provas", f"{escolhido['acertos']} de {escolhido['total']}",
             delta=f"{escolhido['acertos'] - regras['acertos']:+d} sobre as regras" if regras else None)
    b.metric("Segundos por relato", f"{escolhido['s_por_relato']:.1f}".replace(".", ","),
             help="A mediana dos 30 relatos, depois de um aquecimento.")
    c.metric("Memória dos pesos", f"{escolhido['pesos_mb'] / 1000:.1f} GB".replace(".", ","),
             help="Parâmetros × bytes de cada um. O processo inteiro usa um pouco mais.")
    d.metric("Carga (disco → memória)", f"{escolhido['s_carga']:.0f} s",
             help="Uma vez, quando a API sobe — não a cada pedido (Aula 16).")
else:
    st.warning(f"A escolha registrada ({ESCOLHA['modelo']}) ainda não foi medida nesta máquina.")

# ---------------------------------------------------------------- os candidatos
st.markdown("### Os candidatos, medidos")
linhas = []
for m in sorted(medidas, key=lambda m: (-m["acertos"], m["s_por_relato"])):
    linhas.append({
        "": "✅" if m is escolhido else "",
        "Modelo": m["modelo"],
        "Arquitetura": FAMILIA[m["arquitetura"]],
        "Tipo": m["dtype"],
        "Prompt": m["prompt"],
        "Acertos": f"{m['acertos']}/{m['total']}",
        "Sem resposta": m["sem_resposta"],
        "s por relato": m["s_por_relato"],
        "Carga (s)": m["s_carga"],
        "Pesos (MB)": m["pesos_mb"],
    })
st.dataframe(linhas, hide_index=True)
if medidas:
    st.caption(f"Medido em: {medidas[-1]['maquina']} · última medida em {medidas[-1]['medido_em']}. "
               "Na sua máquina os tempos serão outros — e é por isso que se mede.")

# ---------------------------------------------------------------- onde o escolhido erra
if escolhido and escolhido["erros"]:
    textos = {r["id"]: r["texto"] for r in carregar_banco()}
    st.markdown(f"### Onde o escolhido erra ({len(escolhido['erros'])} de {escolhido['total']})")
    st.dataframe(
        [{"nº": e["id"], "Rótulo": e["esperada"], "O modelo disse": e["sugerida"] or "—", "Relato": textos[e["id"]]}
         for e in escolhido["erros"]],
        hide_index=True,
    )
    st.caption("Saber ONDE o modelo erra faz parte da escolha: é o que a página Analisador avisa a quem o usa.")

# ---------------------------------------------------------------- a justificativa e o banco de provas
with st.expander("A justificativa completa (docs/escolha_do_modelo.md — a mesma do TP4)"):
    if ARQ_JUSTIFICATIVA.exists():
        st.markdown(ARQ_JUSTIFICATIVA.read_text(encoding="utf-8"))
    else:
        st.write("O documento ainda não foi escrito.")

with st.expander("O banco de provas — 30 relatos fictícios, rotulados à mão"):
    st.dataframe(carregar_banco(), hide_index=True)
