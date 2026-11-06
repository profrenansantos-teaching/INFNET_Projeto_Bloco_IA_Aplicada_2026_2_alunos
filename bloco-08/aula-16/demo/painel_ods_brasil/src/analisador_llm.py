"""
O motor do POST /processar_texto — um modelo de linguagem LOCAL. Painel ODS Brasil, v14 (Aula 16).

O modelo é o que a Aula 15 escolheu, medindo (docs/escolha_do_modelo.md):
    Qwen/Qwen2.5-1.5B-Instruct — em float32, na CPU, com as definições das categorias no prompt.
Ele SUBSTITUI as regras (src/analisador.py, v11) atrás da mesma rota e do mesmo contrato: quem usa a
API não muda nada. As regras continuam no projeto como LINHA DE BASE da bancada.

COMO ELE CLASSIFICA — perguntando quanto o modelo aposta em cada categoria.
  Na bancada (Aula 15), o modelo ESCREVIA a resposta e procurávamos uma categoria no que ele
  escreveu. Para a API isso não basta:
    · o contrato promete uma categoria DA LISTA — e um LLM pequeno já escreveu "Chuveiro";
    · o contrato promete uma CONFIANÇA de 0 a 1 — e um texto escrito não traz número nenhum.
  Então o modelo não escreve. Ele lê as instruções e o relato, e olhamos UMA vez a próxima palavra
  que ele diria: o modelo dá uma probabilidade a cada palavra possível. Ficamos com as das 6
  categorias (o começo de cada nome — "que", "des", "ench", "se", "pol", "lix"), e as dividimos
  pela soma delas. A maior é a sugestão; o valor dela, a confiança. A resposta é SEMPRE uma das 6.
  No banco de provas: os mesmos 27 de 30 de quando ele escrevia, numa passada só.

⚠️ CONFIANÇA DO MODELO NÃO É CHANCE DE ACERTO. No relato #2 do banco de provas ("O nível do rio
   baixou tanto que o barco…"), o modelo disse "enchente" com confiança 1,00 — e errou (é seca;
   as regras acertam esse). A página Analisador diz isso a quem usa.

O MODELO MORA NA SUA MÁQUINA — e é baixado ANTES, à parte:
    python -m src.baixar_modelo            (uma vez, com internet: ~3,1 GB)
  Aqui ele é carregado com local_files_only=True: a API NUNCA baixa nada. Sem o download feito,
  carregar_motor() levanta OSError — e a rota responde 503 (api/rotas/analise.py).

Rodar isoladamente (carrega o modelo e analisa os 5 exemplos do painel):
    python -m src.analisador_llm
"""

import time
from dataclasses import dataclass

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.bancada import CATEGORIAS, ESCOLHA, INSTRUCOES as PROMPTS

# O modelo e o prompt são os que VENCERAM na bancada (Aula 15) — importados de lá, não copiados:
# se alguém mudar as definições das categorias, a bancada passa a medir exatamente o que a API usa.
# (Sem as definições, o mesmo modelo acertava 23 de 30; com elas, 27.)
MODELO = ESCOLHA["modelo"]
INSTRUCOES = PROMPTS[ESCOLHA["prompt"]]


@dataclass
class Motor:
    """O modelo carregado: o tokenizador, os pesos e o 1º token de cada categoria."""
    nome: str
    tokenizador: AutoTokenizer
    modelo: AutoModelForCausalLM
    tokens_das_categorias: list[int]
    segundos_para_carregar: float


def carregar_motor(nome: str = MODELO) -> Motor:
    """Do disco para a memória — UMA vez, quando a API sobe (~8 s e ~6,5 GB na nossa máquina).

    local_files_only=True: se o modelo não foi baixado (python -m src.baixar_modelo), OSError
    agora — e não um download de 3 GB escondido na subida da API.
    dtype=torch.float32: o modelo foi salvo em bfloat16 (metade da memória), mas na nossa CPU o
    bfloat16 é 5 vezes mais lento (12,8 s × 2,5 s por relato, na bancada).
    """
    relogio = time.perf_counter()
    tokenizador = AutoTokenizer.from_pretrained(nome, local_files_only=True)
    modelo = AutoModelForCausalLM.from_pretrained(nome, local_files_only=True, dtype=torch.float32)
    modelo.eval()                       # modo de uso, não de treino

    # O 1º token do nome de cada categoria. Têm de ser DIFERENTES entre si — senão duas
    # categorias dividiriam a mesma aposta. (No tokenizador do Qwen: que, des, ench, se, pol, lix.)
    tokens = [tokenizador.encode(c, add_special_tokens=False)[0] for c in CATEGORIAS]
    if len(set(tokens)) != len(tokens):
        raise ValueError(f"Duas categorias começam com o mesmo token no tokenizador de {nome}.")
    return Motor(nome, tokenizador, modelo, tokens, round(time.perf_counter() - relogio, 1))


def classificar_com_modelo(texto: str, motor: Motor) -> dict:
    """A categoria mais provável e a confiança. Devolve MAIS do que a API promete (as 6
    probabilidades) — o response model deixa de fora, como fazia com as pontuações das regras."""
    mensagens = [{"role": "system", "content": INSTRUCOES},
                 {"role": "user", "content": f"Relato: {texto}\nCategoria:"}]
    entrada = motor.tokenizador.apply_chat_template(mensagens, add_generation_prompt=True,
                                                    return_tensors="pt", return_dict=True)
    with torch.no_grad():               # só usar o modelo: sem guardar nada para treino
        saida = motor.modelo(**entrada)
    # saida.logits: uma nota para cada palavra do vocabulário, em cada posição. Interessa a ÚLTIMA
    # posição — a próxima palavra —, e só as notas das 6 categorias.
    notas = saida.logits[0, -1, motor.tokens_das_categorias]
    probabilidades = torch.softmax(notas, dim=0).tolist()
    melhor = max(range(len(CATEGORIAS)), key=lambda i: probabilidades[i])
    return {
        "categoria_sugerida": CATEGORIAS[melhor],
        "confianca": round(probabilidades[melhor], 2),
        "pistas": [],                   # um modelo não aponta palavras: lê o texto inteiro
        "probabilidades": {c: round(p, 3) for c, p in zip(CATEGORIAS, probabilidades)},   # detalhe interno
    }


if __name__ == "__main__":
    from src.relatos import carregar_exemplos

    motor = carregar_motor()
    print(f"{motor.nome} · carregado em {motor.segundos_para_carregar} s\n")
    for r in carregar_exemplos():
        relogio = time.perf_counter()
        res = classificar_com_modelo(r["texto"], motor)
        print(f"#{r['id']} declarada: {r['categoria']:<12} sugerida: {res['categoria_sugerida']:<12} "
              f"confiança {res['confianca']:.2f}  ({time.perf_counter() - relogio:.1f} s)")
