
from schemas.usuarios import Usuario
from seguranca.senhas import gerar_hash_senha
from schemas.usuarios import UsuarioAtualizar
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from mysql.connector.errors import IntegrityError
from datetime import date, timedelta
from schemas.emprestimos import EmprestimoCadastrar, EmprestimoResposta, EmprestimoAtualizar, EmprestimoDevolver

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from seguranca.tokens import validar_token_acesso

from schemas.login import DadosLogin, RespostaLogin
from seguranca.senhas import verificar_senha
from seguranca.tokens import criar_token_acesso

from conexoes.mysql import conectar


from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas.erros import RespostaErro



app = FastAPI(
    title="API Biblioteca",
    description="API para gerenciar autores, livros, usuários e empréstimos.",
    version="1.0.0"
)

#PROTEGENDO A API COM BEARER TOKEN
esquema_bearer = HTTPBearer()


def obter_usuario_autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer)
):
    token = credenciais.credentials

    dados_token = validar_token_acesso(token)

    return dados_token



# Tratamento global de erros HTTP
@app.exception_handler(StarletteHTTPException)
async def tratar_erro_http(
    request: Request,
    exc: StarletteHTTPException
):
    mensagens = {
        400: "Requisição inválida.",
        401: "Autenticação necessária.",
        403: "Acesso não permitido.",
        404: "Recurso não encontrado.",
        405: "Método HTTP não permitido."
    }

    mensagem = (
        exc.detail
        if isinstance(exc.detail, str)
        else mensagens.get(exc.status_code, "Erro na requisição.")
    )

    resposta = RespostaErro(
        codigo=exc.status_code,
        mensagem=mensagem
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=resposta.model_dump()
    )



# Tratamento global de erros de validação
@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    exc: RequestValidationError
):
    detalhes = []

    for erro in exc.errors():
        campo = ".".join(
            str(item) for item in erro["loc"]
        )

        tipo = erro["type"]
        mensagem_original = erro["msg"]

        # Personalizar mensagens de e-mail
        if campo.endswith("email"):
            if tipo == "missing":
                mensagem = "O e-mail é obrigatório."
            else:
                mensagem = (
                    "O e-mail informado é inválido. "
                    "Digite um endereço no formato usuario@exemplo.com."
                )

        # Personalizar mensagens de senha
        elif campo.endswith("senha"):
            if tipo == "missing":
                mensagem = "A senha é obrigatória."
            elif tipo == "string_too_short":
                mensagem = "A senha deve ter pelo menos 8 caracteres."
            elif tipo == "string_too_long":
                mensagem = "A senha deve ter no máximo 128 caracteres."
            else:
                mensagem = mensagem_original

        # Campos obrigatórios
        elif tipo == "missing":
            mensagem = "Este campo é obrigatório."

        # Comprimento mínimo
        elif tipo == "string_too_short":
            mensagem = "O texto informado é muito curto."

        # Comprimento máximo
        elif tipo == "string_too_long":
            mensagem = "O texto informado ultrapassa o limite permitido."

        # Tipos de dados inválidos
        elif tipo in ("int_parsing", "int_type"):
            mensagem = "Informe um número inteiro válido."

        else:
            mensagem = mensagem_original

        detalhes.append({
            "campo": campo,
            "mensagem": mensagem,
            "tipo": tipo
        })

    resposta = RespostaErro(
        codigo=422,
        mensagem="Os dados enviados são inválidos. Verifique os campos informados.",
        detalhes=detalhes
    )

    return JSONResponse(
        status_code=422,
        content=resposta.model_dump()
    )



# Tratamento global de erros inesperados
@app.exception_handler(Exception)
async def tratar_erro_interno(
    request: Request,
    exc: Exception
):
    resposta = RespostaErro(
        codigo=500,
        mensagem="Ocorreu um erro interno. Tente novamente mais tarde."
    )

    return JSONResponse(
        status_code=500,
        content=resposta.model_dump()
    )




