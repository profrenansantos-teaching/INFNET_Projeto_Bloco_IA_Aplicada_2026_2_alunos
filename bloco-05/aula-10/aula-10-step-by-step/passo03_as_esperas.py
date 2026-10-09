"""
Passo 3 — Quatro jeitos de esperar, e só um deles é confiável.

A página de exercício começa vazia e recebe as 9 linhas UMA A UMA (a primeira
aos ~0,8 s, a última aos ~3 s). Cada estratégia abaixo roda num navegador novo:

  A · sem espera          -> lê na hora: 0 linhas
  B · time.sleep(1)       -> um chute. Aqui erra por pouco (a 1ª linha chega aos
                             ~1,05 s): 0 linhas. Com sleep(5) daria certo — e
                             custaria 5 s em TODA coleta, precisando ou não.
  C · espera IMPLÍCITA    -> a única que o livro mostra [Chapagain]. find_elements
                             volta assim que existe PELO MENOS UM elemento:
                             a lista vem PELA METADE (1 de 9) — sem erro nenhum.
  D · espera EXPLÍCITA    -> WebDriverWait + a CONDIÇÃO do dado ("9 UFs
                             carregadas"): completa, e sem esperar à toa.

Medido em 23/09/2026 (três execuções, sempre igual): A 0/9 · B 0/9 · C 1/9 · D 9/9.

Rodar:  python passo03_as_esperas.py      (sem rede)
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from _comum import PAGINA, abrir_navegador

LINHAS = (By.CSS_SELECTOR, "#tabela tbody tr")


def sem_espera(driver):
    return driver.find_elements(*LINHAS)


def com_sleep(driver):
    time.sleep(1)                                   # 1 s: por que 1? ninguém sabe
    return driver.find_elements(*LINHAS)


def implicita(driver):
    driver.implicitly_wait(10)                      # "espere ATÉ 10 s por qualquer elemento"…
    return driver.find_elements(*LINHAS)            # …e volta quando aparece o PRIMEIRO


def explicita(driver):
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "status"), "9 UFs carregadas")
    )
    return driver.find_elements(*LINHAS)


ESTRATEGIAS = [
    ("A · sem espera", sem_espera),
    ("B · time.sleep(1)", com_sleep),
    ("C · espera implícita (a do livro)", implicita),
    ("D · espera explícita (a condição)", explicita),
]

for nome, estrategia in ESTRATEGIAS:
    with abrir_navegador() as driver:
        inicio = time.perf_counter()
        driver.get(PAGINA)
        linhas = estrategia(driver)
        segundos = time.perf_counter() - inicio
        veredito = "completa" if len(linhas) == 9 else "INCOMPLETA — e sem erro nenhum"
        print(f"{nome:36s} {segundos:4.1f} s   {len(linhas)}/9 linhas   {veredito}")
