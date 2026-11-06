# Aula 15 — Material de apoio do aluno
### Quem escolhe, mede · PB Etapa 8 · subcompetência 4.3 · **TP4, item 1**

> **O que você leva desta aula:** um **método** para escolher o modelo de linguagem do seu projeto — e o **documento**
> que o TP4 pede para justificá-lo. Os passos estão em `../aula-15-16/aula-15-16-step-by-step/`; o exemplo completo, na v13
> (`demo/painel_ods_brasil/`: `src/ficha_modelo.py`, `src/bancada.py`, `docs/escolha_do_modelo.md`).
>
> **Antes de tudo — em casa, com internet:** `pip install -r requirements-api.txt` (no **Linux**, o `torch` de CPU antes:
> `pip install torch --index-url https://download.pytorch.org/whl/cpu`) e `python passo00_baixar.py` (~1,5 GB).

---

## 1. A pergunta não tem resposta pronta

> *"The truth is that there is not a straightforward answer to this question."* [Alto, p81]

Até aqui, quase toda escolha do curso tinha uma resposta na documentação. **A do modelo não tem.** Depende da tarefa, do
seu dado, da sua máquina e de quem vai usar. O que existe é um **método**:

1. **Declarar os requisitos** — a língua, a máquina, o tempo aceitável, quem vai instalar.
2. **Ler a ficha** dos candidatos — e descartar o inacessível **antes** de baixar.
3. **Medir** no **seu** dado, na **sua** máquina — acertos, segundos, memória.
4. **Decidir** — e escrever **o que pesou contra** (o plano B, os limites).

## 2. Um modelo do Hub em três linhas

```python
from transformers import pipeline

classificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
r = classificador("A água do arroio subiu durante a noite e alcançou as casas da rua de baixo.",
                  candidate_labels=["queimada", "desmatamento", "enchente", "seca", "poluição", "lixo"],
                  hypothesis_template="Este relato é sobre {}.")
print(r["labels"][0], r["scores"][0])          # enchente 0.80
```

- Na **primeira** vez, o `pipeline` **baixa** o modelo para a pasta de cache do Hugging Face (no Windows,
  `C:\Users\<você>\.cache\huggingface\hub`). Nas outras, lê do disco — **sem internet**.
- O modelo são **arquivos**: os pesos (`.safetensors`), a configuração e o tokenizador. **Não vão para o Git.**

## 3. As três famílias — o "GPT, BERT, T5" do TP4

| Família | Como trabalha | Bom para | Exemplos |
|---------|---------------|----------|----------|
| **encoder** (BERT) | lê o texto inteiro e dá uma **nota** | classificar, sentimento, perguntas e respostas | mDeBERTa, BERTimbau |
| **decoder** (GPT) | **escreve** a próxima palavra, uma de cada vez | conversar, seguir instruções, gerar texto | Qwen, Llama, Gemma |
| **encoder-decoder** (T5) | lê um texto e escreve **outro** | traduzir, resumir | T5, BART |

[Alto, p36] · [Parandeh, p96–97]. **Classificar dá para fazer com as três** — o encoder dá nota a cada categoria; o
decoder recebe a tarefa no **prompt** e responde. Qual acerta mais no **seu** dado, só medindo.

## 4. A ficha: o que dá para saber antes de baixar

```bash
python -m src.ficha_modelo Qwen/Qwen2.5-1.5B-Instruct google/gemma-3-1b-it     # (na v13; precisa de internet)
```

| Na ficha | Critério do TP4 | O que procurar |
|----------|-----------------|----------------|
| **licença** | acessibilidade | MIT, Apache 2.0 — tranquilas; `other`, licenças próprias — **leia** antes de usar |
| ***gated*** | acessibilidade | `manual`/`auto` = pede conta + aceitar a licença + token. Num projeto público, **todo mundo** que clonar paga isso |
| **tarefa** (`pipeline_tag`) | desempenho (pista) | `fill-mask` não classifica nem conversa; `zero-shot-classification`, `text-generation` |
| **línguas** do cartão | desempenho (pista) | tem `pt`? — mas o cartão pode estar **incompleto** (o do Qwen2.5 diz só `en`, e ele vai bem em português) |
| **parâmetros** | custo (estimado) | **× 4 bytes** = a memória em float32. 1,5 bilhão × 4 ≈ **6 GB** |

**O que medimos — e a ficha previa:** o zero-shot **mais baixado do Hub** (BART) é inglês: **9 de 30**. O MiniLM
"multilingual" lista 15 línguas, sem o português: **7 de 30**. O Gemma é *gated*: `OSError … gated repo … 401`.

> **O cartão é pista; o banco de provas é veredito.** A ficha descarta o **inacessível**; o que é só pista vai para a
> medida.

## 5. O custo de verdade — memória **e** tempo

**O tipo dos números muda os dois.** O Transformers 5 carrega o modelo no tipo em que ele foi **salvo**:

| Modelo | Tipo | Memória dos pesos | s por relato (nossa CPU) |
|--------|------|------------------:|-------------------------:|
| mDeBERTa | float16 (como foi salvo) | 558 MB | **4,74** |
| mDeBERTa | **float32** | 1.115 MB | **0,61** |
| Qwen2.5-1.5B | bfloat16 (como foi salvo) | 3,1 GB | **12,9** |
| Qwen2.5-1.5B | **float32** | 6,2 GB | **2,8** |

