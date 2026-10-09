"""
Coleta de uma página DINÂMICA com Selenium — Painel ODS Brasil, v8 (Aula 10).

A FONTE
-------
Painel de taxas de desmatamento do PRODES (INPE), no portal TerraBrasilis:
    https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates
Taxa anual de desmatamento na Amazônia Legal, por UF (9 UFs), de 1988 até hoje.
Licença do portal: Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional
(CC BY-SA 4.0) — cite a fonte E distribua o que derivar sob a mesma licença.

POR QUE SELENIUM (e não requests + BeautifulSoup, como na Aula 7)
----------------------------------------------------------------
Com requests, o servidor devolve uma CASCA: ~3 mil bytes de HTML cujo único texto
visível é "TerraBrasilis". A tabela é montada DEPOIS, no navegador, pelo
JavaScript da página. Quem não roda JavaScript não vê dado nenhum. O Selenium
pilota um navegador de verdade (Chrome, sem janela) — e o navegador roda o JS.

POR QUE ESTE ARQUIVO NÃO É IMPORTADO PELO app.py (a regra da Aula 7, com mais motivos)
------------------------------------------------------------------------------------
Não é que seja impossível: o Community Cloud não traz navegador, mas instala o
Chromium via packages.txt (ver DEPLOY.md §10.1 e o passo 6 da Aula 10). É o preço:
1. Um Chrome sem janela custa segundos para abrir (~2–5 s) e 380–640 MB de memória
   (medido) — num app que tem de 690 MB a 2,7 GB no Community Cloud.
2. O build do app passaria a depender de pacotes do sistema (chromium +
   chromium-driver), que precisam casar de versão — mais uma coisa que quebra o deploy.
3. Página dinâmica quebra mais que página estática. Coletando à parte, se quebrar,
   o painel continua no ar com a última coleta boa.
E uma taxa ANUAL de desmatamento não precisa ser coletada a cada hora.
Por isso o selenium vai em requirements-coleta.txt, e NÃO em requirements.txt.

O CAMINHO
---------
    robots.txt  ->  posso?                      (o navegador é um robô também)
    Chrome      ->  abre a página, roda o JS
    ESPERA      ->  pela CONDIÇÃO certa: as linhas, não a tabela   (🐛 tropeço da v8)
    snapshot    ->  data/raw/prodes_renderizado.html  (o HTML DEPOIS do JavaScript)
    extração    ->  BeautifulSoup sobre o snapshot    (o que já sabemos, Aula 7)
    guarda      ->  nunca gravar por cima com resultado incompleto
    saída       ->  data/processed/desmatamento_prodes.csv + desmatamento_meta.json

Rodar (com o ambiente da COLETA — ver requirements-coleta.txt):
    python -m src.coleta_dinamica                 # abre o Chrome sem janela e coleta
    python -m src.coleta_dinamica --do-snapshot   # sem rede e sem navegador: reprocessa o snapshot
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

SITE = "https://terrabrasilis.dpi.inpe.br"
URL = SITE + "/app/dashboard/deforestation/biomes/legal_amazon/rates"
LICENCA = "Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)"
FONTE = "INPE/PRODES — TerraBrasilis"

AGENTE = "INFNET-PB-IA-Aplicada/1.0 (material didatico; contato: professor)"
TEMPO_LIMITE = 60          # segundos: o máximo que aceitamos esperar pela tabela

ARQ_SNAPSHOT = RAW / "prodes_renderizado.html"
ARQ_CSV = PROCESSED / "desmatamento_prodes.csv"
ARQ_META = PROCESSED / "desmatamento_meta.json"

# A Amazônia Legal tem 9 UFs. É um fato do DOMÍNIO — e é ele que nos diz quando a
# tabela está completa (ver esperar_tabela) e quando a extração falhou (ver a guarda).
UFS_AMAZONIA_LEGAL = {
    "Acre": "AC", "Amapá": "AP", "Amazonas": "AM", "Maranhão": "MA", "Mato Grosso": "MT",
    "Pará": "PA", "Rondônia": "RO", "Roraima": "RR", "Tocantins": "TO",
}

SELETOR_UF = "#tb-area tr.dc-table-group"      # uma linha por UF: <b>Acre</b><span> - 18.882,00 km²</span>
SELETOR_ANO = "#tb-area tr.dc-table-row"       # uma linha por ano: 1988 | 620,00 km²


# --------------------------------------------------------------- 1. permissão
def permitido(url: str = URL) -> bool:
    """O navegador pilotado é um robô como outro qualquer: o robots.txt vale para ele."""
    regras = RobotFileParser()
    texto = requests.get(f"{SITE}/robots.txt", headers={"User-Agent": AGENTE}, timeout=30).text
    regras.parse(texto.splitlines())
    return regras.can_fetch(AGENTE, url)


# --------------------------------------------------------------- 2. o navegador
def abrir_navegador():
    """Chrome sem janela. O Selenium Manager (Selenium ≥ 4.6) baixa o driver sozinho —
    o livro (Selenium 4.10, driver baixado à mão) é anterior a isso."""
    from selenium import webdriver          # importado AQUI: o app nunca chega a esta linha

    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--headless=new")         # sem janela
    opcoes.add_argument("--window-size=1500,1000")
    # O Chrome sem janela já se anuncia como "HeadlessChrome" no User-Agent
    # (verificado). Não escondemos isso: disfarçar o robô é o primeiro passo de
    # quem decidiu ignorar o dono do site.
    return webdriver.Chrome(options=opcoes)


def esperar_tabela(driver, tempo_limite: int = TEMPO_LIMITE) -> None:
    """Espera até a tabela estar COMPLETA: as 9 UFs e pelo menos uma linha de ano.

    🐛 Tropeço real da v8: a primeira versão esperava pela TABELA
    (presence_of_element_located "#tb-area"). A espera terminava na hora — e a
    extração devolvia ZERO linhas. Medido: quando o driver.get() volta (~1,5 s), a
    <table> já existe, VAZIA; as 9 UFs e as 342 linhas chegam ~1 s depois, todas
    de uma vez. Esperar pelo elemento errado é o mesmo que não esperar.

    A condição certa é a do DADO: 9 UFs na tabela.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    def tabela_completa(d):
        ufs = d.find_elements(By.CSS_SELECTOR, SELETOR_UF)
        anos = d.find_elements(By.CSS_SELECTOR, SELETOR_ANO)
        return len(ufs) >= len(UFS_AMAZONIA_LEGAL) and len(anos) > 0

    WebDriverWait(driver, tempo_limite, poll_frequency=0.25).until(
        tabela_completa, message="a tabela do PRODES não ficou completa a tempo"
    )


