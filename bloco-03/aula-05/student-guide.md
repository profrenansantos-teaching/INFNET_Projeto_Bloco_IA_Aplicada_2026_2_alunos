# Aula 5 — Material de Apoio do Aluno
### Do meu computador para a internet · PB Etapa 3 · subcompetência 2.1

Hoje o Painel ODS deixa de existir só na sua máquina: ele ganha um **ambiente declarado**, um
**repositório** e uma **URL que qualquer pessoa abre**. 🌱→🌍

> **Padrão do bloco:** Python puro (**sem pandas**); código **guiado**; **IA como copiloto** (usar,
> desde que você entenda e saiba explicar). Traga o projeto das Aulas 1–2.

## Antes da aula — o que fazer e o que ler (≈ 40 min)

**Fazer (obrigatório — sem isso a aula rende metade):**

- [ ] Criar conta gratuita no **GitHub** — `https://www.github.com`
- [ ] Criar conta gratuita no **Streamlit Community Cloud** — `https://share.streamlit.io/signup`
- [ ] Ter o **Git instalado**: `git --version` no terminal deve responder alguma coisa
- [ ] Ter o projeto da Aula 2 rodando: `streamlit run app.py`

**Ler:**

| Leitura | Por quê | Foque em |
|---------|---------|----------|
| RICHARDS, cap. 5 ("Deploying Streamlit with Streamlit Community Cloud") | é a fonte da aula | por que publicar importa (p172); `requirements.txt` (p183); o ciclo `push` → app atualizado (p185); Secrets (p188–191) |
| Mini-deck **Git e GitHub, o essencial** (Aula 2) | recap rápido | as quatro áreas do Git; `origin`; `main` |

**Perguntas-guia:** (1) Por que o Community Cloud precisa do GitHub? (2) Por que o `.venv/` **não** vai
para o repositório, mas o `requirements.txt` vai? (3) O que acontece com o app publicado quando você dá
`git push`? (4) Por que um segredo commitado continua sendo um problema depois de apagado?

## Em aula — o arco

Recap (v2) → **o link que não existe** → **ambiente reprodutível** → **repositório no GitHub** (guiado)
→ **deploy no Community Cloud + logs + segredos** (guiado) → princípios e fecho.

## Conceitos-chave

### 1. Um programa não é só o seu código

```
programa = código + Python + bibliotecas + versões + dados + configuração
```

Quando você diz "funciona", você diz "funciona **nesta** combinação". **Reprodutibilidade** é
conseguir recriar essa combinação a partir do que está **declarado no repositório**.

### 2. As três peças do ambiente

| Peça | Responde a | Vai para o Git? |
|------|-----------|-----------------|
| **`venv`** | *onde* as bibliotecas deste projeto moram | ❌ **não** — é reconstruível |
| **`requirements.txt`** | *quais* bibliotecas e em que versão | ✅ **sim** — é a receita |
| **`.gitignore`** | *o que não* entra no repositório | ✅ sim |

> A regra que resolve 90% das dúvidas: **versiona-se o que o app precisa para funcionar; não se
> versiona o que é reconstruível nem o que é secreto.**

### 3. O contrato do Community Cloud

Ele precisa de **quatro** coisas — e toda falha de deploy é a falta de uma delas:
**repositório** · **branch** · **arquivo principal** (`app.py`) · **`requirements.txt`**.

E a condição de entrada: *"Streamlit Community Cloud runs using GitHub"* [Richards, p174].

### 4. `git push` = publicar

> "Whenever we make changes to the GitHub repository, we will see such changes reflected in the app."
> [Richards, p185]

**O repositório é a fonte da verdade do que está no ar.** Se não está commitado, não está no ar.

### 5. Segredo nunca é código

O padrão do Community Cloud é **repositório público** [Richards, p188]. Tudo que você commita está
publicado — e **apagar depois não resolve, porque o histórico guarda**. A chave tem de ser **revogada
e trocada**.

## Cola de comandos

