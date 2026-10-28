
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError
)

criptografador = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    return criptografador.hash(senha)


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        return criptografador.verify(hash_armazenado, senha)
    except (VerifyMismatchError, VerificationError):
        return False