def baixar_renderizado(url: str = URL) -> tuple[str, float]:
    """Abre a página no Chrome, espera o JavaScript montar a tabela, grava o
    SNAPSHOT do HTML renderizado e devolve (html, segundos)."""
    inicio = time.perf_counter()
    driver = abrir_navegador()
    try:
        driver.get(url)
        esperar_tabela(driver)
        html = driver.page_source          # o HTML DEPOIS do JavaScript
    finally:
        driver.quit()                      # SEMPRE: navegador esquecido aberto come memória
    RAW.mkdir(parents=True, exist_ok=True)
    ARQ_SNAPSHOT.write_text(html, encoding="utf-8")
    return html, time.perf_counter() - inicio


# --------------------------------------------------------------- 3. extrair (sem Selenium)
def _numero(texto: str) -> float:
    """'1.208,00 km²' -> 1208.0  (ponto de milhar, vírgula decimal, unidade no fim)."""
    limpo = re.sub(r"[^\d,.-]", "", texto).replace(".", "").replace(",", ".")
    return float(limpo)


def extrair_tabela(html: str) -> list[dict]:
    """Lê o HTML RENDERIZADO com BeautifulSoup — exatamente como na Aula 7.

    O Selenium só serviu para rodar o JavaScript; daqui em diante é HTML comum.
    Separar as duas coisas permite testar a extração SEM navegador e SEM rede,
    direto no snapshot.
    """
    sopa = BeautifulSoup(html, "html.parser")
    tabela = sopa.select_one("table#tb-area")
    if tabela is None:
        return []

    linhas, estado = [], None
    for tr in tabela.select("tbody tr"):
        classes = tr.get("class", [])
        if "dc-table-group" in classes:                     # cabeçalho de uma UF
            negrito = tr.find("b")
            estado = negrito.get_text(strip=True) if negrito else None
        elif "dc-table-row" in classes and estado:          # uma linha de ano
            celulas = tr.find_all("td")
            if len(celulas) < 2:
                continue
            ano = celulas[0].get_text(strip=True)
            if not ano.isdigit():
                continue
            linhas.append({
                "uf": UFS_AMAZONIA_LEGAL.get(estado, "??"),
                "estado": estado,
                "ano": int(ano),
                "area_km2": _numero(celulas[1].get_text()),
                "fonte": FONTE,
            })
    return linhas


