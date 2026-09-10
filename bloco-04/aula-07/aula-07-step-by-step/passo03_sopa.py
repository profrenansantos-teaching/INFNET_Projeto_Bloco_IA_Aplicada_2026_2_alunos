"""
Passo 3 — Do texto à estrutura: BeautifulSoup.

Não acessa a rede. Lê o snapshot gravado pelo passo 2 (e, se ele não existir,
usa um HTML de brinquedo embutido aqui embaixo — o passo roda sempre).

As quatro operações que resolvem 90% de qualquer raspagem:

    sopa.find("h1")                     o PRIMEIRO que casar   -> tag ou None
    sopa.find_all("a", href=True)       TODOS que casarem      -> lista
    sopa.select("div.data")             seletor CSS            -> lista
    tag.get_text(" ", strip=True)       só o texto, sem marcas -> str

E a regra que evita metade dos bugs: `find` devolve **None** quando não acha.
`.get_text()` em None é AttributeError. Sempre pergunte antes de usar.

Rodar:  python passo03_sopa.py
"""

from pathlib import Path

from bs4 import BeautifulSoup

SNAPSHOT = Path(__file__).parent / "snapshot_meio_ambiente.html"

HTML_DE_BRINQUEDO = """
<html><body>
  <div class="view-content">
    <div class="box-texto">
      <a href="/meio-ambiente/noticia/2026-09/rio-tera-dia-de-chuva">
        <h2>Rio terá dia de chuva e mar de ressaca</h2>
      </a>
    </div>
    <div class="box-texto">
      <a href="/meio-ambiente/noticia/2026-08/depois-da-cop17">
        <h2>Depois da COP17, Brasil é cobrado a efetivar metas</h2>
      </a>
    </div>
    <a href="/institucional/quem-somos">Quem somos</a>
  </div>
</body></html>
"""

if SNAPSHOT.exists():
    html = SNAPSHOT.read_text(encoding="utf-8")
    print(f"lendo o snapshot real ({len(html):,} caracteres)".replace(",", "."))
else:
    html = HTML_DE_BRINQUEDO
    print("snapshot não encontrado — usando o HTML de brinquedo (rode o passo 2 antes)")

sopa = BeautifulSoup(html, "html.parser")   # html.parser vem com o Python: zero dependência extra

print("\n1) find — o primeiro título da página")
titulo = sopa.find("h1")
print("   ", titulo.get_text(" ", strip=True) if titulo else "(não achei h1 — e o programa NÃO quebrou)")

print("\n2) find_all — todos os links")
links = sopa.find_all("a", href=True)
print(f"    {len(links)} links no total")

print("\n3) filtrar: só os que apontam para uma notícia")
noticias = [a for a in links if "/noticia/" in a["href"]]
print(f"    {len(noticias)} apontam para /noticia/")
print("    (o filtro é feito em PYTHON, não no seletor — mais legível e mais fácil de depurar)")

print("\n4) do link para o título: descer na árvore")
vistos = set()
for a in noticias:
    h = a.find(["h1", "h2", "h3"])       # o título está DENTRO do link
    if h is None:
        continue                          # link de imagem, sem texto: ignore
    titulo = h.get_text(" ", strip=True)
    if titulo in vistos:
        continue                          # a mesma matéria aparece 2x (destaque + lista)
    vistos.add(titulo)
    print(f"    · {titulo[:64]}")
    print(f"      href = {a['href'][:64]}")   # atributo se lê como dicionário

print("\n5) select — o mesmo com seletor CSS")
print(f"    div.box-texto  -> {len(sopa.select('div.box-texto'))} blocos")
print("    Use o que for mais claro: os dois chegam ao mesmo lugar.")

print("\n--- a lição do passo ---")
print("Você não 'extrai dados' de uma página: você extrai de uma ESTRUTURA que")
print("alguém escolheu. Se essa pessoa mudar a classe do div amanhã, seu código")
print("para — sem erro, devolvendo lista vazia. Por isso o passo 4 checa o")
print("resultado antes de gravar.")
