# Publicar o Painel ODS no Streamlit Community Cloud

> Roteiro executável da **Aula 5** (PB Etapa 3 · subcompetência 2.1).
> Fonte de referência: RICHARDS, T. *Streamlit for Data Science*, 2ª ed., cap. 5. Citações no formato
> `[Richards, pXX]` remetem à página do PDF.

## 0 · O que o Community Cloud precisa (o contrato)

Exatamente quatro coisas — e **toda** falha de deploy é a falta de uma delas:

| # | Item | No nosso projeto |
|---|------|------------------|
| 1 | **Repositório** no GitHub (público, por padrão) | `painel-ods-brasil` |
| 2 | **Branch** | `main` |
| 3 | **Arquivo principal** (o `.py` que ele executa) | `app.py` |
| 4 | **`requirements.txt`** | `streamlit>=1.40` · `requests>=2.28` |

> "Streamlit Community Cloud runs using GitHub." [Richards, p174]

## 1 · Antes de tudo: conferir o ambiente

```bash
python ../../../../bloco-03/aula-05/aula-05-step-by-step/verificar_ambiente.py
```

O script checa versão do Python, dependências declaradas × instaladas, presença do `.gitignore`,
segredos versionados por engano e caminhos frágeis. **Só siga com tudo em ✅.**

## 2 · Ambiente reprodutível

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py          # confirme que roda antes de publicar
```

**Regra:** instalou biblioteca nova → acrescenta ao `requirements.txt` **na mesma hora**. Esquecer isso
é a causa nº 1 de deploy quebrado (`ModuleNotFoundError`).

## 3 · Repositório

O `.gitignore` **já existe** neste projeto. Confirme que ele está no lugar **antes** do primeiro
`git add` — o `.gitignore` não remove o que já foi rastreado.

```bash
git init -b main
git status                    # confira o que será incluído: NÃO pode aparecer .venv/ nem secrets.toml
git add .
git commit -m "Painel ODS v3: projeto pronto para publicação"
```

No site do GitHub: **New repository** → nome `painel-ods-brasil` → **Create repository**
[Richards, p180–181]. Depois [Richards, p183]:

```bash
git remote add origin https://github.com/SEU_USUARIO/painel-ods-brasil
git push -u origin main
```

## 4 · Deploy

1. Acesse **share.streamlit.io** e entre com a conta do GitHub
   (cadastro gratuito: `https://share.streamlit.io/signup` [Richards, p173]).
2. **New app** → aponte **repositório**, **branch** (`main`) e **arquivo principal** (`app.py`)
   [Richards, p185].
3. **Deploy.** O serviço instala o `requirements.txt`, executa o `app.py` e devolve **uma URL própria**.

## 5 · Atualizar o app publicado

> "Whenever we make changes to the GitHub repository, we will see such changes reflected in the app."
> [Richards, p185]

```bash
git add .
git commit -m "descreve o que mudou"
git push
```

Recarregue a URL. *"It may take a couple of minutes for the app to reload!"* [Richards, p187]
O rodapé do app mostra a `VERSAO` — use-o para confirmar, olhando a página, que o `push` chegou lá.

## 6 · Quando quebra: os logs

**Manage app** (canto inferior direito do app publicado) → logs; dali também dá para **reiniciar**,
**excluir** e **baixar os logs** [Richards, p188].

| O log diz | Causa | Correção |
|-----------|-------|----------|
| `ModuleNotFoundError: No module named 'X'` | dependência não declarada | acrescentar ao `requirements.txt` → `push` |
| `FileNotFoundError: ... .json` | caminho relativo ao diretório de execução | ancorar em `Path(__file__)` (já feito em `src/data_access.py`) |
| `Error installing requirements` | versão inexistente ou erro de digitação | corrigir a linha → `push` |
| App carrega mas mostra "cache local" | a API do IBGE não respondeu | esperado: é o *fallback*. Confira em `Manage app` se há erro de rede |

## 7 · Segredos

O repositório é **público** por padrão: *"the default in Streamlit Community Cloud is to use public
GitHub repositories with entirely public code, data, and models"* [Richards, p188].

| Onde | Arquivo/lugar | Vai para o Git? |
|------|---------------|-----------------|
| Local | `.streamlit/secrets.toml` | ❌ **nunca** (está no `.gitignore`) |
| Repositório | `.streamlit/secrets.toml.example` (chaves em branco) | ✅ sim |
| No ar | **Edit secrets** no painel do Community Cloud [Richards, p190] | — |

No código, lê-se com `st.secrets["nome"]` [Richards, p191].

> ⚠️ Commitou um segredo e apagou depois? **O histórico guarda.** A chave precisa ser **revogada e
> trocada** — apagar o arquivo não basta.

## 8 · Limites do plano gratuito

- **Memória: de 690 MB a 2,7 GB por app; CPU: de 0,078 a 2 núcleos** (documentação do Streamlit,
  limites publicados em fev/2024, "sujeitos a mudança"). O livro, de 2023, fala em 1 GB [Richards, p267].
- Repositório público por padrão; o app publicado ganha automaticamente um botão para ver o código no
  GitHub e um botão **Share** para o dono [Richards, p365].
- Apps **sem acesso por 12 horas** hibernam e reacordam no primeiro acesso (documentação do Streamlit).

## Alternativas (para saber que existem)

| Via | Custo | Observação |
|-----|-------|------------|
| **Streamlit Community Cloud** | grátis | "easiest and preferred method for most Streamlit users" [Richards, p172] |
| AWS / Heroku | pago | controle de recursos; cap. 8 do livro |
| Hugging Face Spaces | grátis | forte para apps de ML; cap. 8/11 do livro |

