"""
O painel como CLIENTE da própria API — Painel ODS Brasil, v12 (Aula 14; criado na v10). Python puro.

É o código da Aula 2 (requests.get, raise_for_status, .json(), plano B) — agora para
falar com a NOSSA API. Sem Streamlit: testável sozinho, como todo o src/.

Três decisões da v10, cada uma com um tropeço por trás:
  · `json=` e não `data=` (com data=, 422 "Input should be a valid dictionary…");
  · `timeout=` sempre (sem ele, uma API travada trava o painel junto);
  · a API desligada não é exceção para o usuário: o painel avisa (o plano B da Aula 2).

v11: analisar_texto() — o POST /processar_texto, lendo só os campos do contrato
(ResultadoAnalise). E o 201 do POST /relatos não quebrou nada aqui porque conferimos a
FAMÍLIA do status (2xx), e não "== 200".

v12 — O STATUS DECIDE COMO LER O CORPO. Toda falha vira UMA exceção, FalhaDaAPI, com a
mensagem já pronta para o usuário:
    422            -> o `detail` é uma LISTA (um item por campo): traduzimos cada item;
    404, 409, 503  -> o `detail` é uma FRASE que a API escreveu para quem pediu: mostramos;
    500            -> a frase da rede de segurança, com o código do erro;
    sem resposta   -> API desligada ou lenta demais: dizemos qual das duas.
🐛 Tropeço real (o painel v11 contra a API v12): um relato enviado duas vezes recebeu 409 —
   e a tela disse "A API não respondeu (HTTPError). Tente de novo." A API tinha respondido, e
   muito bem: "Este relato já foi recebido: nº 3…". O painel jogava fora a resposta e
   inventava outra — e o "tente de novo" levava a outro 409. E com um 500 no GET /relatos, o
   painel v11 mostrava os relatos FICTÍCIOS de exemplo, com a explicação numa legenda.

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


class FalhaDaAPI(Exception):
    """A API não fez o que se pediu. `mensagens` já está pronta para a tela.

    `status` é o código HTTP da resposta — ou None, se a API nem respondeu (desligada,
    ou mais lenta que o timeout). A página usa o status para escolher o TOM: um 409 é um
    aviso (o relato já está gravado); um 422 ou um 500 é um erro.
    """

    def __init__(self, status: int | None, mensagens: list[str]):
        super().__init__(" ".join(mensagens))
        self.status = status
        self.mensagens = mensagens


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


def traduzir(erro: dict) -> str:
    """Um item do `detail` de um 422 -> uma frase para o usuário."""
    campo = erro["loc"][-1]
    if erro["type"] == "extra_forbidden":
        return f"O campo '{campo}' não é aceito — a API não guarda dados pessoais."
    modelo = _MENSAGENS.get((campo, erro["type"]))
    if modelo is None:
        return f"{campo}: {erro['msg']}"
    return modelo.format(**erro.get("ctx", {}))


def _falha(r: requests.Response) -> FalhaDaAPI:
    """Uma resposta de erro -> FalhaDaAPI. O STATUS decide como ler o corpo."""
    if r.status_code == 422:
        return FalhaDaAPI(422, [traduzir(e) for e in r.json()["detail"]])    # uma LISTA
    try:
        frase = r.json()["detail"]                                            # uma FRASE
    except (ValueError, KeyError, TypeError):
        # Corpo que não é JSON (um servidor sem a rede de segurança, um proxy no caminho):
        # não inventamos o motivo — dizemos o que sabemos.
        frase = f"A API respondeu {r.status_code} sem explicar o motivo."
    return FalhaDaAPI(r.status_code, [frase])


def _pedir(metodo: str, url: str, **opcoes) -> requests.Response:
    """Faz o pedido. Devolve a resposta (2xx) — ou levanta FalhaDaAPI, inclusive sem resposta."""
    # 🐛 Tropeço da produção da v12: a primeira versão tratava `Timeout` antes de `ConnectionError`
    #    — e dizia "a API demorou" a uma API DESLIGADA. No Windows, recusar uma conexão em
    #    127.0.0.1 leva ~2 s (medido: 2,02 s; em "localhost", 4,03 s); com timeout de 2 s, a
    #    recusa chega como ConnectTimeout, que é Timeout E ConnectionError ao mesmo tempo.
    #    O que separa os dois casos é ONDE o tempo acabou: antes de conectar (não está no ar)
    #    ou depois, esperando a resposta (ReadTimeout: demorou — um LLM na CPU, na Etapa 8).
    try:
        r = requests.request(metodo, url, **opcoes)
    except requests.exceptions.ReadTimeout:      # conectou, mas a resposta não veio a tempo
        raise FalhaDaAPI(None, [f"A API demorou mais de {opcoes['timeout']} s para responder. "
                                "Tente de novo em instantes."])
    except requests.exceptions.ConnectionError:  # nem conectou (inclui o ConnectTimeout)
        raise FalhaDaAPI(None, ["A API não está no ar. Ela roda à parte: uvicorn api.main:app --reload."])
    if not r.ok:                                 # 4xx ou 5xx; o 201 passa (é 2xx)
        raise _falha(r)
    return r


def listar_relatos(url: str, uf: str | None = None, categoria: str | None = None, limite: int = 50) -> list[dict]:
    """GET /relatos. FalhaDaAPI se não der — quem chama decide o plano B."""
    params = {"limite": limite}
    if uf:
        params["uf"] = uf
    if categoria:
        params["categoria"] = categoria
    return _pedir("GET", f"{url}/relatos", params=params, timeout=10).json()["dados"]


def enviar_relato(url: str, uf: str, categoria: str, texto: str) -> dict:
    """POST /relatos -> o relato gravado (201). FalhaDaAPI com a mensagem, se não der.

    Quem valida é a API. O painel não repete as regras — mostra o que a API disse.
    """
    corpo = {"uf": uf, "categoria": categoria, "texto": texto}
    return _pedir("POST", f"{url}/relatos", json=corpo, timeout=10).json()["relato"]   # json=, e não data=


def analisar_texto(url: str, texto: str) -> dict:
    """POST /processar_texto -> os campos de ResultadoAnalise (ver /docs).

    O timeout é maior que o do envio: o modelo de linguagem (v14) leva segundos na CPU. Medido
    com a API de verdade: ~2,5 s um relato curto; ~8 s um de 2.000 caracteres (o máximo que o
    contrato aceita); e dois pedidos ao mesmo tempo DIVIDEM a CPU (4,6 s cada). 30 s dá folga para
    alguns pedidos juntos, sem deixar a página esperando para sempre.
    503 = o modelo não carregou; a mensagem da API diz que o resto continua funcionando.
    """
    return _pedir("POST", f"{url}/processar_texto", json={"texto": texto}, timeout=30).json()


if __name__ == "__main__":
    url = endereco_api()
    if not api_no_ar(url):
        raise SystemExit(f"A API não está no ar em {url}. Suba-a: uvicorn api.main:app --reload")
    for rotulo, pedido in [
        ("relato curto demais", lambda: enviar_relato(url, "PA", "queimada", "fumaça")),
        ("análise", lambda: analisar_texto(url, "Descarte de entulho e pneus na margem do córrego.")),
    ]:
        try:
            print(rotulo, "->", pedido())
        except FalhaDaAPI as falha:
            print(rotulo, "->", falha.status, falha.mensagens)
