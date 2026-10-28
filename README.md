# 📚 API Biblioteca Avançada

API REST para gerenciamento de uma biblioteca, desenvolvida com Python, FastAPI e MySQL. O projeto implementa operações de cadastro, consulta, atualização e exclusão de autores, livros, usuários e empréstimos, além de autenticação com JWT e documentação interativa com Swagger.

O projeto foi desenvolvido para praticar conceitos de desenvolvimento backend, APIs REST, validação de dados, segurança e integração com banco de dados relacional.

## 🚀 Tecnologias utilizadas

- **Python** — linguagem de programação.
- **FastAPI** — framework para construção da API REST.
- **MySQL 8.4** — banco de dados relacional.
- **MySQL Connector/Python** — conexão com o banco de dados.
- **Pydantic** — validação e estruturação dos dados.
- **JWT** — autenticação baseada em tokens.
- **Argon2** — hash seguro de senhas.
- **python-dotenv** — gerenciamento de variáveis de ambiente.
- **Swagger UI** — documentação e testes interativos.
- **Aiven** — hospedagem do banco de dados MySQL.
- **Render** — plataforma planejada para hospedagem da API.

## ✨ Funcionalidades

### Autenticação e usuários

- Cadastro de usuários.
- Consulta, atualização e exclusão de usuários.
- Armazenamento de senhas com hash Argon2.
- Login com e-mail e senha.
- Geração e validação de tokens JWT.
- Consulta do usuário autenticado.
- Proteção de operações de escrita por autenticação.

### Autores

- Cadastrar autores.
- Listar autores.
- Consultar autor por ID.
- Atualizar autores.
- Excluir autores.

### Livros

- Cadastrar livros vinculados a autores.
- Listar livros com informações dos autores.
- Consultar livro por ID.
- Atualizar livros.
- Excluir livros com tratamento de restrições de integridade.

### Empréstimos

- Cadastrar empréstimos com prazo padrão de 14 dias.
- Listar todos os empréstimos.
- Consultar empréstimo por ID.
- Consultar empréstimos por usuário.
- Consultar histórico de empréstimos por livro.
- Atualizar dados de empréstimos ativos.
- Registrar a data real da devolução.
- Identificar empréstimos ativos, atrasados e devolvidos.
- Impedir empréstimos ativos duplicados para o mesmo livro.
- Excluir empréstimos devolvidos.

## 🛠️ Pré-requisitos

Antes de executar o projeto, instale:

- Python compatível com as dependências utilizadas.
- Git.
- Visual Studio Code ou outra IDE de sua preferência.
- Uma instância MySQL acessível.
- Beekeeper Studio ou outro cliente SQL para administrar o banco, se necessário.

## 📁 Estrutura do projeto

```text
biblioteca-avancada-backend/
├── conexoes/
│   └── mysql.py
├── schemas/
│   ├── erros.py
│   ├── usuarios.py
│   ├── login.py
│   └── emprestimos.py
├── seguranca/
│   ├── senhas.py
│   └── tokens.py
├── .env
├── .gitignore
├── main.py
├── schema.sql
├── teste_conexao.py
└── requirements.txt
```

A estrutura acima representa os principais arquivos conhecidos do projeto. Outros módulos e schemas podem ser adicionados conforme a evolução da aplicação.

## ⚙️ Instalação

### 1. Clonar o repositório

Depois de publicar o projeto no GitHub, execute:

```bash
git clone URL_DO_SEU_REPOSITORIO
cd biblioteca-avancada-backend
```

Substitua `URL_DO_SEU_REPOSITORIO` pelo endereço real do repositório.

### 2. Criar o ambiente virtual

No Windows, usando PowerShell:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, consulte as políticas de execução do seu ambiente ou utilize o terminal CMD.

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` deve conter as dependências necessárias para executar a aplicação.

### 4. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=seu_host_mysql
DB_PORT=3306
DB_NAME=biblioteca
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

JWT_SECRET=sua_chave_secreta
JWT_ALGORITHM=HS256
```

Substitua os valores de exemplo pelas configurações do seu banco de dados e gere uma chave JWT forte e aleatória.

**Segurança:** nunca publique o arquivo `.env`, senhas, tokens ou chaves privadas no GitHub.

### 5. Preparar o banco de dados

Crie o banco `biblioteca` e configure as tabelas necessárias utilizando o arquivo `schema.sql` e os comandos SQL definidos durante o desenvolvimento.

O banco precisa conter as tabelas de autores, livros, usuários e empréstimos, além das chaves estrangeiras e da restrição de empréstimos ativos duplicados.

