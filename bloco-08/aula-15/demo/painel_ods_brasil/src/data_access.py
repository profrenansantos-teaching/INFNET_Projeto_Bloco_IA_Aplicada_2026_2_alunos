"""
Acesso a dados — Painel ODS Brasil (v3, Aula 5).

Coleta via API do IBGE em Python puro (requests + json). Se a API estiver
indisponível, usa o cache local (fail gracefully — princípio da Aula 2).

O QUE MUDOU DA v2 PARA A v3 (preparação para deploy):

1. Verificação de TLS virou CONFIGURAÇÃO, não código.
   Na v2 havia `verify=False` fixo, para atravessar o proxy da rede da escola.
   Isso é um risco de segurança quando o código vai para um repositório PÚBLICO
   e roda num servidor que não tem esse proxy. Agora o padrão é SEGURO
   (verify=True) e a exceção precisa ser declarada de fora:

       PAINEL_ODS_VERIFICAR_SSL=false        (variável de ambiente)
       verificar_ssl = false                 (em .streamlit/secrets.toml)

2. Caminho do cache ancorado em __file__ (e não no diretório de onde o
   comando foi chamado). Localmente os dois funcionam; no servidor, só este.

Rodar isoladamente (sem Streamlit):
    python -m src.data_access
"""

import json
import os
from pathlib import Path

# Âncora no ARQUIVO, não no diretório atual: sobrevive a `streamlit run` de
# qualquer lugar e ao servidor do Streamlit Community Cloud.
BASE = Path(__file__).resolve().parent.parent
CACHE = BASE / "data" / "sample" / "ufs_cache.json"

UA = {"User-Agent": "INFNET-PB-demo/1.0"}
URL_ESTADOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
URL_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324"

_FALSOS = {"0", "false", "nao", "não", "no", "off"}


def _ler_configuracao(nome_env: str, nome_secret: str) -> str | None:
    """Lê uma configuração da variável de ambiente ou dos Secrets do Streamlit.

    A ordem importa: ambiente primeiro (funciona sem Streamlit, no terminal),
    Secrets depois (é como o Community Cloud entrega valores privados).
    """
    valor = os.environ.get(nome_env)
    if valor is not None:
        return valor
    try:  # st.secrets só existe quando rodando dentro do Streamlit
        import streamlit as st

        return st.secrets.get(nome_secret)
    except Exception:
        return None


def verificar_ssl() -> bool:
    """Padrão SEGURO. Só desliga se alguém disser explicitamente para desligar."""
    valor = _ler_configuracao("PAINEL_ODS_VERIFICAR_SSL", "verificar_ssl")
    if valor is None:
        return True
    return str(valor).strip().lower() not in _FALSOS


def _coletar_da_api(timeout: int = 30) -> list[dict]:
    import requests

    verificar = verificar_ssl()
    if not verificar:
        # Só silencia o aviso quando a verificação foi desligada de propósito.
        try:
            import urllib3

            urllib3.disable_warnings()
        except Exception:
            pass

    resp_estados = requests.get(
        URL_ESTADOS,
        params={"orderBy": "nome"},
        headers=UA,
        timeout=timeout,
        verify=verificar,
    )
    resp_estados.raise_for_status()
    por_id = {
        int(e["id"]): {"uf": e["sigla"], "estado": e["nome"], "regiao": e["regiao"]["nome"]}
        for e in resp_estados.json()
    }

    resp_pop = requests.get(
        URL_AGREGADOS,
        params={"localidades": "N3[all]"},
        headers=UA,
        timeout=timeout,
        verify=verificar,
    )
    resp_pop.raise_for_status()
    series = resp_pop.json()[0]["resultados"][0]["series"]

    linhas = []
    for s in series:
        id_uf = int(s["localidade"]["id"])       # o id vem como TEXTO -> int
        valor = int(list(s["serie"].values())[0])
        linha = dict(por_id[id_uf])
        linha["populacao_2025"] = valor
        linhas.append(linha)
    return linhas


def carregar_dados() -> tuple[list[dict], str]:
    """Devolve (linhas, fonte). Nunca levanta exceção: se a API cair, usa o cache."""
    try:
        return _coletar_da_api(), "API do IBGE (ao vivo)"
    except Exception as erro:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        return cache["linhas"], f"cache local — API indisponível ({type(erro).__name__})"


if __name__ == "__main__":
    linhas, fonte = carregar_dados()
    print(f"{len(linhas)} UFs · fonte: {fonte} · verify_ssl={verificar_ssl()}")
    print(linhas[0])
