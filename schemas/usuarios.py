
from pydantic import BaseModel, Field, EmailStr, SecretStr


class Usuario(BaseModel):
    nome: str = Field(
        min_length=2,
        max_length=100,
        description="Nome completo do usuário"
    )

    email: EmailStr = Field(
        max_length=50,
        description="E-mail válido e único do usuário"
    )

    senha: SecretStr = Field(
        min_length=8,
        max_length=128,
        description="Senha com no mínimo 8 caracteres"
    )

class UsuarioAtualizar(BaseModel):
    nome: str = Field(
        min_length=2,
        max_length=100,
        description="Novo nome do usuário"
    )
    email: EmailStr = Field(
        max_length=100,
        description="Novo e-mail do usuário"
    )