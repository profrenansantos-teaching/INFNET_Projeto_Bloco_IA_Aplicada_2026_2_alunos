"""
Passo 4 — o OUTRO lado: um programa que consome a nossa API (Aula 11).

É o código da Aula 2 — `requests.get(...)`, `raise_for_status()`, `.json()` — com
uma diferença só: o endereço agora é o NOSSO. Desde a Aula 2 vocês consomem a API
do IBGE; hoje, alguém pode consumir a de vocês.

COMO RODAR — dois terminais, os dois nesta pasta:
    terminal 1:  uvicorn passo03_consulta_e_ordem:app --reload     (a API)
    terminal 2:  python passo04_cliente.py                          (o cliente)
"""

import requests

API = "http://127.0.0.1:8000"


def pedir(caminho, **params):
    """Faz o GET e mostra o que voltou — inclusive quando é um 422."""
    try:
        r = requests.get(f"{API}{caminho}", params=params, timeout=10)
    except requests.exceptions.ConnectionError:
        raise SystemExit(
            "Não há API escutando em 127.0.0.1:8000. Suba-a noutro terminal:\n"
            "    uvicorn passo03_consulta_e_ordem:app --reload"
        )
    print(f"\nGET {r.url}  ->  {r.status_code}")
    return r


# 1) a consulta: o requests monta o "?desde=2024&limite=3" a partir do dicionário
r = pedir("/desmatamento", desde=2024, limite=3)
r.raise_for_status()
for linha in r.json()["dados"]:
    print(f"   {linha['ano']}  {linha['uf']}  {linha['area_km2']:>7.0f} km²")

# 2) um pedido que a API recusa: 422, e o "detail" diz ONDE e POR QUÊ
r = pedir("/desmatamento", desde=1950)
for erro in r.json()["detail"]:
    print(f"   recusado: {erro['loc']} — {erro['msg']}")

# 3) a ordem das rotas, vista de fora
print("\nA mesma pergunta, nas duas ordens:")
print("   errado:", pedir("/errado/desmatamento/total").json()["detail"][0]["msg"])
print("   certo: ", pedir("/certo/desmatamento/total").json())
