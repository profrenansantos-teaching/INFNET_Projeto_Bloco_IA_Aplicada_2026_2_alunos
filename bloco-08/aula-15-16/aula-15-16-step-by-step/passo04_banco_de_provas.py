"""
Passo 4 · O banco de provas: o modelo bate as regras? (Aula 15 · B5)

"Desempenho" no TP4 é "a precisão… e o tipo de tarefa para a qual o modelo foi treinado". A
precisão que interessa é a no NOSSO dado: 30 relatos fictícios, rotulados à mão (banco_de_provas.csv),
5 por categoria — metade com as palavras que as regras conhecem, metade sem elas.

Os dois motores, lado a lado, nos mesmos 30 relatos:
  · as REGRAS da Aula 13 (regras.json): quando acham uma palavra, acertam; quando não acham, null;
  · o mDeBERTa (zero-shot, float32 — a lição do passo 3): sempre responde. Responde certo?

Repare em DOIS números: os acertos e os que ficaram SEM resposta. Errar e calar não são a mesma coisa.

Rodar:  python passo04_banco_de_provas.py
"""

import json
import re
import time
import unicodedata
from pathlib import Path

import torch
from transformers import pipeline

from _dados import ROTULOS, banco_de_provas

MODELO = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------- o motor de regras (Aula 13)
regras = {cat: termos for cat, termos in json.loads((Path(__file__).parent / "regras.json").read_text(
    encoding="utf-8")).items() if not cat.startswith("_")}


def pelas_regras(texto: str) -> str | None:
    normalizado = sem_acento(texto)
    pontos = {cat: sum(bool(re.search(rf"\b{re.escape(sem_acento(t))}\b", normalizado)) for t in termos)
              for cat, termos in regras.items()}
    return max(pontos, key=pontos.get) if any(pontos.values()) else None


# ---------------------------------------------------------------- o modelo
classificador = pipeline("zero-shot-classification", model=MODELO, dtype=torch.float32)
de_volta = {rotulo: cat for cat, rotulo in ROTULOS.items()}


def pelo_modelo(texto: str) -> str:
    r = classificador(texto, candidate_labels=list(ROTULOS.values()), hypothesis_template="Este relato é sobre {}.")
    return de_volta[r["labels"][0]]


# ---------------------------------------------------------------- a prova
banco = banco_de_provas()
for nome, motor in [("regras", pelas_regras), ("mDeBERTa", pelo_modelo)]:
    relogio = time.perf_counter()
    sugeridas = {r["id"]: motor(r["texto"]) for r in banco}
    segundos = time.perf_counter() - relogio
    certos = sum(sugeridas[r["id"]] == r["categoria"] for r in banco)
    calados = sum(s is None for s in sugeridas.values())
    print(f"\n{nome}: {certos} de {len(banco)} certos · {calados} sem resposta · "
          f"{len(banco) - certos - calados} errados · {segundos:.1f} s no total")
    for r in banco:
        if sugeridas[r["id"]] not in (r["categoria"], None):
            print(f"   #{r['id']:>2} {r['categoria']:<12} → {sugeridas[r['id']]:<12} {r['texto'][:60]}…")
