"""
Acesso a dados — Painel ODS Brasil (Aula 2 — Passo 5).

Tenta a API do IBGE primeiro. Se falhar (rede da sala, timeout, etc.),
carrega do arquivo salvo em data/sample/ufs_cache.json.
A interface (app.py) só precisa chamar: carregar_dados() → (linhas, fonte).
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CACHE = BASE / "data" / "sample" / "ufs_cache.json"
UA = {"User-Agent": "INFNET-PB-demo/1.0"}
URL_ESTADOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
URL_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324"


def _coletar_da_api(timeout: int = 30) -> list[dict]:
    """Faz as 2 chamadas à API e devolve a tabela de 27 linhas."""
    import requests
    try:
        import urllib3
        urllib3.disable_warnings()
    except Exception:
        pass

    r1 = requests.get(URL_ESTADOS, params={"orderBy": "nome"},
                      headers=UA, timeout=timeout, verify=False)
    r1.raise_for_status()
    por_id = {int(e["id"]): {"uf": e["sigla"], "estado": e["nome"], "regiao": e["regiao"]["nome"]}
              for e in r1.json()}

    r2 = requests.get(URL_AGREGADOS, params={"localidades": "N3[all]"},
                      headers=UA, timeout=timeout, verify=False)
    r2.raise_for_status()
    series = r2.json()[0]["resultados"][0]["series"]
    ano = list(series[0]["serie"].keys())[0]
    linhas = []
    for s in series:
        id_uf = int(s["localidade"]["id"])
        valor = int(list(s["serie"].values())[0])
        linha = dict(por_id[id_uf])
        linha[f"populacao_{ano}"] = valor
        linhas.append(linha)
    return linhas


def carregar_dados() -> tuple[list[dict], str]:
    """API primeiro; se falhar → fallback para o cache. Devolve (linhas, descricao_fonte)."""
    try:
        return _coletar_da_api(), "API do IBGE (ao vivo)"
    except Exception as erro:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        return cache["linhas"], f"cache local — API indisponível ({type(erro).__name__})"


if __name__ == "__main__":
    linhas, fonte = carregar_dados()
    print(f"{len(linhas)} UFs · fonte: {fonte}")
    print(linhas[0])
