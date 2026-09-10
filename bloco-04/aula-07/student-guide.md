# Aula 7 — Material de apoio do aluno
### Quando não existe API · PB Etapa 4 · subcompetência 2.4

> Este guia é para consultar **enquanto você faz o TP2**. Ele repete, em forma de referência, o que
> a aula mostrou em forma de história.

---

## 1. A pergunta que vem antes do código

Você quer dados que estão numa página web. Antes de escrever a primeira linha, responda três
perguntas — **nesta ordem**:

| # | Pergunta | Onde se responde | Se a resposta for "não" |
|---|----------|------------------|--------------------------|
| 1 | **Posso baixar?** | `https://site.com/robots.txt` — seguir suas diretivas é *"ethical duty of all developers"* [Chapagain, p100] | procure outra fonte, ou peça acesso ao dono |
| 2 | **Com que frequência?** | `Crawl-delay`, no mesmo arquivo | respeite a pausa — ela decide a arquitetura |
| 3 | **Posso publicar o que baixei?** | licença/termos de uso do conteúdo | você pode **usar** sem poder **republicar** |

**As perguntas 1 e 3 são independentes.** `robots.txt` responde *"posso baixar?"*. A licença
responde *"posso publicar?"*. Existe site que permite uma e não a outra.

### Como verificar, em cinco linhas

```python
from urllib.robotparser import RobotFileParser   # já vem com o Python
import requests

AGENTE = "SeuNome-PB-IA/1.0 (trabalho academico; contato: seu-email)"

regras = RobotFileParser()
regras.parse(requests.get("https://site.com/robots.txt").text.splitlines())

regras.can_fetch(AGENTE, "https://site.com/a-pagina-que-eu-quero")   # True / False
regras.crawl_delay(AGENTE)                                           # segundos, ou None
```

> **Duas das três fontes tentadas nesta aula morreram aqui** — uma devolveu **403** e a outra tinha
> `Disallow: */news/` exatamente na URL desejada. Nenhuma das duas por erro de programação.

### Identifique-se de verdade

```python
AGENTE = "SeuNome-PB-IA/1.0 (trabalho academico; contato: seu-email)"
```

Diz **quem** é, **para quê** e **como avisar** se estiver incomodando.
**Não** copie a assinatura de um Chrome: quando o site bloquear, você não terá como pedir liberação.

---

## 2. Baixar — e ler o status

```python
resposta = requests.get(url, headers={"User-Agent": AGENTE}, timeout=30)

print(resposta.status_code)        # LEIA. Sempre.
resposta.raise_for_status()        # 403/404/500 param AQUI, e não 10 linhas adiante

resposta.encoding = resposta.apparent_encoding or "utf-8"
Path("data/raw/pagina.html").write_text(resposta.text, encoding="utf-8")   # SNAPSHOT
```

### Os códigos que você vai encontrar

| Código | O que significa | O que fazer |
|--------|-----------------|-------------|
| **200** | deu certo | siga |
| **403** | o servidor **recusou** você | outra fonte, ou pedir acesso. Não insista |
| **404** | a URL não existe | confira o endereço |
| **429** | você está pedindo rápido demais | aumente a pausa |
| **500+** | problema do servidor | tente mais tarde; use o snapshot anterior |

> ⚠️ **O erro mais caro desta aula:** um **403 vem com uma página de erro em HTML válido**. Sem
> `raise_for_status()`, o BeautifulSoup processa essa página sem reclamar e devolve **lista vazia**.
> Você passa meia hora consertando o seletor certo contra a página errada.

### Por que gravar o snapshot

1. reprocessar não custa requisição nova — e você vai reprocessar dezenas de vezes;
2. é educado: o servidor dos outros não é o seu disco;
3. é a **prova** do que a página dizia no dia da coleta.

---

## 3. Extrair com BeautifulSoup

```python
from bs4 import BeautifulSoup

sopa = BeautifulSoup(html, "html.parser")   # o parser vem com o Python: sem lxml
```

### As quatro operações que resolvem quase tudo

