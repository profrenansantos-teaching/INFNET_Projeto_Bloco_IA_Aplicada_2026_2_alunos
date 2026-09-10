"""
Leitura das notícias raspadas — Painel ODS Brasil, v5 (Aula 7). Python puro.

DIVISÃO DE TRABALHO (a mesma das camadas da Aula 6, agora com uma fonte nova):

    src/coleta_web.py    RASPA a web  ->  grava data/processed/noticias.csv
    src/noticias.py      LÊ o arquivo ->  entrega listas de dicionários  (este)
    app.py               MOSTRA

Este arquivo não sabe o que é HTML e não acessa a rede. Se a Agência Brasil
mudar o layout amanhã, quem quebra é o coleta_web.py — e o painel continua no
ar mostrando a última coleta. Foi para isso que separamos.

Rodar isoladamente:
    python -m src.noticias
"""

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
ARQUIVO_CSV = PROCESSED / "noticias.csv"
ARQUIVO_META = PROCESSED / "coleta_meta.json"


def carregar_noticias(caminho: Path = ARQUIVO_CSV) -> list[dict]:
    """Lê o CSV da coleta com o módulo `csv` da biblioteca padrão (sem pandas).

    Devolve [] se o arquivo não existir — o painel avisa em vez de quebrar.
    A coluna `palavras` vira int aqui, uma vez só: CSV não tem tipos, e deixar
    isso para a interface espalha conversão por todo lado.
    """
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    for linha in linhas:
        linha["palavras"] = int(linha.get("palavras") or 0)
    return linhas


def metadados(caminho: Path = ARQUIVO_META) -> dict:
    """Quando a coleta foi feita, de onde, sob qual licença. Vai para a tela."""
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def secoes_disponiveis(noticias: list[dict]) -> list[str]:
    return sorted({linha["secao"] for linha in noticias})


def filtrar_noticias(noticias: list[dict], secoes: list[str]) -> list[dict]:
    return [linha for linha in noticias if linha["secao"] in secoes]


def resumo_coleta(noticias: list[dict]) -> dict:
    """Os números do cabeçalho da seção de notícias."""
    com_texto = [linha for linha in noticias if linha["palavras"] > 0]
    return {
        "noticias": len(noticias),
        "secoes": len({linha["secao"] for linha in noticias}),
        "com_texto": len(com_texto),
        "palavras": sum(linha["palavras"] for linha in com_texto),
    }


if __name__ == "__main__":
    linhas = carregar_noticias()
    if not linhas:
        raise SystemExit("Nenhuma notícia. Rode antes: python -m src.coleta_web")
    meta = metadados()
    print(f"coleta de {meta.get('coletado_em', '?')} · {meta.get('site', '?')}")
    print(f"licença: {meta.get('licenca', '?')}")
    print("resumo:", resumo_coleta(linhas))
    print("seções:", secoes_disponiveis(linhas))
    for linha in linhas[:5]:
        print(f"  [{linha['secao']:>17}] {linha['titulo'][:62]:<62} {linha['palavras']:>4} palavras")