# Modelo de dados para criar ou atualizar um autor
class Autor(BaseModel):
    nome: str = Field(
        min_length=2,
        max_length=100,
        description="Nome completo do autor"
    )
    nacionalidade: str | None = Field(
        default=None,
        max_length=50,
        description="Nacionalidade do autor"
    )



# Modelo de dados para criar ou atualizar um livro
class Livro(BaseModel):
    titulo: str = Field(
        min_length=1,
        max_length=150,
        description="Título do livro"
    )

    ano_publicacao: int | None = Field(
        default=None,
        ge=0,
        le=2100,
        description="Ano de publicação"
    )

    id_autor: int = Field(
        gt=0,
        description="ID de um autor já cadastrado"
    )

    categoria: str | None = Field(
        default=None,
        max_length=50,
        description="Categoria do livro"
    )



# Página inicial
@app.get("/")
def inicio():
    return {"mensagem": "API Biblioteca funcionando!"}


# 1. Cadastrar autor
@app.post("/autores", status_code=status.HTTP_201_CREATED)
def cadastrar_autor(autor: Autor,
    usuario: dict = Depends(obter_usuario_autenticado)):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO autores (nome, nacionalidade)
            VALUES (%s, %s)
        """

        cursor.execute(
            sql,
            (autor.nome, autor.nacionalidade)
        )

        conexao.commit()

        id_autor = cursor.lastrowid

        return {
            "mensagem": "Autor cadastrado com sucesso!",
            "id_autor": id_autor,
            "nome": autor.nome,
            "nacionalidade": autor.nacionalidade
        }

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar autor."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


# 2. Listar todos os autores
@app.get("/autores")
def listar_autores():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_autor, nome, nacionalidade
            FROM autores
            ORDER BY nome
        """)

        return cursor.fetchall()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar os autores."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


