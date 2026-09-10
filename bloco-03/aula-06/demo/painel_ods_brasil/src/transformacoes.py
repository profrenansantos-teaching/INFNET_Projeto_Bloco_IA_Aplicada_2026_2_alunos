"""
Transformações do Painel ODS (v4, Aula 6) — Python puro, sem Streamlit.

Por que este arquivo existe: as funções abaixo são a REGRA DE NEGÓCIO do painel
(filtrar, ordenar, exportar). Elas não sabem que existe uma interface — por isso
podem ser testadas no terminal, sem subir o app, e continuam valendo se um dia
a interface mudar.

É a mesma separação de camadas da Aula 2 (dados em src/data_access.py, interface
em app.py), agora com uma terceira camada no meio: a lógica.

Rodar isoladamente:
    python -m src.transformacoes
"""

import csv
import io

CRITERIOS = {
    "População (maior primeiro)": ("populacao_2025", True),
    "População (menor primeiro)": ("populacao_2025", False),
    "Nome do estado (A-Z)": ("estado", False),
    "Sigla da UF (A-Z)": ("uf", False),
}


def filtrar(linhas: list[dict], regioes: list[str], populacao_minima: int) -> list[dict]:
    """Aplica os filtros do formulário. Devolve uma NOVA lista (não altera a original)."""
    return [
        linha
        for linha in linhas
        if linha["regiao"] in regioes and linha["populacao_2025"] >= populacao_minima
    ]


def ordenar(linhas: list[dict], criterio: str) -> list[dict]:
    """Ordena pelo critério escolhido no rádio. Critério desconhecido não quebra o app."""
    campo, decrescente = CRITERIOS.get(criterio, ("populacao_2025", True))
    return sorted(linhas, key=lambda linha: linha[campo], reverse=decrescente)


def faixa_populacao(linhas: list[dict]) -> tuple[int, int]:
    """Menor e maior população da base — os limites do slider.

    Cuidado real: se mínimo == máximo, st.slider levanta exceção. Devolvemos um
    intervalo de largura mínima 1 para que o widget nunca receba min == max.
    """
    if not linhas:
        return 0, 1
    valores = [linha["populacao_2025"] for linha in linhas]
    menor, maior = min(valores), max(valores)
    return (menor, maior) if menor < maior else (menor, menor + 1)


def para_csv(linhas: list[dict]) -> str:
    """Serializa a lista de dicionários em CSV — com o módulo csv da biblioteca padrão."""
    if not linhas:
        return ""
    buffer = io.StringIO()
    escritor = csv.DictWriter(buffer, fieldnames=list(linhas[0].keys()))
    escritor.writeheader()
    escritor.writerows(linhas)
    return buffer.getvalue()


def resumo(linhas: list[dict]) -> dict:
    """Números do cabeçalho — calculados uma vez, usados em três st.metric."""
    return {
        "ufs": len(linhas),
        "regioes": len({linha["regiao"] for linha in linhas}),
        "populacao": sum(linha["populacao_2025"] for linha in linhas),
    }


def comparar(linhas: list[dict], ufs: list[str]) -> list[dict]:
    """Monta a tabela do comparador para as UFs marcadas.

    Recebe a base COMPLETA (não a filtrada) de propósito: uma UF marcada continua
    no comparador mesmo quando o filtro atual a exclui. É essa persistência que
    JUSTIFICA guardar as marcações em st.session_state — sem ela, a comparação
    se perderia a cada mexida nos filtros.

    Acrescenta a cada linha três números que só fazem sentido na comparação:
    participação na população do país, posição no ranking nacional e a distância
    para a maior das UFs marcadas.
    """
    if not ufs:
        return []
    por_uf = {linha["uf"]: linha for linha in linhas}
    marcadas = [por_uf[uf] for uf in ufs if uf in por_uf]
    if not marcadas:
        return []

    ordem_nacional = ordenar(linhas, "População (maior primeiro)")
    posicao = {linha["uf"]: i + 1 for i, linha in enumerate(ordem_nacional)}
    total_brasil = sum(linha["populacao_2025"] for linha in linhas) or 1
    maior_marcada = max(linha["populacao_2025"] for linha in marcadas)

    return [
        {
            "uf": linha["uf"],
            "estado": linha["estado"],
            "regiao": linha["regiao"],
            "populacao_2025": linha["populacao_2025"],
            "% do Brasil": round(100 * linha["populacao_2025"] / total_brasil, 2),
            "posicao_nacional": posicao[linha["uf"]],
            "dif_para_maior": linha["populacao_2025"] - maior_marcada,
        }
        for linha in ordenar(marcadas, "População (maior primeiro)")
    ]


if __name__ == "__main__":
    from src.data_access import carregar_dados

    linhas, fonte = carregar_dados()
    print(f"fonte: {fonte} · {len(linhas)} UFs")
    print("faixa de população:", faixa_populacao(linhas))

    filtradas = filtrar(linhas, ["Sudeste", "Sul"], 2_000_000)
    print(f"Sudeste+Sul com 2M+: {len(filtradas)} UFs")
    print("resumo:", resumo(filtradas))
    print("top 3:", [l["uf"] for l in ordenar(filtradas, "População (maior primeiro)")[:3]])
    print("csv (2 primeiras linhas):")
    print("\n".join(para_csv(filtradas).splitlines()[:2]))

    print()
    print("comparador (SP, RJ, AC) — note que AC nem está no filtro acima:")
    for linha in comparar(linhas, ["SP", "RJ", "AC"]):
        print(f"  {linha['uf']}  {linha['populacao_2025']:>10,}"
              f"  {linha['% do Brasil']:>5}% do Brasil"
              f"  ·  {linha['posicao_nacional']}º no país"
              f"  ·  {linha['dif_para_maior']:>12,} vs. a maior marcada")
