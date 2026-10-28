
from pydantic import BaseModel, Field


class RespostaErro(BaseModel):
    sucesso: bool = False

    codigo: int = Field(
        description="Código HTTP do erro"
    )

    mensagem: str = Field(
        description="Descrição do erro"
    )

    detalhes: list[dict] | None = Field(
        default=None,
        description="Detalhes adicionais, quando disponíveis"
    )
