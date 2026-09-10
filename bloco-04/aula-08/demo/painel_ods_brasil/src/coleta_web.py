"""
Coleta web (WebScraping) — Painel ODS Brasil, v5 (Aula 7).

POR QUE ESTE ARQUIVO NÃO É IMPORTADO PELO app.py
------------------------------------------------
Ele é um SCRIPT, executado à parte, que grava arquivos em data/. O app apenas
LÊ esses arquivos. Três razões, nesta ordem:

1. O robots.txt da Agência Brasil declara `Crawl-delay: 10` — dez segundos entre
   requisições. Um app que raspasse a cada rerun violaria isso na primeira
   interação do usuário.
2. Raspagem quebra. O seletor muda, o site sai do ar, a rede da escola bloqueia.
   Se isso derrubar o painel publicado, o problema do scraping virou problema do
   produto.
3. É o que o enunciado do TP2 pede: "Execute esses códigos separadamente e
   armazene os dados obtidos em arquivos CSV e/ou TXT nos diretórios de data/."

FONTE E LICENÇA
---------------
Agência Brasil (EBC) — conteúdo publicado sob Creative Commons Atribuição 3.0
Brasil: pode ser reutilizado desde que se cite a fonte. Citamos, em cada linha
do CSV (coluna `fonte`) e no rodapé do painel.

O CAMINHO DA COLETA (dois níveis = web crawling)
------------------------------------------------
    robots.txt  ->  posso?          (urllib.robotparser, biblioteca padrão)
    nível 1     ->  página de seção  -> lista de manchetes + links
    nível 2     ->  página da matéria -> data exata + texto completo
    saída       ->  data/raw/*.html          (o SNAPSHOT, prova do que foi lido)
                    data/processed/noticias.csv
                    data/processed/noticias_texto.txt

Rodar:
    python -m src.coleta_web              # coleta completa (respeita 10s; demora)
    python -m src.coleta_web --rapido     # 1 seção, 2 matérias (para a aula)
    python -m src.coleta_web --do-cache   # não acessa a rede: reprocessa o snapshot
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from src.data_access import verificar_ssl

# Âncora no ARQUIVO (lição da Aula 5): funciona de qualquer diretório.
BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

SITE = "https://agenciabrasil.ebc.com.br"
SECOES = {
    "Meio ambiente": "/meio-ambiente",
    "Direitos humanos": "/direitos-humanos",
    "Economia": "/economia",
}

# Identificação honesta: quem somos, para quê, e como nos avisar de um problema.
# Fingir-se de navegador é a primeira coisa que se faz quando se decide ignorar
# o dono do site — e nós não vamos por esse caminho.
AGENTE = "INFNET-PB-IA-Aplicada/1.0 (material didatico; contato: professor)"
CABECALHOS = {"User-Agent": AGENTE}

PAUSA_PADRAO = 10.0    # usada se o robots.txt não declarar Crawl-delay
TEMPO_LIMITE = 30

if not verificar_ssl():
    # Mesma exceção declarada de fora da Aula 5: só silencia o aviso quando
    # ALGUÉM desligou a verificação de propósito (proxy da escola).
    import urllib3

    urllib3.disable_warnings()


# --------------------------------------------------------------- 1. permissão
def permissao(url_base: str = SITE) -> tuple[RobotFileParser, float]:
    """Lê o robots.txt do site e devolve (regras, pausa em segundos).

    robots.txt não é lei nem cadeado: é um pedido explícito do dono do site,
    escrito em um formato que a biblioteca padrão do Python já sabe ler. Ignorá-lo
    é uma decisão, não um descuido — e é a decisão errada.
    """
    regras = RobotFileParser()
    texto = requests.get(
        f"{url_base}/robots.txt",
        headers=CABECALHOS,
        timeout=TEMPO_LIMITE,
        verify=verificar_ssl(),
    ).text
    regras.parse(texto.splitlines())
    pausa = regras.crawl_delay(AGENTE)
    return regras, float(pausa) if pausa else PAUSA_PADRAO


# --------------------------------------------------------------- 2. baixar
def baixar(url: str, regras: RobotFileParser, pausa: float, nome_arquivo: str) -> str:
    """Baixa uma página, GRAVA O SNAPSHOT em data/raw/ e devolve o HTML.

    O snapshot é o que separa "eu raspei" de "eu acho que raspei": ele permite
    reprocessar sem tocar no servidor de novo, e serve de prova do que estava
    escrito na página no dia da coleta.
    """
    if not regras.can_fetch(AGENTE, url):
        raise PermissionError(f"robots.txt não permite: {url}")

    resposta = requests.get(url, headers=CABECALHOS, timeout=TEMPO_LIMITE, verify=verificar_ssl())
    resposta.raise_for_status()          # 403/404/500 param aqui, e não 10 linhas adiante
    resposta.encoding = resposta.apparent_encoding or "utf-8"

    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / nome_arquivo).write_text(resposta.text, encoding="utf-8")

    time.sleep(pausa)                    # a gentileza que o robots.txt pediu
    return resposta.text


def ler_snapshot(nome_arquivo: str) -> str | None:
    caminho = RAW / nome_arquivo
    return caminho.read_text(encoding="utf-8") if caminho.exists() else None


# --------------------------------------------------------------- 3. extrair
def extrair_manchetes(html: str, secao: str) -> list[dict]:
    """Nível 1: da página de seção, tira manchete + link.

    O padrão da página é <a href="/…/noticia/…"><h2>título</h2></a>. Procuramos
    o LINK e perguntamos se ele tem um título dentro — e não o contrário — porque
    é o link que precisamos para o nível 2.
    """
    sopa = BeautifulSoup(html, "html.parser")
    itens, vistos = [], set()

    for link in sopa.find_all("a", href=True):
        if "/noticia/" not in link["href"]:
            continue
        titulo_tag = link.find(["h1", "h2", "h3"])
        if titulo_tag is None:
            continue
        titulo = titulo_tag.get_text(" ", strip=True)
        url = urljoin(SITE, link["href"])
        if not titulo or url in vistos:
            continue                     # a mesma matéria aparece 2x (destaque + lista)
        vistos.add(url)
        # A data aproximada está na PRÓPRIA URL: /noticia/2026-09/titulo-em-slug
        ano_mes = re.search(r"/noticia/(\d{4}-\d{2})/", url)
        itens.append({
            "secao": secao,
            "titulo": titulo,
            "url": url,
            "ano_mes": ano_mes.group(1) if ano_mes else "",
        })
    return itens


def extrair_materia(html: str) -> dict:
    """Nível 2: da página da matéria, tira a data exata e o texto completo."""
    sopa = BeautifulSoup(html, "html.parser")

    titulo_tag = sopa.find("h1")
    bloco_data = sopa.find("div", class_="data")
    corpo = sopa.find("div", class_="conteudo-noticia")

    paragrafos = []
    if corpo is not None:
        paragrafos = [
            p.get_text(" ", strip=True)
            for p in corpo.find_all("p")
            if len(p.get_text(strip=True)) > 40
        ]

    texto = "\n".join(paragrafos)
    return {
        "titulo_materia": titulo_tag.get_text(" ", strip=True) if titulo_tag else "",
        "publicado_em": _limpar_data(bloco_data.get_text(" ", strip=True) if bloco_data else ""),
        "paragrafos": len(paragrafos),
        "palavras": len(texto.split()),
        "texto": texto,
    }


def _limpar_data(bruto: str) -> str:
    """'Publicado em   02/09/2026 - 07:02'  ->  '02/09/2026 07:02'.

    Limpeza é metade do scraping: o que vem da página vem com rótulo, espaço
    duplicado e travessão no meio.
    """
    achado = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})", bruto)
    return f"{achado.group(1)} {achado.group(2)}" if achado else bruto.strip()


# --------------------------------------------------------------- 4. gravar
def gravar_csv(linhas: list[dict], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    campos = ["secao", "titulo", "publicado_em", "palavras", "url", "fonte"]
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)


def gravar_texto(linhas: list[dict], caminho: Path) -> None:
    """Um TXT com o texto corrido — é a matéria-prima da contagem de palavras (Aula 8)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    partes = [f"# {linha['titulo']}\n{linha.get('texto', '')}" for linha in linhas]
    caminho.write_text("\n\n".join(partes), encoding="utf-8")


