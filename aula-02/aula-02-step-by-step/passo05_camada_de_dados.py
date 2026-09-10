"""
PASSO 5 — Isolar em src/data_access.py + FALLBACK (§3.3 + §4.4)
Corresponde a: SEPARACAO DE CAMADAS (dados != interface) e FAIL GENTLY.

Regrinha do bom programador (slide §3.4):
  -> Nao coloque a logica de dados MISTURADA com a tela (app.py)
  -> SEMPRE tenha um plano B se a API cair (rede da sala)

Como usar:
  from src.data_access import carregar_dados
  linhas, fonte = carregar_dados()   # (tabela, descricao de onde veio)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "src"
sys.path.insert(0, str(BASE))

if not (SRC / "data_access.py").exists():
    print("[ALERTA] Arquivo src/data_access.py nao existe. Copie o trecho abaixo.")
    print("-" * 60)
    print(r'''
"""
Acesso a dados — Painel ODS Brasil (Aula 2 — Passo 5).
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CACHE = BASE / "data" / "sample" / "ufs_cache.json"
UA = {"User-Agent": "INFNET-PB-demo/1.0"}
URL_ESTADOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
URL_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324"

def _coletar_da_api(timeout=30):
    import requests
    try: import urllib3; urllib3.disable_warnings()
    except: pass
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

def carregar_dados():
    try:
        return _coletar_da_api(), "API do IBGE (ao vivo)"
    except Exception as erro:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        return cache["linhas"], f"cache local — API indisponivel ({type(erro).__name__})"
''')
    sys.exit(0)

print("=" * 60)
print("PASSO 5: Usando o modulo src/data_access.py (camada isolada + fallback)")
print("=" * 60)

from src.data_access import carregar_dados

print("\n[INFO] Chamando carregar_dados()...")
linhas, fonte = carregar_dados()

print(f"\n   [OK] Resultado: {len(linhas)} UFs")
print(f"   [INFO] Fonte de dados: {fonte}")
print(f"   [INFO] Linha 0: {linhas[0]}")

print("""
[INFO] Principios de boa pratica aplicados aqui:

1) SEPARACAO DE CAMADAS  (notes §3.3)
   Toda a logica de dados esta DENTRO de src/data_access.py.
   O Streamlit (app.py, Passos 6/7) so importa a funcao carregar_dados().
   Se amanha mudar a API ou trocar por CSV, mexe SO aqui.

2) FAIL GENTLY / FALLBACK  (notes §4.4)
   O app NAO MORRE se a rede cair. Ele carrega o ultimo dado salvo.
   Isso e diferenca de minutos na aula:
   * sem fallback -> "deu erro vermelho, reinicia a aula"
   * com fallback -> "ok, usando o cache, segue a aula"
""")

print("PASSO 5 OK! Temos nossa camada de dados pronta para o app.")
print("   Proximo passo (6): Streamlit - carregar os dados e mostrar tabela + metricas.")
