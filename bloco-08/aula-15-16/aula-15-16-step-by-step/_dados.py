"""
Dados dos passos da Aula 15 — o banco de provas e as categorias. (Não é um passo: os passos o importam.)

  · banco_de_provas() — os 30 relatos FICTÍCIOS rotulados à mão (banco_de_provas.csv, a mesma cópia do
    demo): 5 por categoria; metade com as palavras que as regras conhecem, metade sem elas;
  · ARROIO — o relato que as regras da Aula 13 não reconheceram (categoria_sugerida = null);
  · CATEGORIAS, ROTULOS e DEFINICOES — o que o analisador sabe sugerir e o que cada categoria quer dizer.

Os modelos vêm do Hugging Face: rode passo00_baixar.py UMA vez, com internet, antes da aula.
"""

import csv
from pathlib import Path

AQUI = Path(__file__).parent

CATEGORIAS = ["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo"]
# Para o zero-shot, o rótulo é TEXTO que o modelo lê — com acento.
ROTULOS = {"queimada": "queimada", "desmatamento": "desmatamento", "enchente": "enchente",
           "seca": "seca", "poluicao": "poluição", "lixo": "lixo"}
DEFINICOES = {
    "queimada": "fogo, fumaça, incêndio em mata, pasto ou plantação",
    "desmatamento": "corte ou derrubada de árvores, retirada de madeira, floresta virando pasto",
    "enchente": "água subindo, rua ou casa alagada, rio ou córrego transbordando",
    "seca": "falta de chuva, rio, açude ou poço secando, falta de água",
    "poluicao": "esgoto, óleo, produto químico, fumaça de fábrica, água ou ar contaminados",
    "lixo": "lixo, entulho, móveis ou resíduos jogados em lugar errado",
}

ARROIO = "A água do arroio subiu durante a noite e alcançou as casas da rua de baixo."


def banco_de_provas() -> list[dict]:
    """[{id, categoria, texto}, ...] — os 30 relatos rotulados."""
    with open(AQUI / "banco_de_provas.csv", encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))
