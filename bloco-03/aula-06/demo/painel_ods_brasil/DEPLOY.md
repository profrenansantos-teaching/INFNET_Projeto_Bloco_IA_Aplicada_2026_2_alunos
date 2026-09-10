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
python ../../aula-05-step-by-step/verificar_ambiente.py
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

- **1 GB de RAM por app** [Richards, p267].
- Repositório público por padrão; o app publicado ganha automaticamente um botão para ver o código no
  GitHub e um botão **Share** para o dono [Richards, p365].
- Apps sem acesso por muito tempo entram em hibernação e reacordam no primeiro acesso.

## Alternativas (para saber que existem)

| Via | Custo | Observação |
|-----|-------|------------|
| **Streamlit Community Cloud** | grátis | "easiest and preferred method for most Streamlit users" [Richards, p172] |
| AWS / Heroku | pago | controle de recursos; cap. 8 do livro |
| Hugging Face Spaces | grátis | forte para apps de ML; cap. 8/11 do livro |
