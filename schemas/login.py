
from pydantic import BaseModel, EmailStr, Field, SecretStr


class DadosLogin(BaseModel):
    email: EmailStr = Field(
        description="E-mail cadastrado do usuário"
    )

    senha: SecretStr = Field(
        min_length=8,
        max_length=128,
        description="Senha cadastrada pelo usuário"
    )


class RespostaLogin(BaseModel):
    access_token: str = Field(
        description="Token JWT para autenticação"
    )

    token_type: str = Field(
        default="bearer",
        description="Tipo do token de autenticação"
    )
