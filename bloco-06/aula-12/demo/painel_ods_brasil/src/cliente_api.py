"""
O painel como CLIENTE da própria API — Painel ODS Brasil, v10 (Aula 12). Python puro.

É o código da Aula 2 (requests.get, raise_for_status, .json(), plano B) — agora para
falar com a NOSSA API. Sem Streamlit: testável sozinho, como todo o src/.

Três decisões, cada uma com um tropeço por trás:
  · `json=` e não `data=`. Com data=, o requests manda um FORMULÁRIO, e o FastAPI, que
    espera JSON, responde 422 "Input should be a valid dictionary or object to extract
    fields from" — uma mensagem que não ajuda ninguém (verificado);
  · `timeout=` sempre. Sem ele, uma API travada trava o painel junto;
  · a API desligada não é exceção para o usuário: o painel avisa e mostra os exemplos
    (o fail gracefully da Aula 2). O Community Cloud, por exemplo, não alcança uma API que
    roda no SEU computador.

Rodar isoladamente (com a API no ar noutro terminal):
    python -m src.cliente_api
"""

import requests

from src.data_access import _ler_configuracao   # a mesma leitura de configuração da v3

API_PADRAO = "http://127.0.0.1:8000"

# O que o usuário lê quando a API recusa um envio (422). A API diz ONDE (o campo) e
# QUE TIPO de problema; o painel traduz para quem está do outro lado da tela.
_MENSAGENS = {
    ("texto", "string_too_short"): "O texto precisa ter pelo menos 15 caracteres.",
    ("texto", "string_too_long"): "O texto pode ter no máximo 500 caracteres.",
    ("texto", "missing"): "Escreva o que foi observado.",
    ("uf", "literal_error"): "Escolha uma UF da lista.",
    ("categoria", "literal_error"): "Escolha uma categoria da lista.",
}


def endereco_api() -> str:
    """Onde a API está. Padrão: na própria máquina. Configurável sem mexer no código:
    PAINEL_ODS_API_URL (ambiente) ou api_url (.streamlit/secrets.toml)."""
    return (_ler_configuracao("PAINEL_ODS_API_URL", "api_url") or API_PADRAO).rstrip("/")


def api_no_ar(url: str, timeout: float = 2.0) -> bool:
    """A API responde? Desligada, a conexão é recusada na hora — não esperamos o timeout."""
    try:
        return requests.get(f"{url}/", timeout=timeout).ok
    except requests.exceptions.RequestException:
        return False


def listar_relatos(url: str, uf: str | None = None, categoria: str | None = None, limite: int = 50) -> list[dict]:
    """GET /relatos. Levanta exceção se a API falhar — quem chama decide o plano B."""
    params = {"limite": limite}
    if uf:
        params["uf"] = uf
    if categoria:
        params["categoria"] = categoria
    r = requests.get(f"{url}/relatos", params=params, timeout=10)
    r.raise_for_status()
    return r.json()["dados"]


def traduzir(erro: dict) -> str:
    """Um item do `detail` de um 422 -> uma frase para o usuário."""
    campo = erro["loc"][-1]
    if erro["type"] == "extra_forbidden":
        return f"O campo '{campo}' não é aceito — a API não guarda dados pessoais."
    return _MENSAGENS.get((campo, erro["type"]), f"{campo}: {erro['msg']}")


def enviar_relato(url: str, uf: str, categoria: str, texto: str) -> tuple[bool, dict | list[str]]:
    """POST /relatos. Devolve (True, relato gravado) ou (False, [mensagens para o usuário]).

    Quem valida é a API. O painel não repete as regras — mostra o que a API disse.
    """
    corpo = {"uf": uf, "categoria": categoria, "texto": texto}
    r = requests.post(f"{url}/relatos", json=corpo, timeout=10)     # json=, e não data=
    if r.status_code == 422:
        return False, [traduzir(e) for e in r.json()["detail"]]
    r.raise_for_status()
    return True, r.json()["relato"]


if __name__ == "__main__":
    url = endereco_api()
    if not api_no_ar(url):
        raise SystemExit(f"A API não está no ar em {url}. Suba-a: uvicorn api.main:app --reload")
    print("enviando um relato curto demais:", enviar_relato(url, "PA", "queimada", "fumaça"))
    print("relatos na API:", len(listar_relatos(url)))