| Operação | Devolve | Quando usar |
|----------|---------|-------------|
| `sopa.find("h1")` | a **primeira** tag que casar, ou **`None`** [Chapagain, p135] | quando só existe um |
| `sopa.find_all("a", href=True)` | **lista** de tags — **vazia** se nada casar [Chapagain, p137] | quando são vários |
| `sopa.select("div.box-texto h2")` | **lista** (seletor CSS); `select()` ≈ `find_all()`, `select_one()` ≈ `find()` [Chapagain, p138] | quando o caminho é mais claro em CSS |
| `tag.get_text(" ", strip=True)` | **texto** limpo, sem marcação | sempre que for exibir |

Atributo se lê como dicionário: `link["href"]`, `img["src"]`.

> 🐛 **Duas falhas diferentes, e a segunda é pior.** `find()` devolve **`None`** — e
> `sopa.find("h1").get_text()` numa página sem `h1` **quebra** com `AttributeError`. Já `find_all()`
> devolve **lista vazia** [Chapagain, p137]: **não quebra nada**, e o seletor errado passa
> despercebido até o CSV sair vazio. **Pergunte antes de usar; e cheque o resultado antes de
> gravar:**
> ```python
> titulo = sopa.find("h1")
> texto = titulo.get_text(" ", strip=True) if titulo else ""
> ```

### O padrão "do link para o dado"

Quando você precisa do **link** e do **título**, procure o link e desça até o título — não o
contrário:

```python
for link in sopa.find_all("a", href=True):
    if "/noticia/" not in link["href"]:
        continue
    titulo = link.find(["h1", "h2", "h3"])   # o título está DENTRO do link
    if titulo is None:
        continue                              # link de imagem: ignore
    print(titulo.get_text(" ", strip=True), link["href"])
```

### Dois níveis (crawling)

A página de listagem dá **manchete + link**. O texto completo está **na matéria**. Seguir o link e
repetir a extração é *web crawling* — e exige uma pausa entre as requisições.

---

## 4. Limpar — metade do trabalho

```python
import re

def limpar_texto(bruto):
    """\\xa0 é o espaço que não quebra linha: parece um espaço e não é."""
    return re.sub(r"\s+", " ", bruto.replace("\xa0", " ")).strip()

def limpar_data(bruto):
    """'Publicado em   02/09/2026 - 07:02' -> '02/09/2026 07:02'"""
    achado = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})", bruto)
    return f"{achado.group(1)} {achado.group(2)}" if achado else ""
```

**Ancore no formato, não na posição.** Fatiar a string depois de `"Publicado em"` quebra no dia em
que o rótulo mudar; a expressão regular acima, não.

### O checklist de limpeza

- [ ] `\xa0` e espaços repetidos
- [ ] rótulos colados ao valor ("Publicado em", "R$", "%")
- [ ] marcadores de referência da Wikipédia e afins (`[3]`)
- [ ] número com separador brasileiro → `int` / `float`
- [ ] link relativo → absoluto (`urljoin(SITE, href)`)

---

## 5. Gravar — com uma guarda

```python
if not linhas:
    raise SystemExit("Nada extraído — o seletor deve ter quebrado. NÃO vou gravar.")

with caminho.open("w", encoding="utf-8", newline="") as arquivo:   # newline="" !
    escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
    escritor.writeheader()
    escritor.writerows(linhas)
```

- **A guarda** evita destruir a última coleta boa. Zero linhas é quase sempre seletor quebrado.
- **`newline=""`** é obrigatório no Windows; sem ele o CSV sai com uma linha em branco entre cada
  registro.

---

## 6. A arquitetura: coleta ≠ app

```
src/coleta_web.py   raspa  ->  data/processed/noticias.csv     roda ANTES, à parte
src/noticias.py     lê o arquivo (Python puro)
app.py              mostra                                      nunca toca na rede
```

**Duas razões, e a segunda é a que importa:**

1. o `Crawl-delay` (10 s no nosso caso) torna impossível raspar dentro de um app interativo;
2. **a fragilidade da raspagem não pode virar fragilidade do produto.** O seletor vai quebrar um
   dia; quando quebrar, o painel publicado tem de continuar no ar mostrando a última coleta.

