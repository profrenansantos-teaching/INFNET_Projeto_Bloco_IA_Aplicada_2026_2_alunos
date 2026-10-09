"""
Passo 2 — O navegador pilotado: abrir, ler, fechar.

O Selenium abre um Chrome de verdade (sem janela), carrega a página e deixa o
JavaScript rodar. Três coisas para observar:

  1. quanto custa só ABRIR o navegador (segundos, não milissegundos);
  2. o User-Agent: o Chrome sem janela se anuncia como "HeadlessChrome" —
     o robô não está disfarçado, e não vamos disfarçá-lo;
  3. lendo LOGO DEPOIS do driver.get(), a tabela ainda está vazia.
     O get() espera a página CARREGAR — não espera o JavaScript terminar.

O `with` fecha o navegador mesmo se der erro (é o driver.quit() num finally).

Rodar:  python passo02_o_navegador.py        (sem rede: a página é um arquivo local)
"""

import time

from selenium.webdriver.common.by import By

from _comum import PAGINA, abrir_navegador

inicio = time.perf_counter()
with abrir_navegador() as driver:
    print(f"1 · abrir o Chrome levou {time.perf_counter() - inicio:.1f} s")
    print("2 · User-Agent:", driver.execute_script("return navigator.userAgent"))

    driver.get(PAGINA)                                   # espera a página CARREGAR…
    linhas = driver.find_elements(By.CSS_SELECTOR, "#tabela tbody tr")
    status = driver.find_element(By.ID, "status").text
    print(f"3 · logo depois do get(): {len(linhas)} linha(s) · status: {status!r}")

    time.sleep(4)                                        # (só para comparar — ver o passo 3)
    linhas = driver.find_elements(By.CSS_SELECTOR, "#tabela tbody tr")
    status = driver.find_element(By.ID, "status").text
    print(f"    4 s depois:            {len(linhas)} linha(s) · status: {status!r}")
    print("    primeira linha:", linhas[0].text if linhas else "—")
# aqui o navegador já foi fechado pelo `with`
