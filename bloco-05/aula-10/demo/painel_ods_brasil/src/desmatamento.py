"""
Desmatamento na Amazônia Legal (PRODES/INPE) — dados e lógica. Painel ODS Brasil, v8 (Aula 10).

Lê o CSV que src/coleta_dinamica.py gravou e responde às perguntas da página
Desmatamento. Python puro, sem Streamlit e SEM Selenium: este app não abre
navegador — ele só lê o arquivo que a coleta deixou em data/processed/.

Rodar isoladamente:
    python -m src.desmatamento
"""

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ARQ_CSV = BASE / "data" / "processed" / "desmatamento_prodes.csv"
ARQ_META = BASE / "data" / "processed" / "desmatamento_meta.json"


def carregar_desmatamento(caminho: Path = ARQ_CSV) -> list[dict]:
    """Lista de dicionários {uf, estado, ano, area_km2, fonte}. Vazia se a coleta não rodou."""
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as f:
        return [
            {**linha, "ano": int(linha["ano"]), "area_km2": float(linha["area_km2"])}
            for linha in csv.DictReader(f)
        ]


def metadados_desmatamento(caminho: Path = ARQ_META) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}


def ufs_disponiveis(linhas: list[dict]) -> list[str]:
    return sorted({linha["uf"] for linha in linhas})


def faixa_de_anos(linhas: list[dict]) -> tuple[int, int]:
    anos = [linha["ano"] for linha in linhas]
    return min(anos), max(anos)


def filtrar(linhas: list[dict], ufs: list[str], ano_inicial: int, ano_final: int) -> list[dict]:
    return [
        linha for linha in linhas
        if linha["uf"] in ufs and ano_inicial <= linha["ano"] <= ano_final
    ]


def total_por_ano(linhas: list[dict]) -> list[dict]:
    """Soma das UFs em cada ano: [{ano, area_km2}], em ordem de ano."""
    soma: dict[int, float] = {}
    for linha in linhas:
        soma[linha["ano"]] = soma.get(linha["ano"], 0.0) + linha["area_km2"]
    return [{"ano": ano, "area_km2": area} for ano, area in sorted(soma.items())]


def ranking_do_ano(linhas: list[dict], ano: int) -> list[dict]:
    """As UFs no ano escolhido, da que mais desmatou para a que menos desmatou."""
    do_ano = [linha for linha in linhas if linha["ano"] == ano]
    return sorted(
        ({"uf": l["uf"], "estado": l["estado"], "area_km2": l["area_km2"]} for l in do_ano),
        key=lambda l: l["area_km2"],
        reverse=True,
    )


def comparar_anos(linhas: list[dict], ano: int) -> dict:
    """Total do ano, total do ano anterior e a variação percentual — para o st.metric."""
    totais = {t["ano"]: t["area_km2"] for t in total_por_ano(linhas)}
    atual, anterior = totais.get(ano), totais.get(ano - 1)
    variacao = (atual - anterior) / anterior * 100 if atual is not None and anterior else None
    return {"ano": ano, "total": atual, "anterior": anterior, "variacao_pct": variacao}


if __name__ == "__main__":
    dados = carregar_desmatamento()
    if not dados:
        print("Sem coleta. Rode: python -m src.coleta_dinamica")
    else:
        primeiro, ultimo = faixa_de_anos(dados)
        c = comparar_anos(dados, ultimo)
        print(f"{len(dados)} linhas · {len(ufs_disponiveis(dados))} UFs · {primeiro}–{ultimo}")
        print(f"Amazônia Legal {ultimo}: {c['total']:,.0f} km² "
              f"({c['variacao_pct']:+.1f}% sobre {ultimo - 1})".replace(",", "."))
        pico = max(total_por_ano(dados), key=lambda t: t["area_km2"])
        print(f"Pico da série: {pico['ano']} — {pico['area_km2']:,.0f} km²".replace(",", "."))
        print("Ranking", ultimo, [(r["uf"], r["area_km2"]) for r in ranking_do_ano(dados, ultimo)])
