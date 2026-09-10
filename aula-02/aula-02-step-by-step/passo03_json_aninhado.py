"""
PASSO 3 — JSON aninhado: navegar até as séries (§3.2 das notas)
Corresponde a: series = resp_pop.json()[0]["resultados"][0]["series"]

A API de Agregados não retorna uma tabela plana. Ela devolve um JSON PROFUNDO.
É como desempilhar caixas russas:
  [0] → primeiro resultado (temos 1 agregado)
  ["resultados"][0] → primeira classificação (sem filtros extras)
  ["series"] → a lista que a gente quer (1 item por UF)

Rode:  python passo03_json_aninhado.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
from pathlib import Path

import requests

try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass

DADOS = Path(__file__).resolve().parent / "dados"

URL_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324"
UA = {"User-Agent": "INFNET-PB-demo/1.0"}

print("=" * 60)
print("PASSO 3: Navegar o JSON ANINHADO da API de Agregados (SIDRA)")
print("=" * 60)

if sys.stdin.isatty():
    modo = input("Usar (1) API ao vivo ou (2) arquivo salvo? [1/2] (padrão: 2): ").strip()
else:
    modo = ""
if modo == "":
    modo = "2"

if modo == "1":
    print("\n[API] Fazendo GET para /agregados/6579 (populacao)...")
    resp = requests.get(
        URL_AGREGADOS,
        params={"localidades": "N3[all]"},
        headers=UA,
        timeout=30,
        verify=False,
    )
    print(f"   Status HTTP: {resp.status_code}")
    resp.raise_for_status()
    pop_bruto = resp.json()
else:
    print("\n[ARQUIVO] Carregando do arquivo salvo: passo03_populacao_resposta_bruta.json")
    pop_bruto = json.loads((DADOS / "passo03_populacao_resposta_bruta.json").read_text(encoding="utf-8"))

# ---------- 1) DESCOBRINDO A ESTRUTURA ----------
print("\n--- MAPEANDO o JSON (o caca-nivel do programador) ---")
print(f"Tipo do nivel RAIZ: {type(pop_bruto).__name__} com {len(pop_bruto)} elemento(s)")

primeiro = pop_bruto[0]
print(f"\nChaves do primeiro elemento ([0]):")
for k in primeiro.keys():
    print(f"   * '{k}' -> tipo: {type(primeiro[k]).__name__}")

print("\nEntrando em [0]['resultados']...")
resultados = primeiro["resultados"]
print(f"   Tipo: {type(resultados).__name__} com {len(resultados)} item")

r0 = resultados[0]
print(f"   [0] tem as chaves: {list(r0.keys())}")
print(f"   -> 'classificacoes': {len(r0['classificacoes'])} itens (vazio = sem filtros)")
print(f"   -> 'series': tem {len(r0['series'])} itens (sao as UFs!)")

# ---------- 2) A LINHA MAGICA ----------
series = pop_bruto[0]["resultados"][0]["series"]

(DADOS / "passo03b_populacao_series.json").write_text(
    json.dumps(series, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ---------- 3) O que tem DENTRO de UMA serie? ----------
print("\n--- DENTRO de 1 serie (series[0]) ---")
s0 = series[0]
print(json.dumps(s0, indent=2, ensure_ascii=False))

print("\n[INFO] Observacoes IMPORTANTES (tropecos reais!):")
print(f"   1) s0['localidade']['id'] = '{s0['localidade']['id']}'  (tipo: {type(s0['localidade']['id']).__name__})")
print(f"      -> [BUG] E TEXTO! Vamos precisar de int(...) para casar com por_id do Passo 2")
print(f"   2) s0['serie'] = {s0['serie']}  (e OUTRO dict!)")
ano = list(s0["serie"].keys())[0]
valor_bruto = list(s0["serie"].values())[0]
print(f"      -> Ano da serie:  {ano}")
print(f"      -> Valor da pop.: '{valor_bruto}'  (tipo: {type(valor_bruto).__name__} - TEXTO tambem!)")
print(f"      -> Outro [BUG]: precisamos de int() no valor tambem")

print("\nPASSO 3 OK! Sabemos navegar o JSON e pegamos as 'series'.")
print("   Proximo passo (4): loopar nas series, tratar os 2 BUGs (ids e valores texto) e montar as linhas finais.")
