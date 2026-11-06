"""
Passo 5 · Um LLM de conversa: ele ESCREVE a resposta — e o prompt pesa (Aula 15 · B5)

Agora a outra família: um modelo que GERA texto (só decoder, família GPT), treinado para seguir
instruções. Não há categorias para ele dar nota: ele lê as instruções e o relato e escreve.

🐛 Tropeços reais, medidos no banco de provas:
  · Qwen2.5-0.5B com o prompt "simples" (só a lista de categorias): 4 de 30. Ele respondeu
    "Desmatamento" a quase tudo — e, uma vez, "Chuveiro". Um LLM pequeno chuta com convicção.
  · O MESMO modelo com o prompt de "definicoes" (o que cada categoria quer dizer): 11 de 30.
  · O Qwen2.5-1.5B (3 vezes maior): 23 de 30 com o simples, 27 de 30 com as definições.
O tamanho pesa; o prompt pesa — e só o banco de provas mostra quanto. (Prompt é a Competência 5.)

Rode com PROMPT = "simples"; depois "definicoes". Com 16 GB de RAM, troque o MODELO pelo 1.5B
(baixe antes: python passo00_baixar.py --grande).

Rodar:  python passo05_gerador.py
"""

import time
import unicodedata

import torch
from transformers import pipeline

from _dados import CATEGORIAS, DEFINICOES, banco_de_provas

MODELO = "Qwen/Qwen2.5-0.5B-Instruct"      # com 16 GB de RAM: "Qwen/Qwen2.5-1.5B-Instruct"
PROMPT = "simples"                          # troque para "definicoes"

INSTRUCOES = {
    "simples": ("Você classifica relatos de problemas ambientais enviados por moradores. "
                f"Categorias possíveis: {', '.join(CATEGORIAS)}. Responda apenas com o nome de UMA categoria, sem explicar."),
    "definicoes": ("Você classifica relatos de problemas ambientais enviados por moradores de cidades brasileiras.\n"
                   "Categorias:\n" + "".join(f"- {c}: {d}\n" for c, d in DEFINICOES.items())
                   + "Responda apenas com o nome de UMA categoria, exatamente como escrito acima."),
}


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


gerador = pipeline("text-generation", model=MODELO, dtype=torch.float32)

certos, relogio = 0, time.perf_counter()
for r in banco_de_provas():
    mensagens = [{"role": "system", "content": INSTRUCOES[PROMPT]},
                 {"role": "user", "content": f"Relato: {r['texto']}\nCategoria:"}]
    saida = gerador(mensagens, max_new_tokens=10, do_sample=False)
    resposta = saida[0]["generated_text"][-1]["content"].strip()     # a última mensagem: a do modelo
    # O modelo ESCREVE: "Desmatamento", "enchência", "Chuveiro"… — pega a 1ª categoria que aparecer.
    achadas = [c for c in CATEGORIAS if c in sem_acento(resposta)]
    sugerida = achadas[0] if achadas else None
    certos += sugerida == r["categoria"]
    marca = "✓" if sugerida == r["categoria"] else "✗"
    print(f"{marca} #{r['id']:>2} {r['categoria']:<12} o modelo escreveu: {resposta!r}")

print(f"\n{MODELO} · prompt {PROMPT}: {certos} de 30 certos · {time.perf_counter() - relogio:.0f} s no total")
