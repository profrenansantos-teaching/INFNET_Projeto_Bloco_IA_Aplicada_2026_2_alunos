"""
PASSO 4 — Montar as LINHAS FINAIS (§3.2, loop + tratamento de tipos)
Corresponde a:
  for s in series:
      id_uf = int(s["localidade"]["id"])
      valor = int(list(s["serie"].values())[0])
      linha = dict(por_id[id_uf]); linha["populacao_2025"] = valor

Resultado: lista com 27 dicionarios = TABELA (1 dicionario = 1 linha)
  [
    {"uf": "RO", "estado": "Rondonia", "regiao": "Norte", "populacao_2025": 1751950},
    {"uf": "AC", ...},
    ... (27 no total)
  ]

Rode:  python passo04_montar_tabela.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
from pathlib import Path

DADOS = Path(__file__).resolve().parent / "dados"

por_id = json.loads((DADOS / "passo02_ufs_por_id.json").read_text(encoding="utf-8"))
series = json.loads((DADOS / "passo03b_populacao_series.json").read_text(encoding="utf-8"))

# JSON salva chaves como texto -> converte para int no lookup
por_id_int = {int(k): v for k, v in por_id.items()}

print("=" * 60)
print("PASSO 4: Montar TABELA final (27 linhas, 1 por UF)")
print("=" * 60)
print(f"Ingredientes: {len(por_id_int)} UFs no dicionario  +  {len(series)} series de populacao")

linhas = []
for i, s in enumerate(series):
    id_uf = int(s["localidade"]["id"])
    ano = list(s["serie"].keys())[0]
    valor = int(list(s["serie"].values())[0])

    dados_uf = dict(por_id_int[id_uf])
    dados_uf[f"populacao_{ano}"] = valor
    linhas.append(dados_uf)

    if i < 3:
        print(f"   [{i}] id={id_uf:>2} -> {dados_uf}")

print(f"   ... ({len(linhas) - 3} UFs omitidas)")

print(f"\n--- Verificacoes ---")
print(f"   * Temos {len(linhas)} linhas?  {'SIM' if len(linhas) == 27 else 'FALTA ALGUM UF!'}")
chave_pop = [k for k in linhas[0].keys() if "populacao" in k][0]
soma_total = sum(l[chave_pop] for l in linhas)
print(f"   * Soma da populacao: {f'{soma_total:,}'.replace(',', '.')} habitantes")
todas_regioes = sorted({l["regiao"] for l in linhas})
print(f"   * Regioes encontradas ({len(todas_regioes)}): {todas_regioes}")

ARQ_SAIDA = DADOS / "passo04_linhas_finais.json"
ARQ_SAIDA.write_text(json.dumps(linhas, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n[SALVO] Tabela final salva em: {ARQ_SAIDA.name}")

cache_payload = {"periodo": ano, "linhas": linhas}
(DADOS / "ufs_cache.json").write_text(
    json.dumps(cache_payload, indent=2, ensure_ascii=False), encoding="utf-8"
)

print("\nPASSO 4 OK! Temos 27 linhas (lista de dicts) = nossa TABELA.")
print("   Proximo passo (5): isolar a logica em src/data_access.py com fallback para o cache.")
