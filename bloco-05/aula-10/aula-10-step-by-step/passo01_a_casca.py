"""
Passo 1 — A casca: o que o requests (e o BeautifulSoup) enxergam numa página dinâmica.

Parte A (sem rede): lemos o ARQUIVO pagina_dinamica.html — exatamente o que um
servidor entregaria ao requests — e contamos as linhas da tabela com o
BeautifulSoup da Aula 7. Resultado: ZERO. A tabela existe; está vazia. Quem a
preenche é o JavaScript, e nem o requests nem o BeautifulSoup rodam JavaScript.

Parte B (com rede, opcional): o painel do PRODES no TerraBrasilis, via requests.
O HTML inteiro tem ~3 mil bytes, e o único texto visível é "TerraBrasilis".

Rodar:
    python passo01_a_casca.py            # só a parte A (sem rede)
    python passo01_a_casca.py --online   # A + B
"""

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

# ---------------------------------------------------------------- A · sem rede
html = (Path(__file__).resolve().parent / "pagina_dinamica.html").read_text(encoding="utf-8")
sopa = BeautifulSoup(html, "html.parser")
print("A · pagina_dinamica.html, lida como o requests leria:")
print("    <table id='tabela'> existe?   ", sopa.select_one("#tabela") is not None)
print("    linhas no <tbody>:           ", len(sopa.select("#tabela tbody tr")))
print("    <script> na página:          ", len(sopa.find_all("script")))
print("    -> a tabela está VAZIA: os dados só entram quando o JavaScript roda.\n")

# ---------------------------------------------------------------- B · com rede
if "--online" in sys.argv:
    import requests

    URL = "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates"
    resposta = requests.get(
        URL, headers={"User-Agent": "INFNET-PB-IA-Aplicada/1.0 (material didatico)"}, timeout=30
    )
    resposta.raise_for_status()
    sopa = BeautifulSoup(resposta.text, "html.parser")
    for lixo in sopa(["script", "style"]):
        lixo.decompose()
    visivel = re.sub(r"\s+", " ", sopa.get_text(" ")).strip()
    print("B · TerraBrasilis (PRODES) via requests:")
    print(f"    status {resposta.status_code} · {len(resposta.text)} bytes de HTML")
    print(f"    texto visível: {visivel!r} ({len(visivel)} caracteres)")
    print("    tabelas:", len(sopa.find_all("table")))
    print("    -> a casca. No navegador, a mesma URL mostra 9 UFs × 38 anos.")
else:
    print("(Rode com --online para ver a casca do painel real do PRODES.)")
