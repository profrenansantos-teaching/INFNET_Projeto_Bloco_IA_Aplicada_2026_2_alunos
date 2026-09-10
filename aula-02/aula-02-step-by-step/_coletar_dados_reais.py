"""
Coleta respostas REAIS da API do IBGE e salva em arquivos JSON
para usar nos passos do aula-02-step-by-step.
"""

import json
import requests
from pathlib import Path

try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DADOS = BASE / "dados"
DADOS.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "INFNET-PB-demo/1.0"}
VERIFY = False
TIMEOUT = 30

# --- Passo 1: resposta bruta da API de Localidades (UFs) ---
print("1/6 Coletando UFs (resposta bruta)...")
r_ufs = requests.get(
    "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
    params={"orderBy": "nome"},
    headers=UA,
    timeout=TIMEOUT,
    verify=VERIFY,
)
r_ufs.raise_for_status()
ufs_raw = r_ufs.json()
(DADOS / "passo01_ufs_resposta_bruta.json").write_text(
    json.dumps(ufs_raw, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"   -> {len(ufs_raw)} UFs salvas em passo01_ufs_resposta_bruta.json")

# --- Passo 2: dicionario por_id (uf, estado, regiao) ---
print("2/6 Montando dicionario por_id...")
por_id = {int(e["id"]): {"uf": e["sigla"], "estado": e["nome"], "regiao": e["regiao"]["nome"]}
          for e in ufs_raw}
(DADOS / "passo02_ufs_por_id.json").write_text(
    json.dumps(por_id, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"   -> {len(por_id)} chaves salvas em passo02_ufs_por_id.json")

# --- Passo 3: resposta bruta da API de Agregados (populacao) ---
print("3/6 Coletando populacao (resposta bruta)...")
r_pop = requests.get(
    "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    params={"localidades": "N3[all]"},
    headers=UA,
    timeout=TIMEOUT,
    verify=VERIFY,
)
r_pop.raise_for_status()
pop_raw = r_pop.json()
(DADOS / "passo03_populacao_resposta_bruta.json").write_text(
    json.dumps(pop_raw, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"   -> {len(pop_raw[0]['resultados'][0]['series'])} series salvas")

# --- Passo 3b: apenas as series (extraindo parte profunda do JSON) ---
print("4/6 Extraindo apenas as series...")
series_raw = pop_raw[0]["resultados"][0]["series"]
(DADOS / "passo03b_populacao_series.json").write_text(
    json.dumps(series_raw, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"   -> {len(series_raw)} series salvas em passo03b_populacao_series.json")

# Mostra UM exemplo de serie (3 primeiros itens)
print("   Exemplo de serie:", json.dumps(series_raw[:2], indent=2, ensure_ascii=False)[:400], "...")

# --- Passo 4: juntando UFs com populacao (linhas finais) ---
print("5/6 Montando linhas finais (juntando UFs + populacao)...")
ano = list(series_raw[0]["serie"].keys())[0]
chave_pop = f"populacao_{ano}"
linhas = []
for s in series_raw:
    id_uf = int(s["localidade"]["id"])
    valor = int(list(s["serie"].values())[0])
    linha = dict(por_id[id_uf])
    linha[chave_pop] = valor
    linhas.append(linha)
(DADOS / "passo04_linhas_finais.json").write_text(
    json.dumps(linhas, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"   -> {len(linhas)} linhas finais salvas. Ano: {ano}")

# --- Passo 5: cache final (igual ao ufs_cache.json do demo) ---
print("6/6 Salvando cache final com periodo...")
cache_payload = {"periodo": ano, "linhas": linhas}
(DADOS / "ufs_cache.json").write_text(
    json.dumps(cache_payload, indent=2, ensure_ascii=False), encoding="utf-8"
)
# Tambem salva na pasta data/sample igual o demo
(BASE / "data" / "sample" / "ufs_cache.json").write_text(
    json.dumps(cache_payload, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"   -> Cache salvo com periodo {ano}. Arquivos: dados/ufs_cache.json e data/sample/ufs_cache.json")

print("\nDONE. Todos os arquivos de dados reais salvos!")
print(f"\nResumo:")
for f in sorted(DADOS.glob("*.json")):
    print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
