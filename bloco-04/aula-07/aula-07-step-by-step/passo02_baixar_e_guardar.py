"""
Passo 2 — Baixar UMA vez e guardar o HTML.

O erro mais comum de quem começa é usar o servidor dos outros como se fosse
disco próprio: rodar o script trinta vezes ajustando o seletor, e a cada
tentativa bater na página de novo.

O certo é: baixa uma vez, GRAVA o arquivo, e daí em diante trabalha no arquivo.
Isso é mais rápido, é mais educado, e ainda te dá uma prova do que a página
dizia no dia da coleta — que é o que você vai querer quando alguém perguntar
"de onde veio esse número?".

Rodar:  python passo02_baixar_e_guardar.py
"""

import os
from pathlib import Path

import requests

URL = "https://agenciabrasil.ebc.com.br/meio-ambiente"
DESTINO = Path(__file__).parent / "snapshot_meio_ambiente.html"
AGENTE = "INFNET-PB-IA-Aplicada/1.0 (material didatico; contato: professor)"

VERIFICAR = os.environ.get("PAINEL_ODS_VERIFICAR_SSL", "true").lower() not in {"false", "0", "nao"}
if not VERIFICAR:
    import urllib3

    urllib3.disable_warnings()

resposta = requests.get(URL, headers={"User-Agent": AGENTE}, timeout=30, verify=VERIFICAR)

# Leia o status ANTES de parsear. Um 403 devolve uma página de erro perfeitamente
# válida em HTML — e o BeautifulSoup vai processá-la sem reclamar, devolvendo
# zero resultados. Você passaria uma hora culpando o seletor.
print(f"status HTTP: {resposta.status_code}")
print(f"tipo de conteúdo: {resposta.headers.get('Content-Type')}")
print(f"tamanho: {len(resposta.text):,} caracteres".replace(",", "."))
resposta.raise_for_status()

resposta.encoding = resposta.apparent_encoding or "utf-8"
DESTINO.write_text(resposta.text, encoding="utf-8")
print(f"\nsnapshot gravado em: {DESTINO.name}")
print("A partir daqui, o passo 3 lê ESTE arquivo — sem tocar no servidor de novo.")

print("\nOs 400 primeiros caracteres do que chegou:")
print("-" * 70)
print(resposta.text[:400])
print("-" * 70)
print("\nRepare: isto é TEXTO. 'HTML' é só um acordo sobre como marcar esse texto.")
print("O trabalho do passo 3 é transformar esse acordo em estrutura navegável.")