# --------------------------------------------------------------- 5. orquestrar
def coletar(rapido: bool = False, do_cache: bool = False) -> list[dict]:
    """Executa a coleta de ponta a ponta. Devolve as linhas coletadas."""
    secoes = dict(list(SECOES.items())[:1]) if rapido else SECOES
    limite_materias = 2 if rapido else None

    if do_cache:
        regras, pausa = None, 0.0
    else:
        regras, pausa = permissao()
        print(f"robots.txt lido · Crawl-delay = {pausa:.0f}s · respeitando.")

    manchetes: list[dict] = []
    for secao, caminho in secoes.items():
        arquivo = f"secao_{caminho.strip('/')}.html"
        if do_cache:
            html = ler_snapshot(arquivo)
            if html is None:
                print(f"  (sem snapshot de {secao} — pulando)")
                continue
        else:
            html = baixar(SITE + caminho, regras, pausa, arquivo)
        achados = extrair_manchetes(html, secao)
        print(f"  {secao}: {len(achados)} manchetes")
        manchetes.extend(achados)

    linhas = []
    for i, item in enumerate(manchetes):
        if limite_materias is not None and i >= limite_materias:
            item.update({"publicado_em": "", "palavras": 0, "texto": ""})
            linhas.append({**item, "fonte": "Agência Brasil (EBC) — CC BY 3.0 BR"})
            continue
        arquivo = "materia_" + item["url"].rstrip("/").rsplit("/", 1)[-1][:60] + ".html"
        html = ler_snapshot(arquivo) if do_cache else baixar(item["url"], regras, pausa, arquivo)
        if html is None:
            continue
        detalhe = extrair_materia(html)
        linhas.append({**item, **detalhe, "fonte": "Agência Brasil (EBC) — CC BY 3.0 BR"})

    gravar_csv(linhas, PROCESSED / "noticias.csv")
    gravar_texto([l for l in linhas if l.get("texto")], PROCESSED / "noticias_texto.txt")
    (PROCESSED / "coleta_meta.json").write_text(
        json.dumps(
            {
                "coletado_em": datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M"),
                "site": SITE,
                "licenca": "Creative Commons Atribuição 3.0 Brasil",
                "secoes": list(secoes),
                "noticias": len(linhas),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return linhas


if __name__ == "__main__":
    rapido = "--rapido" in sys.argv
    do_cache = "--do-cache" in sys.argv
    inicio = time.perf_counter()
    try:
        linhas = coletar(rapido=rapido, do_cache=do_cache)
    except PermissionError as erro:
        print(f"PARADO POR robots.txt: {erro}")
        sys.exit(1)
    except requests.HTTPError as erro:
        print(f"O servidor recusou: {erro}. O snapshot anterior continua valendo.")
        sys.exit(1)
    print(f"\n{len(linhas)} notícias em {time.perf_counter() - inicio:.1f}s")
    print(f"  -> {PROCESSED / 'noticias.csv'}")
    print(f"  -> {PROCESSED / 'noticias_texto.txt'}")
    for linha in linhas[:3]:
        print(f"  · [{linha['secao']}] {linha['titulo'][:70]} ({linha.get('palavras', 0)} palavras)")
