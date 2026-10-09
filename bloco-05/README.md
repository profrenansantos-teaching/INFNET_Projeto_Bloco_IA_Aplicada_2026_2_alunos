# Bloco 5 — Desenvolvimento de aplicações multifacetadas
### PB Etapa 5 · Competência 3 · entrega: **TP3** (abre aqui; fecha na Etapa 6)

**Competência 3:** integrar aplicação com múltiplas páginas com dados provenientes de APIs
personalizadas.

| Aula | Subcomp. | Tema | Ideia-força |
|:----:|:--------:|------|-------------|
| [aula-09/](aula-09/) | **3.1** | **Uma pergunta, uma página** | roteador → páginas → **estado entre páginas** → link direto |
| [aula-10/](aula-10/) | **3.2** | **Quando o dado chega depois** | a casca → a escada → Selenium → esperar pela condição |

| Subcomp. | O que você deve ser capaz de fazer | Leitura de apoio |
|---------:|-----------------------------------|------------------|
| **3.1** | Criar uma aplicação com **múltiplas páginas e menu de navegação** utilizando Streamlit. | RAGHAVENDRA, cap. **7** |
| **3.2** | Extrair dados de **páginas dinâmicas** com Web Scraping usando **Selenium**. | CHAPAGAIN, *Hands-On Web Scraping with Python*, 2ª ed., cap. **8** |

## O arco do bloco

A Aula 9 divide o painel, que tinha virado uma página de 360 linhas, em **seis páginas** — uma para
cada pergunta do usuário — com **menu de navegação** e **endereço próprio** para cada uma. O que se
quebra quando um app deixa de ser um script só (o filtro que esquecia, o link direto que quebrava)
é a matéria da aula. A Aula 10 traz uma fonte cujo dado **não está no HTML**: ele só aparece depois
que o JavaScript da página roda.

> **Os livros usam a pasta `pages/`; o curso usa `st.navigation`.** As duas formas funcionam no
> Streamlit atual, mas não se somam: com `st.navigation`, a pasta `pages/` é ignorada. O
> [`aula-09/student-guide.md`](aula-09/student-guide.md) compara as duas.

**Rode o app de dentro da pasta dele.** Num app multipáginas, o caminho de cada página é relativo
ao `app.py`:

```bash
cd aula-09/demo/painel_ods_brasil
streamlit run app.py
```

**A Aula 10 precisa do Google Chrome** instalado e de um ambiente próprio para a coleta — o app não
abre navegador:

```bash
cd aula-10/demo/painel_ods_brasil
pip install -r requirements-coleta.txt     # tudo do app + selenium
python -m src.coleta_dinamica              # coleta à parte -> data/processed/
streamlit run app.py                       # o app só lê o CSV
```

Os passos 1 a 4 de [`aula-10/aula-10-step-by-step/`](aula-10/aula-10-step-by-step/) **não precisam de
internet**: eles usam uma página de exercício local. O driver do Chrome, o próprio Selenium baixa na
primeira execução (essa vez, sim, com rede).

**O TP3 abre na Aula 9.** O checklist do item 2 está na seção 8 do
[`aula-09/student-guide.md`](aula-09/student-guide.md); o do item 3 (*Selenium, se necessário*), na seção 10
do [`aula-10/student-guide.md`](aula-10/student-guide.md). **O TP3 fecha no Bloco 6.**
