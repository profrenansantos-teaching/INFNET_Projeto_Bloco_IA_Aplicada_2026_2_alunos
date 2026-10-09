"""
Passo 4 — Interagir, esperar de novo, e entregar o HTML ao BeautifulSoup.

A página só mostra 2024 depois de um CLIQUE. O roteiro completo de uma coleta
dinâmica, em miniatura:

    abrir -> ir -> ESPERAR (9 linhas) -> ESPERAR (botão clicável) -> CLICAR
          -> ESPERAR (18 linhas) -> page_source -> BeautifulSoup (Aula 7)
          -> guarda -> CSV -> fechar

Três ideias para levar:
  · 🐛 esperar pelo DADO não é esperar pela AÇÃO. A primeira versão deste passo
    esperava as 9 linhas e clicava — e levava ElementNotInteractableException:
    a 9ª linha aparece 250 ms ANTES de a página mostrar o botão. Espere pelo que
    você vai USAR: element_to_be_clickable antes de clicar;
  · depois de cada ação, uma espera pela CONDIÇÃO do dado — o clique não
    devolve o dado; ele só dispara o JavaScript que vai buscá-lo;
  · o Selenium serve para RODAR o JavaScript. Extrair é com o BeautifulSoup,
    sobre o page_source — o que já sabemos, e testável sem navegador.

Rodar:  python passo04_clicar_e_extrair.py      (sem rede) -> grava saida_passo04.csv
"""

import csv
from pathlib import Path

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from _comum import PAGINA, abrir_navegador

SAIDA = Path(__file__).resolve().parent / "saida_passo04.csv"


def linhas_na_tela(minimo: int):
    """Condição para o WebDriverWait: devolve as linhas quando há pelo menos `minimo`;
    senão devolve False — e ele tenta de novo (a cada 0,5 s, até o tempo-limite)."""
    def condicao(driver):
        linhas = driver.find_elements(By.CSS_SELECTOR, "#tabela tbody tr")
        return linhas if len(linhas) >= minimo else False
    return condicao


with abrir_navegador() as driver:
    driver.get(PAGINA)
    esperar = WebDriverWait(driver, 10)

    esperar.until(linhas_na_tela(9))
    print("2025 carregado: 9 linhas")

    # 🐛 Clicar aqui direto dava ElementNotInteractableException: o botão ainda
    # estava escondido. Espere pelo que você vai USAR, não só pelo dado.
    botao = esperar.until(EC.element_to_be_clickable((By.ID, "mais")))
    botao.click()                                      # a interação
    esperar.until(linhas_na_tela(18))                  # o clique NÃO devolve o dado
    print("2024 carregado depois do clique: 18 linhas")

    html = driver.page_source                          # o HTML DEPOIS do JavaScript

# ---- daqui para baixo, nada de Selenium: é a Aula 7
sopa = BeautifulSoup(html, "html.parser")
dados = []
for tr in sopa.select("#tabela tbody tr"):
    uf, ano, area = [td.get_text(strip=True) for td in tr.find_all("td")]
    dados.append({"uf": uf, "ano": int(ano),
                  "area_km2": float(area.replace(".", "").replace(",", "."))})

if len({d["uf"] for d in dados}) < 9:                  # a guarda da Aula 7
    raise SystemExit("NÃO gravei: menos de 9 UFs. Algo não carregou.")

with SAIDA.open("w", newline="", encoding="utf-8") as f:
    escritor = csv.DictWriter(f, fieldnames=["uf", "ano", "area_km2"])
    escritor.writeheader()
    escritor.writerows(dados)

print(f"OK — {len(dados)} linhas -> {SAIDA.name}")
print("amostra:", dados[0], "…", dados[-1])
