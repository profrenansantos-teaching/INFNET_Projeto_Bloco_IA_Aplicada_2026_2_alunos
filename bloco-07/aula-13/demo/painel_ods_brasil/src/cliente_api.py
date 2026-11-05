"""
O painel como CLIENTE da própria API — Painel ODS Brasil, v11 (Aula 13; criado na v10). Python puro.

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

v11: analisar_texto() — o POST /processar_texto. O painel lê os campos que a API DECLAROU
no /docs (ResultadoAnalise): categoria_sugerida, confianca, pistas, motor. Se a API um dia
mudar o motor (Etapa 8: um LLM), este código não muda — o contrato é o mesmo.

E o 201: o POST /relatos passou a responder 201 (Created). enviar_relato() não quebrou porque
confere a FAMÍLIA do status (raise_for_status: tudo abaixo de 400 passa), e não "== 200". O
cliente da prefeitura, que conferia "== 200", passou a dizer "falhou" a relatos gravados.

Rodar isoladamente (com a API no ar noutro terminal):
    python -m src.cliente_api
"""

import requests

from src.data_access import _ler_configuracao   # a mesma leitura de configuração da v3

API_PADRAO = "http://127.0.0.1:8000"

# O que o usuário lê quando a API recusa um envio (422). A API diz ONDE (o campo) e
# QUE TIPO de problema; o painel traduz para quem está do outro lado da tela.
# v11: os LIMITES vêm do próprio 422 (o "ctx" de cada erro) — o relato aceita 500
# caracteres e a análise, 2.000. Escrever "500" aqui seria repetir uma regra da API.
_MENSAGENS = {
    ("texto", "string_too_short"): "O texto precisa ter pelo menos {min_length} caracteres.",
    ("texto", "string_too_long"): "O texto pode ter no máximo {max_length} caracteres.",
    ("texto", "missing"): "Escreva o que foi observado.",
    ("uf", "literal_error"): "Escolha uma UF da lista.",
    ("categoria", "literal_error"): "Escolha uma categoria da lista.",
}


def endereco_api() -> str:
    """Onde a API está. Padrão: na própria máquina. Configurável sem mexer no código:
    PAINEL_ODS_API_URL (ambiente) ou api_url (.streamlit/secrets.toml)."""
    return (_ler_configuracao("PAINEL_ODS_API_URL", "api_url") or API_PADRAO).rstrip("/")


def api_no_ar(url: str, timeout: float = 2.0) -> bool:
    """A API responde? Desligada, a conexão é recusada — no Windows, em ~2 s (medido), que
    é o timeout daqui: a página espera no máximo isso para decidir mostrar o plano B."""
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
    modelo = _MENSAGENS.get((campo, erro["type"]))
    if modelo is None:
        return f"{campo}: {erro['msg']}"
    return modelo.format(**erro.get("ctx", {}))


def enviar_relato(url: str, uf: str, categoria: str, texto: str) -> tuple[bool, dict | list[str]]:
    """POST /relatos. Devolve (True, relato gravado) ou (False, [mensagens para o usuário]).

    Quem valida é a API. O painel não repete as regras — mostra o que a API disse.
    """
    corpo = {"uf": uf, "categoria": categoria, "texto": texto}
    r = requests.post(f"{url}/relatos", json=corpo, timeout=10)     # json=, e não data=
    if r.status_code == 422:
        return False, [traduzir(e) for e in r.json()["detail"]]
    r.raise_for_status()            # 201 passa: só levanta erro de 400 para cima
    return True, r.json()["relato"]


def analisar_texto(url: str, texto: str) -> tuple[bool, dict | list[str]]:
    """POST /processar_texto. Devolve (True, resultado) ou (False, [mensagens para o usuário]).

    `resultado` tem os campos de ResultadoAnalise (ver /docs): tipo_analise, texto,
    categoria_sugerida (ou None), confianca, pistas, motor. O timeout é maior que o do
    envio: um modelo de linguagem (Etapa 8) pode levar segundos para responder.
    """
    r = requests.post(f"{url}/processar_texto", json={"texto": texto}, timeout=30)
    if r.status_code == 422:
        return False, [traduzir(e) for e in r.json()["detail"]]
    r.raise_for_status()
    return True, r.json()


if __name__ == "__main__":
    url = endereco_api()
    if not api_no_ar(url):
        raise SystemExit(f"A API não está no ar em {url}. Suba-a: uvicorn api.main:app --reload")
    print("enviando um relato curto demais:", enviar_relato(url, "PA", "queimada", "fumaça"))
    print("analisando:", analisar_texto(url, "Descarte de entulho e pneus na margem do córrego."))
    print("relatos na API:", len(listar_relatos(url)))