É também literalmente o que o enunciado do TP2 pede: *"Execute esses códigos separadamente e
armazene os dados obtidos em arquivos CSV e/ou TXT nos diretórios de `data/`."*

### O que vai (e o que não vai) para o Git

```gitignore
data/raw/*.html      # conteúdo de TERCEIROS, megabytes, regenerável -> NÃO versione
                     # data/processed/ É versionado: o app publicado depende dele
```

---

## 7. Anti-padrões (cada um custou tempo real)

| Anti-padrão | Por que dói |
|-------------|-------------|
| Rodar 30x ajustando o seletor, batendo no site toda vez | usa o servidor dos outros como disco; e é lento |
| `User-Agent` de Chrome | mentira; e quando bloquearem, você não tem como pedir liberação |
| Parsear sem checar o status | você depura o seletor **certo** contra a página **errada** |
| Gravar por cima com resultado vazio | destrói a última coleta boa |
| Raspar dentro do `app.py` | viola o `Crawl-delay` e amarra o painel à saúde do site alheio |
| Publicar conteúdo de terceiros sem ver a licença | problema jurídico, não técnico |

---

## 8. ⚠️ Usando IA para escrever seu scraper

Peça um scraper a um assistente. O código vem funcionando — e quase sempre **sem `robots.txt`, sem
`raise_for_status()` e sem pausa entre requisições**.

> **A regra do curso continua:** use IA, desde que você **entenda e saiba explicar** o que ela
> gerou. Aqui isso tem um teste concreto — se o código gerado não faz as três coisas acima, ele está
> sintaticamente certo e profissionalmente errado, e quem responde por isso é você.

---

## 9. Para o seu TP2 — checklist da subcompetência 2.4

- [ ] Escolhi uma fonte e **verifiquei o `robots.txt`** (posso? qual o `Crawl-delay`?)
- [ ] Verifiquei a **licença** do conteúdo e **cito a fonte** no app
- [ ] Meu `User-Agent` diz quem eu sou
- [ ] Leio o **status HTTP** e chamo `raise_for_status()`
- [ ] Gravo o **snapshot** em `data/raw/` (e ele está no `.gitignore`)
- [ ] Faço **pausa** entre requisições
- [ ] **Limpo** o que extraí (espaços, rótulos, tipos, links absolutos)
- [ ] Tenho **guarda contra resultado vazio** antes de gravar
- [ ] O script roda **separado** do app e grava em `data/processed/` (CSV e/ou TXT)
- [ ] O app **lê o arquivo** e não acessa a rede

---

## 10. Fontes

- **CHAPAGAIN, A.** *Hands-On Web Scraping with Python*, 2ª ed. Packt, 2023 — leitura indicada pelo
  Plano de Ensino para a subcompetência 2.4. **Leia o cap. 5** (*Scraping the Web with Scrapy and
  Beautiful Soup*) e a seção *Parsing robots.txt and sitemap.xml* do **cap. 3**.
- Documentação oficial: [`requests`](https://requests.readthedocs.io),
  [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/),
  [`urllib.robotparser`](https://docs.python.org/3/library/urllib.robotparser.html).
- **Agência Brasil (EBC)** — fonte dos dados do demo; Creative Commons Atribuição 3.0 Brasil.

> **Transparência sobre como este material foi feito.** O conteúdo técnico foi construído a partir
> da **documentação oficial** e **verificado rodando** contra o site real; o livro-texto entrou no
> acervo depois, e as citações foram acrescentadas. A leitura **confirmou** tudo — inclusive as duas
> regras que mais importam aqui: `find()` devolve `None` [Chapagain, p135] e **`find_all()` devolve
> lista vazia** quando não casa [Chapagain, p137].
>
> **E há um ponto em que este curso discorda do livro, de propósito.** Ele recomenda o parser
> `lxml` como "the best parser… because of its memory and speed" [Chapagain, p132]; nós usamos
> `html.parser`, que **já vem com o Python**, para não acrescentar dependência a um app publicado no
> Community Cloud. Trocaríamos se a velocidade virasse um problema **medido**.
>
> Discordar da fonte **com um motivo declarado** é leitura crítica; sem motivo, é desleixo. Vale
> para o livro e vale para a IA.
