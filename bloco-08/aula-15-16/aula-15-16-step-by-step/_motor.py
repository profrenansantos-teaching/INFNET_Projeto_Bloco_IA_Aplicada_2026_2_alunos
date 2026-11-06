"""
O motor dos passos da Aula 16 — um modelo pequeno, para os passos rodarem em qualquer máquina. (Não é um passo.)

O demo (v14) usa o Qwen2.5-1.5B, o escolhido na Aula 15 (~8 s para carregar, ~6,5 GB). Os passos usam o
irmão menor, o Qwen2.5-0.5B (~1 GB no disco, carrega em poucos segundos): o assunto da Aula 16 não é
acertar mais — é ONDE e COMO o modelo entra na API. As duas funções são as do demo:

  carregar()    o modelo do disco para a memória (local_files_only=True: nunca baixa nada);
  classificar() a probabilidade de cada categoria como próxima palavra → a categoria e a confiança.
E uma terceira, só para o passo 5:
  escrever()    o modelo ESCREVE a resposta (como na bancada da Aula 15) — texto livre.

Baixe o modelo antes, com internet:  python passo00_baixar.py   (nesta pasta)
"""

import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELO = "Qwen/Qwen2.5-0.5B-Instruct"
CATEGORIAS = ["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo"]
INSTRUCOES = (
    "Você classifica relatos de problemas ambientais enviados por moradores. "
    f"Categorias possíveis: {', '.join(CATEGORIAS)}. Responda apenas com o nome de UMA categoria, sem explicar."
)


def carregar(nome: str = MODELO) -> dict:
    relogio = time.perf_counter()
    tokenizador = AutoTokenizer.from_pretrained(nome, local_files_only=True)
    modelo = AutoModelForCausalLM.from_pretrained(nome, local_files_only=True, dtype=torch.float32)
    modelo.eval()
    tokens = [tokenizador.encode(c, add_special_tokens=False)[0] for c in CATEGORIAS]
    print(f"[motor] {nome} carregado em {time.perf_counter() - relogio:.1f} s", flush=True)
    return {"nome": nome, "tokenizador": tokenizador, "modelo": modelo, "tokens": tokens}


def _entrada(texto: str, motor: dict):
    mensagens = [{"role": "system", "content": INSTRUCOES}, {"role": "user", "content": f"Relato: {texto}\nCategoria:"}]
    return motor["tokenizador"].apply_chat_template(mensagens, add_generation_prompt=True,
                                                    return_tensors="pt", return_dict=True)


def classificar(texto: str, motor: dict) -> dict:
    with torch.no_grad():
        notas = motor["modelo"](**_entrada(texto, motor)).logits[0, -1, motor["tokens"]]
    probabilidades = torch.softmax(notas, dim=0).tolist()
    melhor = max(range(len(CATEGORIAS)), key=lambda i: probabilidades[i])
    return {"categoria": CATEGORIAS[melhor], "confianca": round(probabilidades[melhor], 2)}


def escrever(texto: str, motor: dict) -> str:
    entrada = _entrada(texto, motor)
    with torch.no_grad():
        saida = motor["modelo"].generate(**entrada, max_new_tokens=10, do_sample=False)
    novos = saida[0, entrada["input_ids"].shape[1]:]          # só o que o modelo escreveu
    return motor["tokenizador"].decode(novos, skip_special_tokens=True).strip()