# 3. Buscar autor por ID
@app.get("/autores/{id_autor}")
def buscar_autor(id_autor: int):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_autor, nome, nacionalidade
            FROM autores
            WHERE id_autor = %s
            """,
            (id_autor,)
        )

        autor = cursor.fetchone()

        if autor is None:
            raise HTTPException(
                status_code=404,
                detail="Autor não encontrado."
            )

        return autor

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar o autor."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


# 4. Atualizar autor
@app.put("/autores/{id_autor}")
def atualizar_autor(id_autor: int, autor: Autor,usuario: dict = Depends(obter_usuario_autenticado)):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT id_autor
            FROM autores
            WHERE id_autor = %s
            """,
            (id_autor,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Autor não encontrado."
            )

        cursor.execute(
            """
            UPDATE autores
            SET nome = %s, nacionalidade = %s
            WHERE id_autor = %s
            """,
            (autor.nome, autor.nacionalidade, id_autor)
        )

        conexao.commit()

        return {
            "mensagem": "Autor atualizado com sucesso!",
            "id_autor": id_autor,
            "nome": autor.nome,
            "nacionalidade": autor.nacionalidade
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar autor."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


# 5. Excluir autor
@app.delete("/autores/{id_autor}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_autor(id_autor: int, usuario: dict = Depends(obter_usuario_autenticado)):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id_autor FROM autores WHERE id_autor = %s",
            (id_autor,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Autor não encontrado."
            )

        cursor.execute(
            "DELETE FROM autores WHERE id_autor = %s",
            (id_autor,)
        )

        conexao.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir autor. Verifique se existem livros vinculados."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()



# 1. Cadastrar livro
@app.post("/livros", status_code=status.HTTP_201_CREATED)
def cadastrar_livro(livro: Livro, usuario: dict = Depends(obter_usuario_autenticado)):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Verificar se o autor existe
        cursor.execute(
            "SELECT id_autor FROM autores WHERE id_autor = %s",
            (livro.id_autor,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Autor não encontrado."
            )

        # Cadastrar o livro
        cursor.execute(
            """
            INSERT INTO livros
                (titulo, ano_publicacao, id_autor, categoria)
            VALUES (%s, %s, %s, %s)
            """,
            (
                livro.titulo,
                livro.ano_publicacao,
                livro.id_autor,
                livro.categoria
            )
        )

        conexao.commit()

        return {
            "mensagem": "Livro cadastrado com sucesso!",
            "id_livro": cursor.lastrowid,
            "titulo": livro.titulo,
            "ano_publicacao": livro.ano_publicacao,
            "id_autor": livro.id_autor,
            "categoria": livro.categoria
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar livro."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()



@app.get("/livros")
def listar_livros():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                livros.id_livro,
                livros.titulo,
                livros.ano_publicacao,
                livros.categoria,
                autores.id_autor,
                autores.nome AS nome_autor
            FROM livros
            INNER JOIN autores
                ON livros.id_autor = autores.id_autor
            ORDER BY livros.id_livro
        """)

        livros = cursor.fetchall()

        return {
            "mensagem": "Livros listados com sucesso!",
            "total": len(livros),
            "livros": livros
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao listar livros."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()



@app.get("/livros/{id_livro}")
def buscar_livro(id_livro: int):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                livros.id_livro,
                livros.titulo,
                livros.ano_publicacao,
                livros.categoria,
                autores.id_autor,
                autores.nome AS nome_autor
            FROM livros
            INNER JOIN autores
                ON livros.id_autor = autores.id_autor
            WHERE livros.id_livro = %s
        """, (id_livro,))

        livro = cursor.fetchone()

        if livro is None:
            raise HTTPException(
                status_code=404,
                detail="Livro não encontrado."
            )

        return livro

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao buscar livro."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()



@app.put("/livros/{id_livro}")
def atualizar_livro(id_livro: int, livro: Livro, usuario: dict = Depends(obter_usuario_autenticado)):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Verifica se o livro existe
        cursor.execute(
            "SELECT id_livro FROM livros WHERE id_livro = %s",
            (id_livro,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Livro não encontrado."
            )

        # Verifica se o autor existe
        cursor.execute(
            "SELECT id_autor FROM autores WHERE id_autor = %s",
            (livro.id_autor,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Autor não encontrado."
            )

        # Atualiza o livro
        cursor.execute("""
            UPDATE livros
            SET titulo = %s,
                ano_publicacao = %s,
                id_autor = %s,
                categoria = %s
            WHERE id_livro = %s
        """, (
            livro.titulo,
            livro.ano_publicacao,
            livro.id_autor,
            livro.categoria,
            id_livro
        ))

        conexao.commit()

        return {
            "mensagem": "Livro atualizado com sucesso!",
            "id_livro": id_livro,
            "titulo": livro.titulo,
            "ano_publicacao": livro.ano_publicacao,
            "id_autor": livro.id_autor,
            "categoria": livro.categoria
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar livro."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()



from mysql.connector.errors import IntegrityError


@app.delete("/livros/{id_livro}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_livro(id_livro: int, usuario: dict = Depends(obter_usuario_autenticado)):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id_livro FROM livros WHERE id_livro = %s",
            (id_livro,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Livro não encontrado."
            )

        cursor.execute(
            "DELETE FROM livros WHERE id_livro = %s",
            (id_livro,)
        )

        conexao.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise

    except IntegrityError:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir este livro porque ele possui empréstimos relacionados."
        )

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir livro."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()



from mysql.connector.errors import IntegrityError


@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: Usuario):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Gera o hash da senha antes de salvar no banco
        senha_hash = gerar_hash_senha(
            usuario.senha.get_secret_value()
        )

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (%s, %s, %s)
        """, (
            usuario.nome,
            usuario.email,
            senha_hash
        ))

        conexao.commit()

        # Não retorna a senha nem o hash
        return {
            "mensagem": "Usuário cadastrado com sucesso!",
            "id_usuario": cursor.lastrowid,
            "nome": usuario.nome,
            "email": usuario.email
        }

    except IntegrityError as erro:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        if erro.errno == 1062:
            raise HTTPException(
                status_code=409,
                detail="Este e-mail já está cadastrado."
            )

        raise HTTPException(
            status_code=409,
            detail="Não foi possível cadastrar o usuário devido a uma restrição do banco."
        )

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar usuário."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()



@app.get("/usuarios")
def listar_usuarios():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_usuario, nome, email
            FROM usuarios
            ORDER BY id_usuario
        """)

        usuarios = cursor.fetchall()

        return {
            "mensagem": "Usuários listados com sucesso!",
            "total": len(usuarios),
            "usuarios": usuarios
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao listar usuários."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.put("/usuarios/{id_usuario}")
def atualizar_usuario(id_usuario: int, usuario: UsuarioAtualizar):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Verificar se o usuário existe
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado."
            )

        # Verificar se o e-mail já pertence a outro usuário
        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE email = %s AND id_usuario != %s
            """,
            (str(usuario.email), id_usuario)
        )

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Este e-mail já está cadastrado para outro usuário."
            )

        # Atualizar nome e e-mail
        cursor.execute(
            """
            UPDATE usuarios
            SET nome = %s, email = %s
            WHERE id_usuario = %s
            """,
            (usuario.nome, str(usuario.email), id_usuario)
        )

        conexao.commit()

        return {
            "mensagem": "Usuário atualizado com sucesso!",
            "id_usuario": id_usuario,
            "nome": usuario.nome,
            "email": str(usuario.email)
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar usuário."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


# Excluir usuário
@app.delete("/usuarios/{id_usuario}")
def excluir_usuario(id_usuario: int):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # 1. Verificar se o usuário existe
        cursor.execute(
            """
            SELECT id_usuario, nome
            FROM usuarios
            WHERE id_usuario = %s
            """,
            (id_usuario,)
        )

        usuario = cursor.fetchone()

        if usuario is None:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado."
            )

        # 2. Verificar se existem empréstimos vinculados
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM emprestimos
            WHERE id_usuario = %s
            """,
            (id_usuario,)
        )

        resultado = cursor.fetchone()

        if resultado["total"] > 0:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Não é possível excluir este usuário porque "
                    "existem empréstimos vinculados a ele."
                )
            )

        # 3. Excluir o usuário
        cursor.execute(
            """
            DELETE FROM usuarios
            WHERE id_usuario = %s
            """,
            (id_usuario,)
        )

        conexao.commit()

        return {
            "mensagem": "Usuário excluído com sucesso!",
            "id_usuario": id_usuario,
            "nome": usuario["nome"]
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir usuário."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.post(
    "/auth/login",
    response_model=RespostaLogin,
    summary="Autenticar usuário",
    description="Valida o e-mail e a senha e retorna um token JWT."
)
def login(dados: DadosLogin):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Buscar usuário pelo e-mail
        cursor.execute(
            """
            SELECT id_usuario, nome, email, senha_hash
            FROM usuarios
            WHERE email = %s
            """,
            (str(dados.email),)
        )

        usuario = cursor.fetchone()

        # Usar a mesma mensagem para e-mail ou senha incorretos
        if usuario is None or not verificar_senha(
            dados.senha.get_secret_value(),
            usuario["senha_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="E-mail ou senha incorretos."
            )

        # Gerar token JWT
        token = criar_token_acesso(
            id_usuario=usuario["id_usuario"],
            email=usuario["email"]
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível realizar o login. Tente novamente."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.get("/auth/me", summary="Consultar usuário autenticado")
def consultar_usuario_autenticado(
    usuario: dict = Depends(obter_usuario_autenticado)
):
    return {
        "mensagem": "Token válido!",
        "id_usuario": usuario["sub"],
        "email": usuario.get("email")
    }



@app.post(
    "/emprestimos",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar empréstimo",
    description="Registra um empréstimo com prazo padrão de 14 dias. Exige autenticação JWT."
)
def cadastrar_emprestimo(
    emprestimo: EmprestimoCadastrar,
    usuario: dict = Depends(obter_usuario_autenticado)
):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # 1. Verificar se o usuário existe
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario = %s",
            (emprestimo.id_usuario,)
        )
        usuario_cadastrado = cursor.fetchone()

        if usuario_cadastrado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        # 2. Verificar se o livro existe
        cursor.execute(
            "SELECT id_livro FROM livros WHERE id_livro = %s",
            (emprestimo.id_livro,)
        )
        livro_cadastrado = cursor.fetchone()

        if livro_cadastrado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado."
            )

        # 3. Impedir dois empréstimos ativos do mesmo livro
        cursor.execute(
            """
            SELECT id_emprestimo
            FROM emprestimos
            WHERE id_livro = %s
              AND data_devolucao_real IS NULL
            LIMIT 1
            """,
            (emprestimo.id_livro,)
        )
        emprestimo_ativo = cursor.fetchone()

        if emprestimo_ativo is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este livro já possui um empréstimo ativo."
            )

        # 4. Calcular as datas
        data_emprestimo = date.today()
        data_devolucao_prevista = data_emprestimo + timedelta(days=14)

        # 5. Salvar no banco
        cursor.execute(
            """
            INSERT INTO emprestimos (
                id_usuario,
                id_livro,
                data_emprestimo,
                data_devolucao_prevista,
                data_devolucao_real
            )
            VALUES (%s, %s, %s, %s, NULL)
            """,
            (
                emprestimo.id_usuario,
                emprestimo.id_livro,
                data_emprestimo,
                data_devolucao_prevista
            )
        )

        id_emprestimo = cursor.lastrowid
        conexao.commit()

        return {
            "mensagem": "Empréstimo cadastrado com sucesso.",
            "id_emprestimo": id_emprestimo,
            "id_usuario": emprestimo.id_usuario,
            "id_livro": emprestimo.id_livro,
            "data_emprestimo": data_emprestimo,
            "data_devolucao_prevista": data_devolucao_prevista,
            "data_devolucao_real": None,
            "status": "ativo"
        }

    except HTTPException:
        if conexao is not None:
            conexao.rollback()
        raise

    except IntegrityError:
        if conexao is not None:
            conexao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este livro já possui um empréstimo ativo ou os dados violam uma restrição do banco."
        )

    except Exception:
        if conexao is not None:
            conexao.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível cadastrar o empréstimo."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()