## 9 · E quando o app vira multipáginas? (v7 · Aula 9)

**Nada muda no deploy.** O **arquivo principal continua sendo `app.py`** — agora um roteador — e o
contrato de quatro itens é o mesmo. Três conferências antes do `push`:

| Conferir | Por quê |
|----------|---------|
| a pasta `paginas/` e o `comum.py` foram **commitados** (`git status`) | página que não subiu = `StreamlitPageNotFoundError` no ar |
| os caminhos em `st.Page("paginas/…")` batem com os nomes dos arquivos, **inclusive maiúsculas** | o servidor do Community Cloud é Linux: `Paginas/` ≠ `paginas/` |
| nenhuma dependência nova | `st.navigation` e `st.Page` vêm com o Streamlit (≥ 1.36) |

## 10 · E o Selenium? (v8 · Aula 10)

**Na v8, ele não vai para o Community Cloud — por escolha.** A coleta roda na sua máquina
(`python -m src.coleta_dinamica`), grava `data/processed/desmatamento_prodes.csv`, e é esse CSV que sobe
com o `git push`. O app só lê.

| Arquivo | Quem instala | Tem Selenium? |
|---------|--------------|:-------------:|
| `requirements.txt` | o Community Cloud (e você, para rodar o app) | ❌ |
| `requirements-coleta.txt` | só você, para coletar (`-r requirements.txt` + `selenium`) | ✅ |

Antes do push: confira que `data/processed/desmatamento_*.{csv,json}` estão no `git status` — e que
`data/raw/prodes_renderizado.html` **não** está (conteúdo de terceiros, regenerável).

### 10.1 E se eu QUISER o Selenium no app publicado? (aprofundamento)

**Dá.** O Community Cloud roda em Debian e **não traz navegador**, mas instala pacotes do sistema
listados num `packages.txt` **na raiz** do repositório:

```text
chromium
chromium-driver
```

(uma linha por pacote, **sem comentários** — cada linha vai para o instalador do sistema.) E o
`selenium` passa a ir no **`requirements.txt`**, porque agora o app o importa.

No código, três escolhas tornam isso viável — o exemplo completo e testado está em
`../../../../bloco-05/aula-10/aula-10-step-by-step/passo06_selenium_no_app/app.py`:

| Escolha | Por quê |
|---------|---------|
| `@st.cache_data(ttl=3600)` **na coleta** | o cache é compartilhado: o navegador abre **no máximo uma vez por hora, para todos**. Sem isso, um Chrome por rerun |
| navegador **aberto e fechado** dentro da função cacheada (`with`) | em `@st.cache_resource` ele ficaria aberto para sempre e seria dividido entre sessões |
| a **falha também vai para o cache** (devolvida, não levantada) | exceção não é cacheada: uma coleta que falha abriria um Chrome novo a cada rerun |

E, no servidor, `--headless=new --no-sandbox --disable-dev-shm-usage` e o driver do sistema
(`Service(shutil.which("chromedriver"))`), pareado com o Chromium que o `packages.txt` instalou.

**Verificado localmente** (23/09/2026): 1ª coleta **6,1 s**, reruns **0 ms**, nenhum navegador aberto
depois; falha servida do cache em **0,01 s**. Um Chrome sem janela ocupou **380 MB vazio e ~640 MB**
com o PRODES carregado.

**Não verificado por nós no Community Cloud.** O `packages.txt` é documentado pelo Streamlit; `chromium`
+ `chromium-driver` vêm de projetos de referência e do fórum — onde também há relatos de
`chromium-driver` não encontrado (jun/2025) e de navegador e driver em versões diferentes.

**O preço, resumido:** 380–640 MB por navegador num app de 690 MB–2,7 GB; *build* que depende de
pacotes do sistema; o servidor fora do Brasil (há sites que bloqueiam por localização — não testamos
o INPE); e, depois de 12 h de hibernação, o primeiro visitante paga a coleta. **Vale quando o dado
precisa ser mais fresco que a última coleta.** Para uma taxa anual, não vale — por isso a v8 coleta à
parte.

## 11 · E a API? (v9 · Aula 11)

**A API não vai para o Community Cloud.** Ele roda o **arquivo principal com o Streamlit** — o contrato
de quatro itens da seção 0 — e é esse app que fica acessível pela URL. Uma API FastAPI precisa de um
servidor próprio (o `uvicorn`), e o Community Cloud não o publica. Na v9 a API roda **na sua máquina**,
noutro terminal:

```bash
pip install -r requirements-api.txt      # -r requirements.txt + fastapi + uvicorn
uvicorn api.main:app --reload            # da pasta painel_ods_brasil/  ->  http://127.0.0.1:8000/docs
```

| Arquivo | Quem instala | Tem FastAPI? |
|---------|--------------|:------------:|
| `requirements.txt` | o Community Cloud (e você, para rodar o app) | ❌ |
| `requirements-api.txt` | só você, para rodar a API (`-r requirements.txt` + `fastapi` + `uvicorn`) | ✅ |

**O `git push` leva a pasta `api/` junto** — e não faz mal nenhum: o Community Cloud não a importa. Ela
fica no repositório porque faz parte do projeto (o TP3 pede a aplicação **integrada** com a API), e
quem clonar o repositório roda as duas coisas.

**E para publicar a API?** Seria outro serviço, que hospede um servidor Python (o livro do FastAPI
empacota a aplicação com Docker e aponta plataformas de nuvem [Adeshina, p192–203]). **Fora do escopo
do TP3 — e não verificado por nós.** O TP4 integra um LLM **local** à mesma API, rodando na sua
máquina: o padrão da Etapa 6 continua valendo lá.
