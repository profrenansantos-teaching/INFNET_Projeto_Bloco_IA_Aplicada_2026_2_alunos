"""
O analisador de relatos — o MOTOR provisório do POST /processar_texto. Painel ODS Brasil, v11 (Aula 13).

Python puro. Lê data/analisador/regras.json (para cada categoria, as palavras que a
denunciam), procura essas palavras no texto e sugere a categoria com mais pistas.

POR QUE UM MOTOR DE REGRAS, SE O TP4 PEDE UM LLM:
  o TP4 pede uma rota que receba um texto e devolva "um JSON estruturado com... o texto
  processado, o tipo de análise realizada e os resultados gerados" (item 3). O FORMATO
  dessa resposta é a Etapa 7; o LLM é a Etapa 8. Construímos primeiro o CONTRATO
  (api/respostas.py: ResultadoAnalise), com um motor simples atrás dele. Na Etapa 8,
  troca-se o motor — carregar_regras() vira carregar o modelo; classificar() vira chamá-lo
  — e a rota continua devolvendo o mesmo formato. Quem já usa a rota não muda nada.

O QUE ESTE MOTOR NÃO SABE FAZER (e é bom que se veja):
  "A água do arroio subiu e alcançou as casas" é uma enchente — e nenhuma palavra da lista
  aparece. O motor devolve categoria_sugerida = None. Um modelo de linguagem entende o
  sentido; uma lista de palavras, não. É o argumento da Etapa 8, medido no nosso dado.

Rodar isoladamente:
    python -m src.analisador
"""

import json
import re
from pathlib import Path

from src.analise_texto import _sem_acento   # a mesma normalização da contagem de palavras (Aula 8)

BASE = Path(__file__).resolve().parent.parent
ARQ_REGRAS = BASE / "data" / "analisador" / "regras.json"
MOTOR = "regras-v1 (palavras-chave)"


def carregar_regras(caminho: Path = ARQ_REGRAS) -> dict[str, list[str]]:
    """{categoria: [palavras]} — sem a chave "_sobre", que é só um comentário no arquivo."""
    regras = json.loads(caminho.read_text(encoding="utf-8"))
    return {categoria: termos for categoria, termos in regras.items() if not categoria.startswith("_")}


def classificar(texto: str, regras: dict[str, list[str]]) -> dict:
    """Sugere a categoria do texto. Devolve MAIS do que a API promete: as pontuações de
    todas as categorias e o texto normalizado são detalhes deste motor — úteis para depurar,
    e que o response model deixa de fora (um LLM não teria os mesmos detalhes)."""
    normalizado = _sem_acento(texto)
    pontuacoes, achados = {}, {}
    for categoria, termos in regras.items():
        # \b: a palavra inteira — "seca" não pode casar com "secador"
        achados[categoria] = [t for t in termos if re.search(rf"\b{re.escape(_sem_acento(t))}\b", normalizado)]
        pontuacoes[categoria] = len(achados[categoria])

    total = sum(pontuacoes.values())
    if total == 0:
        melhor, confianca, pistas = None, 0.0, []
    else:
        melhor = max(pontuacoes, key=pontuacoes.get)
        confianca, pistas = round(pontuacoes[melhor] / total, 2), achados[melhor]
    return {
        "categoria_sugerida": melhor,
        "confianca": confianca,
        "pistas": pistas,
        "pontuacoes": pontuacoes,            # detalhe interno (não sai pela API)
        "texto_normalizado": normalizado,    # detalhe interno (não sai pela API)
    }


if __name__ == "__main__":
    from src.relatos import carregar_exemplos

    regras = carregar_regras()
    print(f"{MOTOR} · {sum(len(t) for t in regras.values())} palavras em {len(regras)} categorias\n")
    for r in carregar_exemplos():
        res = classificar(r["texto"], regras)
        print(f"#{r['id']} declarada: {r['categoria']:<12} sugerida: {str(res['categoria_sugerida']):<12} "
              f"confiança {res['confianca']:.2f}  pistas {res['pistas']}")
