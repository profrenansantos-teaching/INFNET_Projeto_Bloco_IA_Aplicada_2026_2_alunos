"""
Passo 1 · Um modelo do Hub em três linhas (Aula 15 · B3)

O relato que as regras não reconheceram (a Aula 13 devolveu null) — agora, com um modelo de linguagem.

pipeline() junta as três peças de um modelo numa chamada só:
  o TOKENIZADOR (texto → números) · os PESOS (as contas) · o PÓS-PROCESSAMENTO (números → resposta).

A tarefa daqui é "zero-shot-classification": o modelo nunca viu as NOSSAS categorias. Ele foi
treinado para outra pergunta — "a frase B decorre da frase A?" (inferência textual) — e o
pipeline a faz uma vez por categoria: "A água do arroio subiu…" → "Este relato é sobre enchente."?
É um modelo da família BERT (só encoder): lê o texto inteiro e dá uma nota; não escreve nada.

Observe o TEMPO da análise e guarde o número: o passo 3 descobre de onde ele vem.

Rodar:  python passo01_pipeline.py
"""

import time

from huggingface_hub import constants
from transformers import pipeline

from _dados import ARROIO, ROTULOS

MODELO = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

relogio = time.perf_counter()
classificador = pipeline("zero-shot-classification", model=MODELO)          # 1. carregar
print(f"carregado em {time.perf_counter() - relogio:.1f} s")

relogio = time.perf_counter()
resultado = classificador(ARROIO, candidate_labels=list(ROTULOS.values()),   # 2. perguntar
                          hypothesis_template="Este relato é sobre {}.")
print(f"analisado em {time.perf_counter() - relogio:.1f} s\n\n{ARROIO}")

for rotulo, nota in zip(resultado["labels"], resultado["scores"]):          # 3. ler
    print(f"   {rotulo:<13} {nota:.2f}  {'█' * round(nota * 40)}")

print(f"\nOs arquivos do modelo estão em {constants.HF_HUB_CACHE}")
