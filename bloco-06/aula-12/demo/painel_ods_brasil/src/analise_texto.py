"""
Análise do texto raspado — Painel ODS Brasil, v6 (Aula 8). Python puro.

O que o TP2 pede: "exiba informações relevantes geradas a partir do conteúdo
obtido, como nuvens de palavras e estatísticas básicas".

Uma nuvem de palavras é, por dentro, uma CONTAGEM: quantas vezes cada palavra
aparece. Fazemos a contagem aqui, em Python puro (`collections.Counter`, da
biblioteca padrão), e desenhamos com `st.bar_chart` — um gráfico de barras diz
a mesma coisa que a nuvem e diz melhor, porque tem escala.

Quem quiser a nuvem desenhada instala `wordcloud` + `matplotlib` e declara as
duas no requirements.txt. Não fazemos isso aqui: duas dependências pesadas para
um efeito visual não se pagam, e o Community Cloud demora mais para construir.

Rodar isoladamente:
    python -m src.analise_texto
"""

import re
import unicodedata
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ARQUIVO_TEXTO = BASE / "data" / "processed" / "noticias_texto.txt"

# Palavras que aparecem muito e informam pouco. Sem esta lista, o "top 10" de
# qualquer texto em português é: de, a, o, que, e, do, da, em… — verdadeiro e
# inútil. Manter a lista à mão (em vez de instalar o NLTK) deixa visível que
# esta é uma DECISÃO editorial, não um dado da natureza.
PALAVRAS_VAZIAS = frozenset("""
a as o os um uma uns umas de do da dos das em no na nos nas por para per com sem sob sobre
ao aos à às e ou mas que se quando onde como qual quais quanto quantos porque pois
ele ela eles elas eu tu nos vos me te lhe lhes seu sua seus suas meu minha dele dela
este esta estes estas esse essa esses essas isso isto aquele aquela aquilo
ser sao é foi era sera seja sendo estar esta estao estava ter tem tinha havia ha
mais menos muito muitos pouco pouca todo toda todos todas outro outra outros outras
ja nao sim tambem entre ate apos antes durante desde cada mesmo mesma assim ainda
segundo disse afirmou destacou ressaltou explicou acordo caso ano anos dia dias
pelo pela pelos pelas pode podem podera deve devem havera fica ficam vai vao
grande grandes parte partes forma vezes apenas cerca ainda entao logo
""".split())
# A lista acima nasceu CURTA e cresceu OLHANDO O RESULTADO: na primeira execução
# o top 15 trouxe "pelo", "pela", "pode" e "grande" — palavras verdadeiras e
# vazias. Revisar a lista depois de ver o gráfico faz parte do método; é por isso
# que ela mora aqui, visível e discutível, e não escondida dentro de uma
# biblioteca que ninguém abre.

MINIMO_LETRAS = 4


def carregar_texto(caminho: Path = ARQUIVO_TEXTO) -> str:
    """Lê o TXT produzido pela coleta. Devolve '' se ainda não houver coleta."""
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def _sem_acento(palavra: str) -> str:
    """'ambiental' e 'ambientaL' e 'Ambiental' têm de contar como a MESMA palavra.

    Normalizamos para comparar com a lista de palavras vazias (que está sem
    acento), mas exibimos a forma original — quem lê o gráfico quer ver 'saúde',
    não 'saude'.
    """
    decomposta = unicodedata.normalize("NFD", palavra.lower())
    return "".join(c for c in decomposta if unicodedata.category(c) != "Mn")


def palavras(texto: str) -> list[str]:
    """Quebra o texto em palavras, mantendo acento e hífen, descartando o resto.

    \\w em Python já inclui letras acentuadas — por isso não precisamos de uma
    expressão gigante com todas as vogais do português.
    """
    return re.findall(r"\w+(?:-\w+)?", texto.lower(), flags=re.UNICODE)


def frequencia(texto: str, quantidade: int = 20) -> list[dict]:
    """As `quantidade` palavras mais frequentes, já sem as palavras vazias.

    Devolve lista de dicionários (o formato de tabela do curso), pronta para
    st.bar_chart e st.dataframe.
    """
    contagem = Counter(
        palavra
        for palavra in palavras(texto)
        if len(palavra) >= MINIMO_LETRAS
        and not palavra.isdigit()
        and _sem_acento(palavra) not in PALAVRAS_VAZIAS
    )
    return [
        {"palavra": palavra, "ocorrencias": vezes}
        for palavra, vezes in contagem.most_common(quantidade)
    ]


def estatisticas(texto: str) -> dict:
    """As 'estatísticas básicas' do enunciado do TP2.

    ⚠️ Este número NÃO bate com a coluna `palavras` do noticias.csv — e a diferença
    é conteúdo, não bug. São dois contadores diferentes:

      · o CSV usa `len(texto.split())` por matéria  -> 10.182
      · aqui usamos a regex \\w+ sobre o TXT inteiro -> 10.439

    A diferença (257) vem de duas coisas: o TXT também contém as linhas de título
    ("# manchete"), e a regex separa tokens que o split() mantinha grudados na
    pontuação. Quando dois contadores discordam, a pergunta certa não é "qual está
    errado?", e sim "o que exatamente cada um está contando?".
    """
    todas = palavras(texto)
    uteis = [p for p in todas if len(p) >= MINIMO_LETRAS and _sem_acento(p) not in PALAVRAS_VAZIAS]
    return {
        "caracteres": len(texto),
        "palavras": len(todas),
        "palavras_uteis": len(uteis),
        "vocabulario": len(set(uteis)),
    }


if __name__ == "__main__":
    texto = carregar_texto()
    if not texto:
        raise SystemExit("Sem texto. Rode antes: python -m src.coleta_web")
    print("estatísticas:", estatisticas(texto))
    print("\ntop 15 palavras:")
    for linha in frequencia(texto, 15):
        print(f"  {linha['ocorrencias']:>4}x  {linha['palavra']}")
