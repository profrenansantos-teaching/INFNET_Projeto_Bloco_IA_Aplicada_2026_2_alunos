"""
Relatos de campo — guardar e ler. Painel ODS Brasil, v12 (Aula 14; criado na v10). Python puro.

DIVISÃO DE TRABALHO (a mesma das Aulas 7 e 10, agora com dado que CHEGA em vez de ser coletado):

    api/rotas/relatos.py   RECEBE e VALIDA (o modelo Pydantic)  ->  chama gravar_relato()
    src/relatos.py         GUARDA e LÊ o arquivo                    (este)
    paginas/relatos.py     MOSTRA — e, para gravar, PEDE à API. Nunca escreve no arquivo.

Um dono para cada escrita: quem grava é a API, depois de validar. Se o painel também
escrevesse aqui, a validação teria de existir em dois lugares — e um dia os dois
discordariam.

POR QUE data/relatos/ NÃO É VERSIONADO (.gitignore):
  é conteúdo enviado por PESSOAS. O repositório do Community Cloud é público, e um texto
  livre pode conter o que não devia (um nome, um telefone). Versionamos só os exemplos
  FICTÍCIOS de data/sample/relatos_exemplo.csv — que o painel mostra quando a API não está no ar.

Rodar isoladamente:
    python -m src.relatos
"""

import csv
import threading
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ARQ_RELATOS = BASE / "data" / "relatos" / "relatos.csv"
ARQ_EXEMPLOS = BASE / "data" / "sample" / "relatos_exemplo.csv"
CAMPOS = ["id", "recebido_em", "uf", "categoria", "texto"]

# As rotas `def` rodam em PARALELO (Aula 11: 8,0 s × 2,0 s). Dois envios ao mesmo tempo
# leem o mesmo "último id" e gravam dois relatos com o mesmo número. MEDIDO, sem esta trava:
# 40 envios simultâneos → só 9 números distintos (17 relatos com o nº 3); em 120 envios,
# 3 sumiram. Com a trava: 40 envios, 40 números. Ela faz um envio esperar o outro terminar —
# só durante a gravação, que leva milissegundos.
# (Com mais de um processo do servidor, isso não basta: é trabalho para um banco de dados.)
_TRAVA = threading.Lock()


def carregar_relatos(caminho: Path = ARQ_RELATOS) -> list[dict]:
    """Lista de dicionários {id, recebido_em, uf, categoria, texto}. Vazia se nada foi enviado."""
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8", newline="") as f:
        return [{**linha, "id": int(linha["id"])} for linha in csv.DictReader(f)]


def carregar_exemplos() -> list[dict]:
    """Os relatos FICTÍCIOS de data/sample/ — para o painel ter o que mostrar sem a API."""
    return carregar_relatos(ARQ_EXEMPLOS)


class RelatoRepetido(Exception):
    """O MESMO relato (UF, categoria e texto) chegou de novo em menos de JANELA_REPETIDO.

    Uma exceção do DOMÍNIO, e não do HTTP: este arquivo não sabe o que é 409. Quem
    traduz para HTTP é a rota (api/rotas/relatos.py). Assim src/ continua testável sem
    FastAPI — e a regra ("repetido") fica separada da resposta ("409 Conflict").
    """

    def __init__(self, anterior: dict):
        super().__init__(f"relato repetido: igual ao nº {anterior['id']}")
        self.anterior = anterior


# Por que 10 minutos: na v12 a equipe de campo, com o sinal caindo, apertava "Enviar" de
# novo quando a tela demorava — e o mesmo relato entrava duas, três vezes. Um texto igual,
# da mesma UF e categoria, dentro de 10 minutos, é o mesmo envio repetido.
JANELA_REPETIDO = timedelta(minutes=10)


def _repetido(anteriores: list[dict], uf: str, categoria: str, texto: str, agora: datetime) -> dict | None:
    """O relato igual mais recente dentro da janela — ou None."""
    for r in reversed(anteriores):                          # do mais novo para o mais velho
        if agora - datetime.strptime(r["recebido_em"], "%d/%m/%Y %H:%M") > JANELA_REPETIDO:
            return None                                     # daqui para trás, todos são mais velhos
        if (r["uf"], r["categoria"], r["texto"]) == (uf, categoria, texto):
            return r
    return None


def buscar_relato(id_relato: int, caminho: Path = ARQ_RELATOS) -> dict | None:
    """O relato com este número — ou None, se não houver (a rota decide o que isso vira: 404)."""
    for r in carregar_relatos(caminho):
        if r["id"] == id_relato:
            return r
    return None


def gravar_relato(uf: str, categoria: str, texto: str, caminho: Path = ARQ_RELATOS) -> dict:
    """Acrescenta UM relato ao arquivo e devolve o que foi gravado (com id e data).

    Recebe dados JÁ VALIDADOS (pela API). Abre o arquivo em modo "a" — acrescentar —
    e nunca em "w", que zeraria os relatos anteriores (o defeito 2 da A15, na Aula 10).
    O csv.DictWriter cuida de vírgulas, aspas e quebras de linha dentro do texto.

    v12: levanta RelatoRepetido se o mesmo relato chegou há menos de 10 minutos. A conferência
    fica DENTRO da trava — senão, dois envios iguais simultâneos passariam os dois.
    """
    with _TRAVA:
        anteriores = carregar_relatos(caminho)
        agora = datetime.now()
        anterior = _repetido(anteriores, uf, categoria, texto, agora)
        if anterior is not None:
            raise RelatoRepetido(anterior)
        novo = {
            "id": max((r["id"] for r in anteriores), default=0) + 1,
            "recebido_em": agora.strftime("%d/%m/%Y %H:%M"),
            "uf": uf,
            "categoria": categoria,
            "texto": texto,
        }
        caminho.parent.mkdir(parents=True, exist_ok=True)
        arquivo_novo = not caminho.exists()
        with caminho.open("a", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=CAMPOS)
            if arquivo_novo:
                escritor.writeheader()
            escritor.writerow(novo)
    return novo


def filtrar_relatos(relatos: list[dict], uf: str | None = None, categoria: str | None = None) -> list[dict]:
    return [
        r for r in relatos
        if (uf is None or r["uf"] == uf) and (categoria is None or r["categoria"] == categoria)
    ]


if __name__ == "__main__":
    enviados = carregar_relatos()
    print(f"{len(enviados)} relato(s) enviado(s) · {len(carregar_exemplos())} exemplo(s) fictício(s)")
    for r in (enviados or carregar_exemplos())[-3:]:
        print(f"  #{r['id']} {r['uf']} · {r['categoria']} · {r['texto'][:60]}")