@app.get(
    "/emprestimos",
    summary="Listar empréstimos",
    description="Lista os empréstimos com os nomes dos usuários e títulos dos livros."
)
def listar_emprestimos():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id_emprestimo,
                e.id_usuario,
                u.nome AS nome_usuario,
                e.id_livro,
                l.titulo AS titulo_livro,
                e.data_emprestimo,
                e.data_devolucao_prevista,
                e.data_devolucao_real,
                CASE
                    WHEN e.data_devolucao_real IS NOT NULL THEN 'devolvido'
                    WHEN e.data_devolucao_prevista < CURDATE() THEN 'atrasado'
                    ELSE 'ativo'
                END AS status
            FROM emprestimos e
            INNER JOIN usuarios u ON e.id_usuario = u.id_usuario
            INNER JOIN livros l ON e.id_livro = l.id_livro
            ORDER BY e.id_emprestimo DESC
        """)

        emprestimos = cursor.fetchall()
        return emprestimos

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível listar os empréstimos."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.get(
    "/emprestimos/{id_emprestimo}",
    summary="Consultar empréstimo por ID",
    description="Consulta um empréstimo específico, incluindo usuário, livro e status."
)
def consultar_emprestimo(id_emprestimo: int):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id_emprestimo,
                e.id_usuario,
                u.nome AS nome_usuario,
                e.id_livro,
                l.titulo AS titulo_livro,
                e.data_emprestimo,
                e.data_devolucao_prevista,
                e.data_devolucao_real,
                CASE
                    WHEN e.data_devolucao_real IS NOT NULL THEN 'devolvido'
                    WHEN e.data_devolucao_prevista < CURDATE() THEN 'atrasado'
                    ELSE 'ativo'
                END AS status
            FROM emprestimos e
            INNER JOIN usuarios u ON e.id_usuario = u.id_usuario
            INNER JOIN livros l ON e.id_livro = l.id_livro
            WHERE e.id_emprestimo = %s
        """, (id_emprestimo,))

        emprestimo = cursor.fetchone()

        if emprestimo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empréstimo não encontrado."
            )

        return emprestimo

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível consultar o empréstimo."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()