O float16 e o bfloat16 economizam memória — e foram pensados para **placas de vídeo**. Numa CPU sem suporte nativo, a
conta é lenta. **Meça na sua máquina:**

```python
import torch
from transformers import pipeline
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", dtype=torch.float32)   # o tipo, explícito
memoria = sum(p.numel() * p.element_size() for p in pipe.model.parameters())                  # bytes dos pesos
```

> *"the larger the model, the more computation and memory it requires… which can result in higher latency"* [Alto, p81]

## 6. O banco de provas — o benchmark que importa é o seu

> *"you might want to use a model that is a top performer in one specific benchmark, rather than a top performer, on
> average, across all benchmarks."* [Alto, p82]

Um **banco de provas** é um punhado de exemplos **do seu projeto**, com a resposta certa escrita **antes** de rodar
qualquer modelo. O nosso: 30 relatos fictícios, 5 por categoria — metade com as palavras que as regras conhecem, metade
sem.

- **20 a 30 exemplos** já separam um modelo bom de um ruim. Não separam 18 de 20 — diga isso no documento.
- **Rotule antes**, para não "ajustar" o rótulo à resposta do modelo.
- Conte também **os que ficaram sem resposta**: errar e calar não são a mesma coisa (regras: 13 certos, 17 calados, 0
  errados; mDeBERTa: 18 certos, 12 errados).

## 7. O LLM que escreve — e o prompt que pesa

Um decoder **escreve** a resposta. Um pequeno **chuta com convicção**: o Qwen2.5-0.5B respondeu "Desmatamento" a quase
tudo, "Chuveiro" a um relato de chuva, "chama-vaquinha" a um de chaminé — **4 de 30**. Escrever no prompt **o que cada
categoria quer dizer**:

```
Você classifica relatos de problemas ambientais enviados por moradores de cidades brasileiras.
Categorias:
- queimada: fogo, fumaça, incêndio em mata, pasto ou plantação
- enchente: água subindo, rua ou casa alagada, rio ou córrego transbordando
…
Responda apenas com o nome de UMA categoria, exatamente como escrito acima.
```

| Modelo | Prompt simples | Com as definições |
|--------|---------------:|------------------:|
| Qwen2.5-0.5B | 4 | 11 |
| Qwen2.5-1.5B | 23 | **27** |

## 8. O documento do TP4 — `docs/escolha_do_modelo.md`

O da v13 é o modelo. As seções que **não podem faltar**:

1. **A tarefa** — e o que existe hoje (a linha de base: as regras, 13 de 30).
2. **Os requisitos** — o que "adequado" quer dizer **no seu projeto**, e a máquina da medida.
3. **Os candidatos** — com a ficha; **os descartados e por quê**.
4. **As medidas** — a tabela da bancada (acertos, segundos, memória, tipo, prompt).
5. **A decisão** — por critério do TP4: desempenho, custo computacional local, acessibilidade local.
6. **O que pesou contra** — e o **plano B**, medido; **onde o escolhido erra**.
7. **Os limites** — tamanho do banco de provas, quem rotulou, uma máquina só.

## 9. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| Escolher pelos **downloads** | o mais baixado mede a tarefa (e a língua) dos outros — o BART: 9 de 30 |
| Escolher pelo **tamanho** ou pelo **mais novo** | o Qwen3-1.7B acertou o mesmo que o 1.5B, com mais memória |
| Escolher pelo nome **"LLM"** | um LLM pequeno escreveu "Chuveiro" |
| Testar em **três exemplos** | três acertos não distinguem nada |
| Deixar o **`dtype`** no automático | 4,5 s por relato onde cabiam 0,57 |
| Não anotar **a máquina** | os segundos de um não valem para outro |
| Esconder **onde erra** | quem usa precisa saber quando conferir |
| Um modelo ***gated*** num projeto público | cada pessoa que clonar precisa de conta e token |
| Os **pesos no Git** | gigabytes que não são seus — e o GitHub recusa arquivos acima de 100 MB |

## 10. O TP4, depois desta aula

- ✅ **Item 1** — o método e o documento. **Faça o do seu projeto**: o seu banco de provas, os seus candidatos, os seus
  números. O modelo do demo **não** é uma resposta para copiar — é um exemplo de justificativa.
- 🔜 **Item 2** — o modelo atrás de `POST /processar_texto`: **Aula 16**.
- ✅ Itens 3 e 4 — Aulas 13 e 14 (o contrato e os erros não mudam).
- Entrega: semana de **16–21/11/2026**.

## 11. Fontes

- ALTO, V. *Building LLM Powered Applications*. Packt, 2024 — cap. 3 (*Choosing an LLM for Your Application*). [K3]
- PARANDEH, A. *Building Generative AI Services with FastAPI*. O'Reilly, 2025 — cap. 3 (as variantes de transformer).
- Hugging Face — `pipeline`; `huggingface_hub` (`HfApi.model_info`); modelos *gated*.
- **O livro é de 2024**: os modelos que ele compara (GPT-4, Claude 2, LLaMA-2, Falcon, Mistral) estão datados, e ele
  não trata de CPU, memória, português nem de medir na própria máquina. O método desta aula preenche essa lacuna.
