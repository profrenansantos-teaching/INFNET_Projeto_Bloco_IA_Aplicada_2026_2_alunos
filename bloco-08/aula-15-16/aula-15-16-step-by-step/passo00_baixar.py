"""
Passo 0 · Baixar os modelos ANTES da aula (rode em casa, com internet — uma vez só).

Um modelo do Hugging Face são arquivos: os PESOS (as contas, num .safetensors), a configuração e
o tokenizador. O primeiro uso baixa tudo para a pasta de cache do Hugging Face (no Windows,
C:\\Users\\<você>\\.cache\\huggingface\\hub); os seguintes leem de lá, sem internet.

Os passos da aula usam dois modelos (~1,5 GB). O terceiro é OPCIONAL: 3,1 GB para baixar e
~6,5 GB de memória para rodar — só se a sua máquina tem 16 GB de RAM.

Rodar:  python passo00_baixar.py            (os dois da aula)
        python passo00_baixar.py --grande   (+ o Qwen2.5-1.5B, o escolhido do demo)
"""

import sys
import time

from huggingface_hub import snapshot_download

MODELOS = [
    "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",   # 558 MB — passos 1, 3 e 4
    "Qwen/Qwen2.5-0.5B-Instruct",                                    # 988 MB — passo 5
]
if "--grande" in sys.argv:
    MODELOS.append("Qwen/Qwen2.5-1.5B-Instruct")                     # 3,1 GB — passo 5, opcional

# Só o que o Transformers usa: muitos repositórios trazem os pesos duas vezes (.safetensors e o
# antigo .bin) — baixar as duas cópias seria pagar o download em dobro.
SO_O_NECESSARIO = ["*.json", "*.safetensors", "*.txt", "*.model", "tokenizer*", "merges.txt", "vocab.*"]

for modelo in MODELOS:
    relogio = time.perf_counter()
    pasta = snapshot_download(modelo, allow_patterns=SO_O_NECESSARIO)
    print(f"{modelo}: pronto em {time.perf_counter() - relogio:.0f} s\n   {pasta}")
