
from datetime import date
from pydantic import BaseModel, Field, model_validator


class EmprestimoCadastrar(BaseModel):
    id_usuario: int = Field(
        gt=0,
        description="ID de um usuário já cadastrado"
    )
    id_livro: int = Field(
        gt=0,
        description="ID de um livro já cadastrado"
    )


class EmprestimoAtualizar(BaseModel):
    id_usuario: int = Field(
        gt=0,
        description="ID do usuário responsável pelo empréstimo"
    )
    id_livro: int = Field(
        gt=0,
        description="ID do livro emprestado"
    )
    data_emprestimo: date = Field(
        description="Data em que o empréstimo foi realizado"
    )
    data_devolucao_prevista: date = Field(
        description="Data limite prevista para devolução"
    )

   
    @model_validator(mode="after")
    def validar_datas(self):
        hoje = date.today()

        if self.data_emprestimo > hoje:
            raise ValueError(
                "A data do empréstimo não pode ser futura."
            )

        if self.data_devolucao_prevista < self.data_emprestimo:
            raise ValueError(
                "A data prevista para devolução não pode ser anterior "
                "à data do empréstimo."
            )

        return self



class EmprestimoDevolver(BaseModel):
    data_devolucao_real: date = Field(
        description="Data em que o livro foi efetivamente devolvido"
    )
    
    @model_validator(mode="after")
    def validar_data_devolucao(self):
        hoje = date.today()

        if self.data_devolucao_real > hoje:
            raise ValueError(
                "A data real de devolução não pode ser futura."
            )

        return self



class EmprestimoResposta(BaseModel):
    id_emprestimo: int
    id_usuario: int
    nome_usuario: str
    id_livro: int
    titulo_livro: str
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao_real: date | None = None
    status: str
