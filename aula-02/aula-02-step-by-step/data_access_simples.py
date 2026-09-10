"""
data_access_SIMPLES.py — MÍNIMO necessário (como no PDF §3).

Só tem o que o aluno PRECISA entender para o TP1:
  1) requests.get(url) → .raise_for_status() → .json()
  2) Navegar JSON aninhado ([0]["resultados"][0]["series"])
  3) Tratar tipos (int nos ids e valores)
  4) Try/except → cache local (fallback se rede cair)

Como usar:
  from data_access_simples import carregar_dados
  linhas, fonte = carregar_dados()
"""

import json
from pathlib import Path
import requests

try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass

CACHE = Path(__file__).resolve().parent / "data" / "sample" / "ufs_cache.json"


def carregar_dados():
    try:
        # ---- API 1: UFs (Localidades) ----
        resp_ufs = requests.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
            params={"orderBy": "nome"},
            timeout=20,
            verify=False,
        )
        resp_ufs.raise_for_status()                                     # erro se status != 2xx
        por_id = {int(e["id"]): {"uf": e["sigla"], "estado": e["nome"], "regiao": e["regiao"]["nome"]}
                  for e in resp_ufs.json()}

        # ---- API 2: População (Agregados / SIDRA) ----
        resp_pop = requests.get(
            "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
            params={"localidades": "N3[all]"},
            timeout=20,
            verify=False,
        )
        resp_pop.raise_for_status()
        series = resp_pop.json()[0]["resultados"][0]["series"]           # JSON aninhado

        # ---- Montar tabela (lista de dicionários) ----
        linhas = []
        for s in series:
            id_uf = int(s["localidade"]["id"])                          # texto → int
            valor = int(list(s["serie"].values())[0])                   # texto → int
            linha = dict(por_id[id_uf])                                  # copia UF+estado+regiao
            linha["populacao_2025"] = valor                              # add população
            linhas.append(linha)

        return linhas, "API do IBGE (ao vivo)"

    except Exception:
        # Rede caiu / timeout / requests não instalado
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        return cache["linhas"], "cache local (API indisponível)"


if __name__ == "__main__":
    linhas, fonte = carregar_dados()
    print(f"{len(linhas)} UFs · fonte: {fonte}")
    print(linhas[0])