# --------------------------------------------------------------- 4. guarda e gravação
def conferir(linhas: list[dict]) -> str:
    """A guarda da Aula 7, com o fato do domínio: devolve '' se está tudo certo,
    ou o motivo para NÃO gravar."""
    if not linhas:
        return "zero linhas — seletor quebrado ou página não carregou"
    ufs = {linha["uf"] for linha in linhas}
    if "??" in ufs:
        return "apareceu uma UF que não conhecemos — a estrutura da página mudou?"
    if len(ufs) < len(UFS_AMAZONIA_LEGAL):
        return f"só {len(ufs)} de {len(UFS_AMAZONIA_LEGAL)} UFs — a tabela veio incompleta"
    return ""


def gravar(linhas: list[dict], segundos: float, origem: str) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with ARQ_CSV.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["uf", "estado", "ano", "area_km2", "fonte"])
        escritor.writeheader()
        escritor.writerows(linhas)
    anos = sorted({linha["ano"] for linha in linhas})
    meta = {
        "coletado_em": datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M"),
        "site": FONTE,
        "url": URL,
        "licenca": LICENCA,
        "ferramenta": "Selenium (Chrome sem janela) + BeautifulSoup",
        "origem_desta_gravacao": origem,
        "linhas": len(linhas),
        "ufs": len({linha["uf"] for linha in linhas}),
        "anos": f"{anos[0]}–{anos[-1]}",
        "segundos": round(segundos, 1),
    }
    ARQ_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------- orquestração
def coletar(do_snapshot: bool = False) -> list[dict]:
    if do_snapshot:
        if not ARQ_SNAPSHOT.exists():
            sys.exit("Não há snapshot em data/raw/. Rode primeiro sem --do-snapshot.")
        html, segundos, origem = ARQ_SNAPSHOT.read_text(encoding="utf-8"), 0.0, "snapshot"
    else:
        if not permitido():
            sys.exit(f"robots.txt não permite {URL}. Parando aqui.")
        html, segundos = baixar_renderizado()
        origem = "navegador"

    linhas = extrair_tabela(html)
    problema = conferir(linhas)
    if problema:
        # Guarda contra resultado ruim (Aula 7): a última coleta boa fica onde está.
        sys.exit(f"NÃO gravei: {problema}. A coleta anterior foi preservada.")
    gravar(linhas, segundos, origem)
    return linhas


if __name__ == "__main__":
    linhas = coletar(do_snapshot="--do-snapshot" in sys.argv)
    meta = json.loads(ARQ_META.read_text(encoding="utf-8"))
    print(f"OK — {meta['linhas']} linhas · {meta['ufs']} UFs · anos {meta['anos']} · "
          f"{meta['segundos']} s · {meta['origem_desta_gravacao']}")
    print(f"     -> {ARQ_CSV.relative_to(BASE)}")
