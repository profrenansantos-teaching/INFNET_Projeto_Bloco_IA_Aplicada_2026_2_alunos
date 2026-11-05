"""
O que a API ACEITA — os modelos de entrada. Painel ODS Brasil, v10 (Aula 12).

Um modelo Pydantic é o CONTRATO do corpo de um POST: que campos, de que tipo, com que
limites. O FastAPI confere cada envio contra ele ANTES de a função da rota rodar; o que não
cumpre volta com 422 e a lista de TODOS os problemas — não só o primeiro. E do mesmo modelo
sai a documentação do /docs, com o exemplo.

"Models are created by subclassing Pydantic's BaseModel class." [Adeshina, p40]

LIVRO × HOJE (Pydantic 2):
  o livro configura o modelo com `class Config: schema_extra = {...}` [Adeshina, p51–52].
  No Pydantic 2 isso ainda RODA — avisa que "'schema_extra' has been renamed to
  'json_schema_extra'" — e o exemplo SOME do /docs (verificado). O jeito de hoje é o
  `model_config = ConfigDict(...)`, abaixo.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# As 27 UFs. Um relato pode vir de qualquer lugar do país — não só da Amazônia Legal.
SiglaUF = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

Categoria = Literal["queimada", "desmatamento", "enchente", "seca", "poluicao", "lixo", "outro"]


class Relato(BaseModel):
    """Um relato de campo: onde, o quê, e o que foi observado — e nada além disso."""

    model_config = ConfigDict(
        # 🐛 Tropeço da v10: sem esta linha, um envio com "nome" e "telefone" do morador
        #    voltava 200 — os dois campos eram DESCARTADOS em silêncio (o padrão do Pydantic
        #    é ignorar o que sobra), e a equipe de campo acreditou que tinham sido gravados.
        #    Com "forbid", a API RECUSA (422, "Extra inputs are not permitted") e diz quais
        #    campos sobraram: quem envia fica sabendo que dado pessoal não entra aqui.
        extra="forbid",
        # "   " com 15 espaços não é um relato: tira os espaços das pontas ANTES de medir.
        str_strip_whitespace=True,
        # O exemplo que o /docs mostra no "Try it out" (o "schema_extra" do livro, versão 2).
        json_schema_extra={
            "examples": [
                {
                    "uf": "PA",
                    "categoria": "queimada",
                    "texto": "Fumaça densa na beira da BR-163 desde cedo, com cheiro de mato queimado.",
                }
            ]
        },
    )

    uf: SiglaUF = Field(description="Sigla da UF onde o fato foi observado.")
    categoria: Categoria = Field(description="O tipo de ocorrência.")
    texto: str = Field(
        min_length=15,
        max_length=500,
        description="O que foi observado, em 15 a 500 caracteres. Não escreva nomes, telefones nem e-mails.",
    )
