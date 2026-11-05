"""Router dos relatos (passo 4): o POST validado do passo 2 + o arquivo do passo 3."""

import csv
from pathlib import Path
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/relatos", tags=["relatos"])

ARQUIVO = Path(__file__).resolve().parents[2] / "relatos_passo04.csv"   # na pasta dos passos
CAMPOS = ["uf", "categoria", "texto"]


class Relato(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    uf: Literal["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO", "SP", "RJ", "RS", "BA", "PE"]
    categoria: Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]
    texto: str = Field(min_length=15, max_length=500)


def _ler():
    if not ARQUIVO.exists():
        return []
    with ARQUIVO.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@router.post("", summary="Enviar um relato")
def enviar(relato: Relato):
    """Valida (o modelo) e grava (o arquivo). Campo a mais: 422."""
    novo = not ARQUIVO.exists()
    with ARQUIVO.open("a", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            escritor.writeheader()
        escritor.writerow(relato.model_dump())
    return {"mensagem": "Relato recebido.", "total": len(_ler())}


@router.get("", summary="Listar os relatos")
def listar():
    return {"linhas": len(_ler()), "dados": _ler()}
