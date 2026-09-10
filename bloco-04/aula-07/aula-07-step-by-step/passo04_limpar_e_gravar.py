"""
Passo 4 — Limpar o que veio e gravar o CSV.

Extrair é a parte fácil. O que sai de uma página vem com rótulo colado
("Publicado em   02/09/2026 - 07:02"), espaço duro invisível (\\xa0), marcador
de referência ("46 179 008[3]") e vírgula no lugar do ponto.

Limpeza é metade do trabalho — e é onde mora a diferença entre um CSV que
alimenta um painel e um CSV que ninguém consegue usar.

Não acessa a rede. Rodar:  python passo04_limpar_e_gravar.py
"""

import csv
import re
from pathlib import Path

DESTINO = Path(__file__).parent / "noticias_exemplo.csv"

# O que o passo 3 devolveria: texto cru, do jeito que estava na página.
# ATENÇÃO: o título do meio contém um \xa0 DE VERDADE (entre "chuva" e "e") —
# é impossível vê-lo aqui, e é exatamente esse o problema. Rode o arquivo e
# compare o `repr` de antes e depois.
BRUTO = [
    {"secao": "Meio ambiente",
     "titulo": "  Depois da COP17, Brasil é cobrado a efetivar metas  ",
     "data": "Publicado em   28/08/2026 - 14:31",
     "url": "/meio-ambiente/noticia/2026-08/depois-da-cop17",
     "texto": "O Brasil assumiu o compromisso de restaurar 12 milhões de hectares."},
    {"secao": "Meio ambiente",
     "titulo": "Rio terá dia de chuva e mar de ressaca",
     "data": "Publicado em 02/09/2026 - 07:02",
     "url": "/meio-ambiente/noticia/2026-09/rio-tera-dia-de-chuva",
     "texto": "O Sistema Alerta Rio prevê céu encoberto e pancadas de chuva."},
    {"secao": "Economia",
     "titulo": "Bolsa sobe 1,3% e atinge maior nível em quatro meses",
     "data": "",                                   # nem toda página traz tudo
     "url": "/economia/noticia/2026-09/bolsa-sobe",
     "texto": ""},
]

SITE = "https://agenciabrasil.ebc.com.br"


def limpar_texto(bruto: str) -> str:
    """Tira espaço duro, junta espaços repetidos e apara as pontas.

    \\xa0 é o "espaço que não quebra linha". Ele PARECE um espaço na tela e
    passa despercebido — até você comparar duas strings e elas não baterem.
    """
    return re.sub(r"\s+", " ", bruto.replace("\xa0", " ")).strip()


def limpar_data(bruto: str) -> str:
    """'Publicado em   02/09/2026 - 07:02' -> '02/09/2026 07:02'.

    Uma expressão regular pequena e ancorada no FORMATO (dd/mm/aaaa hh:mm) é
    mais robusta do que fatiar a string por posição: se o rótulo mudar de
    'Publicado em' para 'Publicado', o fatiamento quebra e este não.
    """
    achado = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})", bruto)
    return f"{achado.group(1)} {achado.group(2)}" if achado else ""


def limpar(linha: dict) -> dict:
    titulo = limpar_texto(linha["titulo"])
    texto = limpar_texto(linha["texto"])
    return {
        "secao": limpar_texto(linha["secao"]),
        "titulo": titulo,
        "publicado_em": limpar_data(linha["data"]),
        "palavras": len(texto.split()),
        "url": linha["url"] if linha["url"].startswith("http") else SITE + linha["url"],
        "fonte": "Agência Brasil (EBC) — CC BY 3.0 BR",
    }


limpas = [limpar(linha) for linha in BRUTO]

print("antes  ->  depois\n")
for antes, depois in zip(BRUTO, limpas):
    print(f"  título: {antes['titulo']!r}")
    print(f"       -> {depois['titulo']!r}")
    print(f"  data:   {antes['data']!r}")
    print(f"       -> {depois['publicado_em']!r}\n")

# GUARDA: nunca grave por cima de um arquivo bom com um resultado vazio.
# Coleta que devolve zero linhas quase sempre é seletor quebrado, não site vazio.
if not limpas:
    raise SystemExit("Nada extraído — o seletor deve ter quebrado. NÃO vou gravar.")

with DESTINO.open("w", encoding="utf-8", newline="") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=list(limpas[0].keys()))
    escritor.writeheader()
    escritor.writerows(limpas)

print(f"gravado: {DESTINO.name} ({len(limpas)} linhas)")
print("\nnewline='' no open() é obrigatório no Windows — sem ele o csv escreve")
print("uma linha em branco entre cada registro. É o bug mais chato desta aula.")
print("\nDaqui, o arquivo vira insumo do painel: a coleta acabou, o uso começa.")
