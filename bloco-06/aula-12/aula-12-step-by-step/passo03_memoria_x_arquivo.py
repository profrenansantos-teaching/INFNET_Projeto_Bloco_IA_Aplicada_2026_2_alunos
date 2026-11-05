"""
Passo 3 — onde o relato mora: na memória ou num arquivo? (Aula 12 · 🐛 tropeço real da v10)

    uvicorn passo03_memoria_x_arquivo:app --reload        (num TERMINAL de verdade)

O livro guarda os itens numa lista: "a temporary in-app database" [Adeshina, p37]. Temporária
mesmo. Faça, no /docs:

  1. POST /memoria  e  POST /arquivo — três vezes cada (o mesmo corpo serve);
  2. GET  /memoria  e  GET  /arquivo — três e três;
  3. SALVE QUALQUER ARQUIVO .py desta pasta (até este, sem mudar nada). O --reload reinicia
     o servidor em ~3 s;
  4. GET  /memoria  -> []    ·    GET /arquivo -> os três continuam lá.

O arquivo é `relatos_passo03.csv`, nesta pasta (não versionado). Abra-o no editor: é texto.
"""

import csv
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Passo 3 — memória × arquivo")

ARQUIVO = Path(__file__).parent / "relatos_passo03.csv"
CAMPOS = ["uf", "categoria", "texto"]


class Relato(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    uf: Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO", "SP", "RJ", "RS", "BA", "PE"]
    categoria: Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]
    texto: str = Field(min_length=15, max_length=500)


# ---------------------------------------------------------------- na memória (o livro)
na_memoria = []


@app.post("/memoria")
def guardar_na_memoria(relato: Relato):
    na_memoria.append(relato.model_dump())
    return {"guardados": len(na_memoria)}


@app.get("/memoria")
def ler_da_memoria():
    return na_memoria


# ---------------------------------------------------------------- no arquivo (a v10)
@app.post("/arquivo")
def guardar_no_arquivo(relato: Relato):
    novo = not ARQUIVO.exists()
    with ARQUIVO.open("a", encoding="utf-8", newline="") as f:    # "a": ACRESCENTA. "w" zeraria.
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            escritor.writeheader()
        escritor.writerow(relato.model_dump())
    return {"guardados": len(ler_do_arquivo())}


@app.get("/arquivo")
def ler_do_arquivo():
    if not ARQUIVO.exists():
        return []
    with ARQUIVO.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
