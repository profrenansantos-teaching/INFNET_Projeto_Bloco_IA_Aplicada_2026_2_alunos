# Escolha do modelo de linguagem — Painel ODS Brasil (v13)

> **TP4, item 1** — *"Justifique a escolha do modelo, detalhando os critérios de desempenho, custo computacional local
> e acessibilidade que levaram à sua decisão."* Este documento é a justificativa; a página **🧪 Escolha do modelo** do
> painel mostra os mesmos números, lidos de `data/analisador/avaliacao.json`.

## 1. A tarefa

O analisador recebe um **relato de campo** — texto livre, em português do Brasil, de 15 a 2.000 caracteres, escrito por
quem viu o problema — e sugere **uma de seis categorias**: queimada, desmatamento, enchente, seca, poluição, lixo.
É uma tarefa de **classificação**.

Até a v13, quem classifica é um **motor de regras** (palavras-chave, Aula 13). Ele **acerta 13 dos 30** relatos do banco de
provas e, nos outros 17, **não responde**: sem uma palavra da lista, devolve `null`. Ele nunca erra — e quase nunca
ajuda quando o relato foge das palavras esperadas (*"a água do arroio subiu e alcançou as casas"*).

## 2. O que "adequado" quer dizer, neste projeto

| Requisito | Por quê |
|-----------|---------|
| Entende **português do Brasil** informal | os relatos são escritos por moradores, não por técnicos |
| Roda **na CPU** da máquina da API, **sem nuvem** | o TP4 pede execução local; e quem roda a API (um colega, a prefeitura) pode não ter placa de vídeo — por isso tudo foi medido **só na CPU** |
| Responde em **poucos segundos** | quem pede espera na página; o painel desiste em 30 s (Aula 14) |
| **Baixa sem conta e sem token** | o repositório é público: qualquer colega clona e roda |
| Licença que permite o uso | o projeto é aberto e pode ser reaproveitado |
| **Acerta mais que as regras** | senão, não há motivo para trocar |

**A máquina da medida:** Intel Core i5-12400F (6 núcleos, 12 *threads*), 32 GB de RAM, Windows 11, PyTorch 2.14 (CPU),
Transformers 5.21. Os tempos mudam noutra máquina — e por isso a bancada existe.

## 3. Os candidatos — e os que a ficha já descartou

As fichas vêm de `python -m src.ficha_modelo` (o Hub, antes de baixar):