@app.put(
    "/emprestimos/{id_emprestimo}",
    summary="Atualizar empréstimo",
    description="Atualiza os dados de um empréstimo ativo. Exige autenticação JWT."
)
def atualizar_emprestimo(
    id_emprestimo: int,
    dados: EmprestimoAtualizar,
    usuario: dict = Depends(obter_usuario_autenticado)
):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_emprestimo, data_devolucao_real
            FROM emprestimos
            WHERE id_emprestimo = %s
        """, (id_emprestimo,))

        emprestimo_atual = cursor.fetchone()

        if emprestimo_atual is None:
            raise HTTPException(
                status_code=404,
                detail="Empréstimo não encontrado."
            )

        if emprestimo_atual["data_devolucao_real"] is not None:
            raise HTTPException(
                status_code=409,
                detail="Não é possível alterar um empréstimo já devolvido."
            )

        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario = %s",
            (dados.id_usuario,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        cursor.execute(
            "SELECT id_livro FROM livros WHERE id_livro = %s",
            (dados.id_livro,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")

        # Não permitir que outro empréstimo ativo use o mesmo livro.
        cursor.execute("""
            SELECT id_emprestimo
            FROM emprestimos
            WHERE id_livro = %s
              AND id_emprestimo <> %s
              AND data_devolucao_real IS NULL
            LIMIT 1
        """, (dados.id_livro, id_emprestimo))

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Este livro já possui outro empréstimo ativo."
            )

        cursor.execute("""
            UPDATE emprestimos
            SET id_usuario = %s,
                id_livro = %s,
                data_emprestimo = %s,
                data_devolucao_prevista = %s
            WHERE id_emprestimo = %s
        """, (
            dados.id_usuario,
            dados.id_livro,
            dados.data_emprestimo,
            dados.data_devolucao_prevista,
            id_emprestimo
        ))

        conexao.commit()

        return {
            "mensagem": "Empréstimo atualizado com sucesso.",
            "id_emprestimo": id_emprestimo
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None:
            conexao.rollback()
        raise HTTPException(
            status_code=500,
            detail="Não foi possível atualizar o empréstimo."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()



@app.patch(
    "/emprestimos/{id_emprestimo}/devolucao",
    summary="Registrar devolução de livro",
    description="Registra a data real de devolução. Exige autenticação JWT."
)
def registrar_devolucao(
    id_emprestimo: int,
    dados: EmprestimoDevolver,
    usuario: dict = Depends(obter_usuario_autenticado)
):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_emprestimo, data_emprestimo, data_devolucao_real
            FROM emprestimos
            WHERE id_emprestimo = %s
        """, (id_emprestimo,))

        emprestimo = cursor.fetchone()

        if emprestimo is None:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")

        if emprestimo["data_devolucao_real"] is not None:
            raise HTTPException(
                status_code=409,
                detail="Este empréstimo já foi devolvido."
            )

        if dados.data_devolucao_real < emprestimo["data_emprestimo"]:
            raise HTTPException(
                status_code=422,
                detail="A data real de devolução não pode ser anterior ao empréstimo."
            )

        cursor.execute("""
            UPDATE emprestimos
            SET data_devolucao_real = %s
            WHERE id_emprestimo = %s
        """, (dados.data_devolucao_real, id_emprestimo))

        conexao.commit()

        return {
            "mensagem": "Devolução registrada com sucesso.",
            "id_emprestimo": id_emprestimo,
            "data_devolucao_real": dados.data_devolucao_real,
            "status": "devolvido"
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None:
            conexao.rollback()
        raise HTTPException(
            status_code=500,
            detail="Não foi possível registrar a devolução."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()



@app.delete(
    "/emprestimos/{id_emprestimo}",
    summary="Excluir empréstimo",
    description="Exclui um empréstimo já devolvido. Exige autenticação JWT."
)
def excluir_emprestimo(
    id_emprestimo: int,
    usuario: dict = Depends(obter_usuario_autenticado)
):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # 1. Verificar se o empréstimo existe
        cursor.execute("""
            SELECT id_emprestimo, data_devolucao_real
            FROM emprestimos
            WHERE id_emprestimo = %s
        """, (id_emprestimo,))

        emprestimo = cursor.fetchone()

        if emprestimo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empréstimo não encontrado."
            )

        # 2. Não excluir empréstimos ainda ativos
        if emprestimo["data_devolucao_real"] is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não é possível excluir um empréstimo ainda ativo. Registre a devolução primeiro."
            )

        # 3. Excluir o empréstimo devolvido
        cursor.execute("""
            DELETE FROM emprestimos
            WHERE id_emprestimo = %s
        """, (id_emprestimo,))

        conexao.commit()

        return {
            "mensagem": "Empréstimo excluído com sucesso.",
            "id_emprestimo": id_emprestimo
        }

    except HTTPException:
        raise

    except Exception:
        if conexao is not None:
            conexao.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível excluir o empréstimo."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()




