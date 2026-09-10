"""
Passo 1 — Antes de raspar: pedir licença.

A pergunta que vem ANTES de "como extraio isto?" é "posso extrair isto?".
Três checagens, nesta ordem — e nenhuma delas exige biblioteca nova:

  1. robots.txt   — o pedido explícito do dono do site, em formato legível por
                    máquina. A biblioteca padrão do Python já sabe interpretá-lo.
  2. Crawl-delay  — de quanto em quanto tempo ele aceita uma requisição.
  3. licença      — o que você pode FAZER com o conteúdo depois de baixá-lo.

Rodar:  python passo01_permissao.py
"""

import os
from urllib.robotparser import RobotFileParser

import requests

SITE = "https://agenciabrasil.ebc.com.br"

# Identifique-se de verdade. Um User-Agent honesto diz quem é, para quê, e como
# ser avisado se você estiver incomodando. Copiar a assinatura de um Chrome é o
# começo de um caminho que termina em bloqueio — merecido.
AGENTE = "INFNET-PB-IA-Aplicada/1.0 (material didatico; contato: professor)"

# A rede da escola usa proxy com TLS interceptado (lição da Aula 5: a exceção é
# CONFIGURAÇÃO, e o padrão continua seguro).
VERIFICAR = os.environ.get("PAINEL_ODS_VERIFICAR_SSL", "true").lower() not in {"false", "0", "nao"}
if not VERIFICAR:
    import urllib3

    urllib3.disable_warnings()

print(f"Lendo {SITE}/robots.txt …\n")
texto = requests.get(
    f"{SITE}/robots.txt", headers={"User-Agent": AGENTE}, timeout=30, verify=VERIFICAR
).text

regras = RobotFileParser()
regras.parse(texto.splitlines())

for caminho in ["/meio-ambiente", "/economia", "/admin/config", "/cron.php"]:
    permitido = regras.can_fetch(AGENTE, SITE + caminho)
    print(f"  {'PODE   ' if permitido else 'NÃO PODE'}  {caminho}")

pausa = regras.crawl_delay(AGENTE)
print(f"\nCrawl-delay declarado: {pausa} segundos")
print("-> é isto que decide o DESENHO do seu programa:")
print("  com 10s por requisição, raspar dentro do app é impossível;")
print("  a coleta roda à parte, grava um arquivo, e o app lê o arquivo.")

print("\nE a licença? Na Agência Brasil, o rodapé diz Creative Commons Atribuição 3.0:")
print("  pode reutilizar CITANDO a fonte. É por isso que o CSV tem a coluna `fonte`.")
print("  robots.txt responde 'posso BAIXAR?'. A licença responde 'posso PUBLICAR?'.")
