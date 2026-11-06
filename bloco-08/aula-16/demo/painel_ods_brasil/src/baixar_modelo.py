"""
Baixar o modelo — UMA vez, com internet, ANTES de subir a API. Painel ODS Brasil, v14 (Aula 16).

O TP4 pede o modelo "baixado e executado localmente… sem depender de serviços externos". Por isso
o download é um passo À PARTE, como a coleta (Aulas 7 e 10): a API só LÊ o que já está no disco
(src/analisador_llm.py carrega com local_files_only=True).

🐛 Tropeço real (Aula 16): na primeira versão, a API carregava o modelo pelo nome, sem
   local_files_only. Com o cache vazio (um colega que acabou de clonar), a SUBIDA da API virou um
   download de 3,1 GB em silêncio: 71 s na nossa rede antes de responder a qualquer rota — numa rede
   mais lenta, minutos. Sem internet, pior: a carga tentava o Hub 5 vezes, esperando cada vez mais, e
   só desistia depois de ~80 s (medido: 82,5 s). Com local_files_only=True, o erro vem em 0,4 s.

Para onde vai: a pasta de cache do Hugging Face (no Windows, C:\\Users\\<você>\\.cache\\huggingface\\hub)
— FORA do projeto. O modelo não vai para o Git: 3 GB não cabem num repositório (o GitHub recusa
arquivos acima de 100 MB) e não são nossos para redistribuir.

Rodar (ambiente de requirements-api.txt):
    python -m src.baixar_modelo
"""

import time

from huggingface_hub import snapshot_download

from src.bancada import ESCOLHA   # o modelo escolhido na Aula 15 (sem importar o torch só para saber o nome)

MODELO = ESCOLHA["modelo"]

# Só o que o Transformers usa — sem cópias antigas de pesos (.bin), quando o repositório as tem.
SO_O_NECESSARIO = ["*.json", "*.safetensors", "*.txt", "tokenizer*", "merges.txt", "vocab.*"]

if __name__ == "__main__":
    print(f"Baixando {MODELO} (~3,1 GB na primeira vez; nas outras, só confere)…")
    relogio = time.perf_counter()
    pasta = snapshot_download(MODELO, allow_patterns=SO_O_NECESSARIO)
    print(f"Pronto em {time.perf_counter() - relogio:.0f} s → {pasta}")
    print("Agora a API carrega o modelo do disco: uvicorn api.main:app --reload")