@app.get(
    "/emprestimos/usuario/{id_usuario}",
    summary="Consultar empréstimos por usuário",
    description="Lista os empréstimos de um usuário específico."
)
def consultar_emprestimos_por_usuario(id_usuario: int):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Verificar se o usuário existe
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        # Buscar os empréstimos do usuário
        cursor.execute("""
            SELECT
                e.id_emprestimo,
                e.id_usuario,
                u.nome AS nome_usuario,
                e.id_livro,
                l.titulo AS titulo_livro,
                e.data_emprestimo,
                e.data_devolucao_prevista,
                e.data_devolucao_real,
                CASE
                    WHEN e.data_devolucao_real IS NOT NULL THEN 'devolvido'
                    WHEN e.data_devolucao_prevista < CURDATE() THEN 'atrasado'
                    ELSE 'ativo'
                END AS status
            FROM emprestimos e
            INNER JOIN usuarios u ON e.id_usuario = u.id_usuario
            INNER JOIN livros l ON e.id_livro = l.id_livro
            WHERE e.id_usuario = %s
            ORDER BY e.id_emprestimo DESC
        """, (id_usuario,))

        return cursor.fetchall()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível consultar os empréstimos do usuário."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.get(
    "/emprestimos/livro/{id_livro}",
    summary="Consultar empréstimos por livro",
    description="Lista o histórico de empréstimos de um livro específico."
)
def consultar_emprestimos_por_livro(id_livro: int):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Verificar se o livro existe
        cursor.execute(
            "SELECT id_livro FROM livros WHERE id_livro = %s",
            (id_livro,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado."
            )

        # Buscar o histórico de empréstimos do livro
        cursor.execute("""
            SELECT
                e.id_emprestimo,
                e.id_usuario,
                u.nome AS nome_usuario,
                e.id_livro,
                l.titulo AS titulo_livro,
                e.data_emprestimo,
                e.data_devolucao_prevista,
                e.data_devolucao_real,
                CASE
                    WHEN e.data_devolucao_real IS NOT NULL THEN 'devolvido'
                    WHEN e.data_devolucao_prevista < CURDATE() THEN 'atrasado'
                    ELSE 'ativo'
                END AS status
            FROM emprestimos e
            INNER JOIN usuarios u ON e.id_usuario = u.id_usuario
            INNER JOIN livros l ON e.id_livro = l.id_livro
            WHERE e.id_livro = %s
            ORDER BY e.id_emprestimo DESC
        """, (id_livro,))

        return cursor.fetchall()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível consultar o histórico do livro."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()