Se estiver utilizando a instância Aiven já configurada, confira os parâmetros de conexão e os requisitos de SSL fornecidos pelo serviço.

### 6. Executar a API

Com o ambiente virtual ativado, execute:

```powershell
python -m uvicorn main:app --reload
```

A aplicação estará disponível localmente em:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## 🔐 Autenticação JWT

Para acessar as operações protegidas:

1. Execute `POST /auth/login`.
2. Informe o e-mail e a senha de um usuário cadastrado.
3. Copie o valor de `access_token` retornado.
4. Clique em **Authorize** no Swagger.
5. Informe o token e confirme a autorização.
6. Execute as operações protegidas.

Os tokens possuem validade limitada. Após a expiração, será necessário autenticar novamente.

## 📡 Principais endpoints

Os endpoints abaixo representam as rotas implementadas no projeto.

| Método | Endpoint                                 | Descrição                         |
| ------ | ---------------------------------------- | --------------------------------- |
| POST   | `/auth/login`                            | Autenticar usuário                |
| GET    | `/auth/me`                               | Consultar usuário autenticado     |
| POST   | `/usuarios`                              | Cadastrar usuário                 |
| GET    | `/usuarios`                              | Listar usuários                   |
| GET    | `/usuarios/{id_usuario}`                 | Consultar usuário                 |
| PUT    | `/usuarios/{id_usuario}`                 | Atualizar usuário                 |
| DELETE | `/usuarios/{id_usuario}`                 | Excluir usuário                   |
| POST   | `/autores`                               | Cadastrar autor                   |
| GET    | `/autores`                               | Listar autores                    |
| GET    | `/autores/{id_autor}`                    | Consultar autor                   |
| PUT    | `/autores/{id_autor}`                    | Atualizar autor                   |
| DELETE | `/autores/{id_autor}`                    | Excluir autor                     |
| POST   | `/livros`                                | Cadastrar livro                   |
| GET    | `/livros`                                | Listar livros                     |
| GET    | `/livros/{id_livro}`                     | Consultar livro                   |
| PUT    | `/livros/{id_livro}`                     | Atualizar livro                   |
| DELETE | `/livros/{id_livro}`                     | Excluir livro                     |
| POST   | `/emprestimos`                           | Cadastrar empréstimo              |
| GET    | `/emprestimos`                           | Listar empréstimos                |
| GET    | `/emprestimos/{id_emprestimo}`           | Consultar empréstimo              |
| GET    | `/emprestimos/usuario/{id_usuario}`      | Consultar empréstimos por usuário |
| GET    | `/emprestimos/livro/{id_livro}`          | Consultar histórico por livro     |
| PUT    | `/emprestimos/{id_emprestimo}`           | Atualizar empréstimo              |
| PATCH  | `/emprestimos/{id_emprestimo}/devolucao` | Registrar devolução               |
| DELETE | `/emprestimos/{id_emprestimo}`           | Excluir empréstimo                |

As operações de escrita protegidas exigem autenticação JWT. Consulte o Swagger para conferir os parâmetros, os schemas e as respostas de cada rota.

## 🧪 Testes

A API pode ser testada pelo Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Os testes realizados durante o desenvolvimento incluíram:

- Cadastro e consulta de autores.
- Cadastro e consulta de livros.
- Cadastro e gerenciamento de usuários.
- Autenticação e validação de JWT.
- Cadastro e consulta de empréstimos.
- Registro de devolução.
- Consultas por ID de usuário e de livro.
- Tratamento de registros inexistentes.
- Validação de datas.
- Proteção contra empréstimos ativos duplicados.

## ☁️ Publicação

A publicação está planejada para o GitHub e o Render.

Antes de disponibilizar a API publicamente, é necessário:

1. Enviar o código ao GitHub sem arquivos secretos.
2. Configurar as variáveis de ambiente no Render.
3. Configurar o comando de instalação e o comando de inicialização da aplicação.
4. Verificar a conectividade do Render com o MySQL hospedado na Aiven.
5. Testar a API publicada e sua documentação Swagger.

A publicação da aplicação não migra o banco de dados automaticamente.

## 🔒 Segurança

O projeto utiliza hash Argon2 para senhas, autenticação JWT e consultas SQL parametrizadas.

Antes de utilizar a aplicação em produção, recomenda-se revisar o tratamento de erros, a autorização por usuário, a configuração de SSL, a gestão de segredos e as regras de integridade do banco.

## 👨‍💻 Autor

Desenvolvido como projeto de estudo e portfólio na área de desenvolvimento backend com Python, APIs REST, FastAPI e bancos de dados relacionais.
