"""Peças que os passos repetem: o endereço da página de exercício e o Chrome sem janela."""

from pathlib import Path

PAGINA = (Path(__file__).resolve().parent / "pagina_dinamica.html").as_uri()   # file:///…


def abrir_navegador():
    from selenium import webdriver

    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--headless=new")        # sem janela (tire esta linha para VER o Chrome)
    opcoes.add_argument("--window-size=1200,900")
    return webdriver.Chrome(options=opcoes)      # o Selenium Manager baixa o driver sozinho