```bash
# --- ambiente ---
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt
streamlit run app.py

# --- identificar-se no Git (uma vez por máquina) ---
git config --global user.name  "Seu Nome"
git config --global user.email seu@email

# --- repositório (o .gitignore PRIMEIRO!) ---
git init -b main
git status                          # confira o que vai entrar
git add .
git commit -m "Painel ODS v3: pronto para publicar"

# --- conectar ao GitHub e enviar ---
git remote add origin https://github.com/SEU_USUARIO/painel-ods-brasil
git push -u origin main

# --- o ciclo, dali em diante ---
git add . && git commit -m "o que mudou" && git push
```

```gitignore
# .gitignore mínimo
.venv/
__pycache__/
*.py[cod]
.streamlit/secrets.toml
.env
```

```python
# caminho que sobrevive à mudança de máquina
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent      # ancorado no ARQUIVO
CACHE = BASE / "data" / "sample" / "ufs_cache.json"

# segredo fora do código
if st.text_input("Senha", type="password") != st.secrets["senha"]:
    st.stop()
```

## Diagnóstico automático

```bash
python aula-05-step-by-step/verificar_ambiente.py CAMINHO/DO/SEU/PROJETO
```

Checa ambiente, dependências declaradas × importadas, `.gitignore`, segredos rastreados, caminhos
frágeis e estado do repositório. Rode **antes** de publicar.

## Quando o deploy quebrar (vai quebrar — faz parte)

**Manage app** → logs. Leia a **última linha** do traceback antes de mexer em qualquer coisa.

| O log diz | Causa | Correção |
|-----------|-------|----------|
| `ModuleNotFoundError: No module named 'X'` | dependência não declarada | acrescentar ao `requirements.txt` → `push` |
| `FileNotFoundError: ... .json` | caminho relativo ao diretório de execução | ancorar em `Path(__file__)` |
| `Error installing requirements` | versão inexistente / erro de digitação | corrigir a linha → `push` |

## IA como copiloto

Boa pergunta para a IA: *"explique linha a linha o que este `.gitignore` protege e por quê"*.
Má prática: pedir "faça meu deploy" e colar o resultado sem entender — quando quebrar (e vai), você
precisa **ler o log** e saber o que cada um dos quatro itens do contrato significa.

## Checklist do TP2 (parte desta aula)

- [ ] `.gitignore` criado **antes** do primeiro `git add`
- [ ] `requirements.txt` lista tudo que o app importa
- [ ] Repositório no GitHub, com **mais de um** commit
- [ ] App publicado no Community Cloud, com URL que abre
- [ ] Uma alteração feita **depois** do deploy, com `push`, visível no app no ar
- [ ] Nenhum segredo, `.venv/` ou `__pycache__/` no repositório

## Autoteste

1. Por que o `.venv/` não vai para o repositório, mas o `requirements.txt` vai?
2. Quais são as quatro coisas que o Community Cloud precisa para publicar o seu app?
3. O app roda no laptop e falha no ar com `ModuleNotFoundError`. O que aconteceu?
4. Qual a diferença entre `Path(__file__)` e um caminho relativo como `"data/x.json"`?
5. Commitei uma chave de API e apaguei no commit seguinte. Estou seguro?
6. O que é preciso fazer para que uma alteração no código apareça no app publicado?

<details><summary>Respostas</summary>

1. Porque o `.venv/` é **reconstruível** a partir do `requirements.txt` — e contém binários compilados
   para **um** sistema operacional, inúteis no servidor. O `requirements.txt` é a **receita**: sem ele,
   o servidor não sabe o que instalar.
2. **Repositório** (público por padrão), **branch**, **arquivo principal** (`app.py`) e
   **`requirements.txt`**.
3. A biblioteca estava instalada no seu ambiente local mas **não declarada** no `requirements.txt`. O
   servidor instala **exatamente** o que está declarado [Richards, p183]. É a definição operacional de
   "funciona na minha máquina".
4. `Path(__file__)` aponta para **onde o arquivo `.py` está**; um caminho relativo é resolvido a partir
   **do diretório de onde o comando foi chamado**. Localmente costumam coincidir; no servidor, não.
5. **Não.** O histórico do Git guarda a versão anterior. É preciso **revogar e trocar** a chave.
6. `git add` → `git commit` → **`git push`**. O Community Cloud reconstrói sozinho a partir do
   repositório [Richards, p185]; leva um ou dois minutos.

</details>