| Modelo | Arquitetura | Tarefa no Hub | Licença | Gated | Parâmetros | Download |
|--------|-------------|---------------|---------|:-----:|-----------:|---------:|
| `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` | encoder (BERT) | zero-shot | MIT | não | 107 mi | 428 MB |
| `facebook/bart-large-mnli` | encoder-decoder | zero-shot | MIT | não | 407 mi | 1,6 GB |
| `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | encoder (BERT) | zero-shot | MIT | não | 279 mi | 558 MB |
| `HuggingFaceTB/SmolLM2-360M-Instruct` | decoder (GPT) | geração | Apache 2.0 | não | 362 mi | 724 MB |
| `Qwen/Qwen2.5-0.5B-Instruct` | decoder (GPT) | geração | Apache 2.0 | não | 494 mi | 988 MB |
| `Qwen/Qwen3-0.6B` | decoder (GPT) | geração | Apache 2.0 | não | 752 mi | 1,5 GB |
| `Qwen/Qwen2.5-1.5B-Instruct` | decoder (GPT) | geração | Apache 2.0 | não | 1.544 mi | 3,1 GB |
| `Qwen/Qwen3-1.7B` | decoder (GPT) | geração | Apache 2.0 | não | 2.032 mi | 4,1 GB |

**Descartados pela ficha, sem baixar:**
- `google/gemma-3-1b-it` e `meta-llama/Llama-3.2-1B-Instruct` — **gated**: pedem conta, aceite da licença e token. Sem
  isso, `OSError: You are trying to access a gated repo… 401`. Quebra o requisito "baixa sem conta".
- `neuralmind/bert-base-portuguese-cased` (BERTimbau) — é português, mas a tarefa é `fill-mask`: não foi treinado para
  classificar nem para seguir instruções. Exigiria treinar (fine-tuning) com relatos rotulados que não temos.
- `Qwen/Qwen2.5-3B-Instruct` — licença `other` (não Apache, como os irmãos menores) e ~12 GB em float32.

**Mantidos apesar da ficha:** o cartão do Qwen2.5 declara só `en`, e o do MiniLM lista 15 línguas sem o português. O
cartão é pista, não veredito — os dois foram **medidos**.

## 4. As medidas — no nosso dado, na nossa máquina

`python -m src.bancada <modelo> --tarefa <zero-shot|gerar>`, no **banco de provas** (`data/analisador/banco_de_provas.csv`:
30 relatos fictícios, 5 por categoria, rotulados à mão). Segundos = mediana por relato, depois de um aquecimento.

| Motor | Tipo | Prompt | Acertos | s por relato | Pesos na memória |
|-------|------|--------|--------:|-------------:|-----------------:|
| regras (v11) | — | — | 13/30 (17 sem resposta) | 0,0 | — |
| MiniLM-L6 (zero-shot) | float32 | — | 7/30 | 0,05 | 0,4 GB |
| BART-large-MNLI (zero-shot) | float32 | — | 9/30 | 1,05 | 1,6 GB |
| mDeBERTa (zero-shot) | float16 (como foi salvo) | — | 18/30 | **4,5** | 0,6 GB |
| mDeBERTa (zero-shot) | float32 | — | 18/30 | 0,57 | 1,1 GB |
| SmolLM2-360M (gera) | float32 | definições | 4/30 (24 sem resposta) | 1,32 | 1,4 GB |
| Qwen2.5-0.5B (gera) | float32 | simples | 4/30 | 0,51 | 2,0 GB |
| Qwen2.5-0.5B (gera) | float32 | definições | 11/30 | 0,79 | 2,0 GB |
| Qwen3-0.6B (gera) | float32 | definições | 20/30 | 1,06 | 2,4 GB |
| Qwen2.5-1.5B (gera) | float32 | simples | 23/30 | 1,42 | 6,2 GB |
| **Qwen2.5-1.5B (gera)** | **float32** | **definições** | **27/30** | **2,8** | **6,2 GB** |
| Qwen3-1.7B (gera) | float32 | definições | 27/30 | 2,97 | 6,9 GB |
| Qwen2.5-1.5B (gera) | bfloat16 (como foi salvo) | definições | 27/30 | **12,9** | 3,1 GB |

O que a tabela ensinou:
- **Popular não é adequado.** O BART-large-MNLI é o zero-shot mais baixado do Hub — e é inglês: 9 de 30.
- **"Multilíngue" não quer dizer português.** O MiniLM: 7 de 30 — a lista do cartão já avisava.
- **O tipo dos números é custo.** O mDeBERTa salvo em float16 levava 4,5 s por relato na nossa CPU; em float32, 0,57 s,
  com o mesmo acerto e o dobro de memória.
- **Um LLM pequeno chuta com convicção.** O Qwen2.5-0.5B respondeu "Desmatamento" a quase tudo.
- **O prompt pesa.** As definições das categorias levaram o Qwen2.5-1.5B de 23 para 27, e o Qwen2.5-0.5B de 4 para 11.
- **Maior e mais novo não é sempre melhor.** O Qwen3-1.7B acertou os mesmos 27 — com mais memória (6,9 GB) e um pouco mais devagar (2,97 s).

## 5. A decisão: `Qwen/Qwen2.5-1.5B-Instruct`, em float32, na CPU, com as definições no prompt

| Critério do TP4 | O que pesou |
|-----------------|-------------|
| **Desempenho** | **27 de 30** no banco de provas — as regras, 13; o melhor zero-shot, 18. É um modelo de **conversa** (decoder, família GPT), treinado para seguir instruções: a tarefa vem descrita no prompt, sem treinar nada. Em português, apesar do cartão. |
| **Custo computacional local** | **3,1 GB** para baixar, uma vez; **6,2 GB** de pesos na memória (float32); **2,8 s** por relato na CPU; ~16 s para carregar — uma vez, quando a API sobe. Cabe numa máquina de 16 GB com o painel aberto. |
| **Acessibilidade local** | **Apache 2.0**, não é gated: baixa sem conta. Roda com `transformers` + `torch` na CPU, sem placa de vídeo. Uma vez baixado, funciona **sem internet**. |

## 6. O que pesou contra — e o plano B

- **A memória.** 6,2 GB de pesos não cabem com folga num notebook de 8 GB. Plano B, medido:
  - o **mesmo modelo em bfloat16** — metade da memória (3,1 GB) e o mesmo acerto (27 de 30), mas **12,9 s** por
    relato **na nossa CPU**, que não faz conta em bfloat16 nativamente. Numa CPU que faz, meça de novo;
  - o **Qwen3-0.6B** — 20 de 30, 1,1 s, 2,4 GB.
- **Onde ele erra** (3 de 30): o nº 2 (*"o nível do rio baixou… o barco não chega ao porto"* — seca; ele diz enchente),
  o nº 20 (*"o gado morrendo de sede, a represa sumiu"* — seca; ele diz enchente) e o nº 30 (*"despejando material de
  demolição no mangue"* — lixo; ele diz desmatamento). O nº 2 as regras acertam.
- **Ele sempre responde.** As regras calam quando não sabem; o modelo aposta. Por isso a página Analisador avisa que a
  sugestão é para conferir.

## 7. Limites desta avaliação

- **30 relatos é pouco**: cada erro vale 3,3 pontos. A diferença entre 27 e 23 é real; entre 20 e 18, talvez não.
- **Os relatos são fictícios e foram escritos por nós**, que conhecíamos as categorias — relatos reais serão mais
  variados (e terão erros de digitação).
- **Um rótulo por relato, dado por uma pessoa.** Alguns são ambíguos: a chaminé que solta fumaça cinza (nº 25) é
  poluição ou queimada? O entulho no mangue (nº 30) é lixo ou desmatamento?
- **Uma máquina só.** Os segundos e a memória valem para ela.
- **Reavaliar** quando chegarem relatos reais: rotular uma amostra, acrescentar ao banco de provas, rodar a bancada.
