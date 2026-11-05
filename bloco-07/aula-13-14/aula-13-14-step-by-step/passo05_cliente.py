"""
Passo 5 — o cliente que lê pelo status (Aula 14 · TP4, item 4: "feedback útil para o usuário final").

    terminal 1:  uvicorn passo02_status_certo:app --reload     (a API do passo 2)
    terminal 2:  python passo05_cliente.py

O `detail` de um erro NÃO tem sempre o mesmo formato:
    422            -> uma LISTA (um item por campo errado)
    404, 409, 503  -> uma FRASE
Um cliente que trata todo erro como 422 — "para cada item do detail, mostre o msg" — quebra no
primeiro 404: percorre a frase LETRA POR LETRA. 🐛 TypeError: string indices must be integers.

O jeito certo: o STATUS decide como ler o corpo. E a falta de resposta (API lenta demais, API
desligada) também vira uma frase — não um traceback.

Este é o desenho de src/cliente_api.py no demo (v12): uma função, FalhaDaAPI, e as páginas mostram
a mensagem no tom certo (409 e 503 são avisos; 422 e 500, erros).
"""

import requests

API = "http://127.0.0.1:8000"


def mensagens_ingenuo(r: requests.Response) -> list[str]:
    """🐛 Trata todo erro como um 422."""
    return [erro["msg"] for erro in r.json()["detail"]]


def mensagens_pelo_status(r: requests.Response) -> list[str]:
    """O status decide como ler o corpo."""
    if r.status_code == 422:
        return [f"{erro['loc'][-1]}: {erro['msg']}" for erro in r.json()["detail"]]
    try:
        return [r.json()["detail"]]                       # 404, 409, 503, 500 (com a rede): uma frase
    except (ValueError, KeyError, TypeError):
        return [f"A API respondeu {r.status_code} sem explicar o motivo."]


def pedir(metodo: str, caminho: str, **opcoes) -> list[str]:
    """Faz o pedido e devolve o que o USUÁRIO deve ler — inclusive quando não há resposta."""
    try:
        r = requests.request(metodo, API + caminho, timeout=opcoes.pop("timeout", 10), **opcoes)
    except requests.exceptions.ReadTimeout:      # conectou; a resposta é que não veio a tempo
        return ["A API demorou demais para responder. Tente de novo em instantes."]
    except requests.exceptions.ConnectionError:  # nem conectou — inclui o ConnectTimeout: no Windows,
        return ["A API não está no ar."]         # recusar uma conexão leva ~2 s (medido)
    if r.ok:
        return [f"OK ({r.status_code})"]
    return mensagens_pelo_status(r)


if __name__ == "__main__":
    relato = {"uf": "PA", "categoria": "queimada", "texto": "Fumaça densa na beira da estrada desde cedo."}
    print("1º envio:        ", pedir("POST", "/relatos", json=relato))
    print("2º envio (igual):", pedir("POST", "/relatos", json=relato))
    print("relato nº 99:    ", pedir("GET", "/relatos/99"))
    print("texto curto:     ", pedir("POST", "/relatos", json={**relato, "texto": "fumaça"}))
    print("motor lento:     ", pedir("GET", "/lento", timeout=2))

    print("\n🐛 o cliente ingênuo, no mesmo 404:")
    r = requests.get(API + "/relatos/99", timeout=10)
    try:
        print(mensagens_ingenuo(r))
    except TypeError as erro:
        print("   TypeError:", erro)
