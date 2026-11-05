"""
Passo 4 (cliente) — o programa da prefeitura, que conferia "== 200". Rode com o passo 4 no ar:

    python passo04_cliente.py

Dois jeitos de conferir o mesmo envio:
  · ingênuo:    r.status_code == 200       -> diz "FALHOU" a um relato que foi GRAVADO (201)
  · pela família: r.ok  (ou 200 <= status < 300)  -> 200 e 201 são sucesso; 4xx e 5xx, não

O que importa é a FAMÍLIA do status — o primeiro dígito: "The first digit of a status code
defines its category." [Adeshina, p62]
"""

import requests

API = "http://127.0.0.1:8000"
RELATO = {"uf": "PA", "categoria": "queimada", "texto": "Fumaça densa na beira da estrada desde cedo."}

for rota in ["/v1/relatos", "/relatos"]:
    r = requests.post(API + rota, json=RELATO, timeout=10)
    ingenuo = "gravado" if r.status_code == 200 else "FALHOU"
    pela_familia = "gravado" if r.ok else "FALHOU"
    print(f"POST {rota:<12} -> {r.status_code}  | == 200: {ingenuo:<8} | r.ok: {pela_familia:<8} | {r.json()}")
