"""
Passo 3 · O custo de verdade: memória e segundos, na SUA máquina (Aula 15 · B4)

🐛 Tropeço real: no passo 1, UM relato levou cerca de 5 segundos. O modelo tem 279 milhões de
parâmetros — não devia ser tanto. O que aconteceu:
  o Transformers 5 carrega o modelo no TIPO em que ele foi salvo. Este foi salvo em float16
  (2 bytes por número: metade do download). Só que a CPU faz conta em float16 DEVAGAR — o
  float16 foi feito para placas de vídeo.

Rode como está (DTYPE = "auto") e anote os números. Depois troque para "float32" e rode de novo.

A conta de padaria da memória: parâmetros × bytes de cada um.
  279 milhões × 2 bytes (float16) ≈ 558 MB   ·   279 milhões × 4 bytes (float32) ≈ 1.115 MB
O processo inteiro ocupa um pouco mais (o tokenizador, o Python, as contas do momento).

Rodar:  python passo03_custo.py
"""

import statistics
import time

import torch
from transformers import pipeline

from _dados import ROTULOS, banco_de_provas

MODELO = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
DTYPE = "auto"        # "auto" = o tipo em que o modelo foi salvo · troque para "float32"

relogio = time.perf_counter()
classificador = pipeline("zero-shot-classification", model=MODELO,
                         dtype="auto" if DTYPE == "auto" else getattr(torch, DTYPE))
carga = time.perf_counter() - relogio

pesos = list(classificador.model.parameters())
parametros = sum(p.numel() for p in pesos)
memoria = sum(p.numel() * p.element_size() for p in pesos)
print(f"tipo: {pesos[0].dtype} · {parametros / 1e6:.0f} milhões de parâmetros × {pesos[0].element_size()} bytes"
      f" = {memoria / 1e6:,.0f} MB de pesos · carga {carga:.1f} s".replace(",", "."))

relatos = [r["texto"] for r in banco_de_provas()[:6]]
classificador(relatos[0], candidate_labels=list(ROTULOS.values()))      # aquecimento: não conta
tempos = []
for texto in relatos[1:]:
    relogio = time.perf_counter()
    classificador(texto, candidate_labels=list(ROTULOS.values()), hypothesis_template="Este relato é sobre {}.")
    tempos.append(time.perf_counter() - relogio)
print(f"segundos por relato (mediana de {len(tempos)}): {statistics.median(tempos):.2f}")
