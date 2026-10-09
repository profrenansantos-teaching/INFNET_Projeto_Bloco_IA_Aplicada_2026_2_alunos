"""
Passo 5 (COM REDE) — A escada, subida ao vivo no painel real do PRODES.

O enunciado do TP3 manda usar Selenium "se necessário" e "manter a simplicidade
quando possível". Este passo sobe a escada degrau por degrau, na mesma página:

  degrau 1 · requests na URL da página  -> a casca (sem dado)
  degrau 2 · o JSON que a página baixa   -> achado na aba Rede (Network) das
             ferramentas do navegador: rates2025.json + um SEGUNDO arquivo que
             traduz os códigos (18278 -> "Acre"). Rápido — e sem contrato nenhum.
  degrau 3 · Selenium                     -> a tabela que o INPE mostra a humanos

E fecha conferindo o degrau 3 contra o degrau 2: se os dois caminhos dão os mesmos
números, a extração está certa. (Verificado em 23/09/2026: 342 × 342, zero
diferenças.)

Rodar:  python passo05_a_escada.py        (precisa de internet; ~15 s)
"""

import sys
import time
from pathlib import Path

import requests

# Reaproveita o coletor da v8 — o mesmo código que alimenta o painel.
DEMO = Path(__file__).resolve().parents[1] / "demo" / "painel_ods_brasil"
sys.path.insert(0, str(DEMO))
from src.coleta_dinamica import URL, baixar_renderizado, extrair_tabela  # noqa: E402

AGENTE = {"User-Agent": "INFNET-PB-IA-Aplicada/1.0 (material didatico)"}

# ---- degrau 1 · a casca
inicio = time.perf_counter()
casca = requests.get(URL, headers=AGENTE, timeout=30).text
print(f"1 · requests na página: {len(casca)} bytes de HTML, sem dado "
      f"({time.perf_counter() - inicio:.1f} s)")

# ---- degrau 2 · o JSON por trás da página
inicio = time.perf_counter()
BASE_JSON = "https://terrabrasilis.dpi.inpe.br/app/prodes/dashboard/deforestation/files/"
taxas = requests.get(BASE_JSON + "rates2025.json", headers=AGENTE, timeout=30).json()
nomes = requests.get(BASE_JSON + "config/loinames/prodes_legal_amazon.json",
                     headers=AGENTE, timeout=30).json()
codigo_para_nome = {x["gid"]: x["loiname"] for lo in nomes["lois"] for x in lo["loinames"]}
via_json = {}
for periodo in taxas["periods"]:
    ano = periodo["endDate"]["year"]
    for item in periodo["features"]:
        via_json[(codigo_para_nome[item["loiname"]], ano)] = sum(a["area"] for a in item["areas"])
print(f"2 · JSON por trás da página: {len(via_json)} pares (UF, ano) "
      f"({time.perf_counter() - inicio:.1f} s) — o nome do arquivo tem o ANO: rates2025.json")

# ---- degrau 3 · Selenium
html, segundos = baixar_renderizado()
via_selenium = {(linha["estado"], linha["ano"]): linha["area_km2"] for linha in extrair_tabela(html)}
print(f"3 · Selenium: {len(via_selenium)} pares (UF, ano) ({segundos:.1f} s, contando o Chrome)")

# ---- conferência cruzada
diferentes = [chave for chave, valor in via_selenium.items()
              if chave not in via_json or abs(valor - via_json[chave]) > 0.001]
print(f"\nconferência: {len(via_selenium)} × {len(via_json)} pares · {len(diferentes)} diferença(s)")
