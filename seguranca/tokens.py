
import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not JWT_SECRET:
    raise RuntimeError(
        "A variável JWT_SECRET não foi configurada no arquivo .env."
    )


def criar_token_acesso(id_usuario: int, email: str) -> str:
    agora = datetime.now(timezone.utc)

    payload = {
        "sub": str(id_usuario),
        "email": email,
        "iat": agora,
        "exp": agora + timedelta(minutes=30)
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return token



def validar_token_acesso(token: str) -> dict:
    try:
        dados = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        id_usuario = dados.get("sub")

        if not id_usuario:
            raise HTTPException(
                status_code=401,
                detail="Token inválido."
            )

        return dados

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado. Faça login novamente."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido. Faça login novamente."
        )
