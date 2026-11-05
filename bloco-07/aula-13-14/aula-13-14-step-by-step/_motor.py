"""
O motor provisório dos passos da Aula 13 — o mesmo do demo (src/analisador.py), compacto e sem arquivo.

Sugere a categoria de um texto procurando palavras-chave. Devolve MAIS do que uma API deveria
prometer: as pontuações de todas as categorias e o texto normalizado — detalhes do motor.
"""

import re
import unicodedata

REGRAS = {
    "queimada": ["fumaça", "fogo", "queimada", "queimado", "incêndio", "chamas", "cinzas"],
    "desmatamento": ["desmatamento", "derrubada", "motosserra", "toras", "troncos"],
    "enchente": ["enchente", "alagamento", "alagou", "inundação", "transbordou", "cheia"],
    "seca": ["seca", "estiagem", "nível do rio", "baixou", "sem chuva", "secou"],
    "poluicao": ["poluição", "esgoto", "óleo", "mancha", "peixes mortos", "espuma"],
    "lixo": ["lixo", "entulho", "descarte", "pneus", "resíduos"],
}
MOTOR = "regras-v1 (palavras-chave)"


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def classificar(texto: str) -> dict:
    normalizado = _sem_acento(texto)
    achados = {cat: [t for t in termos if re.search(rf"\b{re.escape(_sem_acento(t))}\b", normalizado)]
               for cat, termos in REGRAS.items()}
    pontuacoes = {cat: len(lista) for cat, lista in achados.items()}
    total = sum(pontuacoes.values())
    melhor = max(pontuacoes, key=pontuacoes.get) if total else None
    return {
        "categoria_sugerida": melhor,
        "confianca": round(pontuacoes[melhor] / total, 2) if total else 0.0,
        "pistas": achados[melhor] if melhor else [],
        "pontuacoes": pontuacoes,             # detalhe do motor
        "texto_normalizado": normalizado,     # detalhe do motor
    }
