# 📚 API Biblioteca — Backend

API REST para gerenciamento de uma biblioteca, desenvolvida com Python e FastAPI, utilizando MySQL para persistência de dados e JWT para autenticação.

O projeto permite gerenciar usuários, autores, livros e empréstimos, incluindo o controle de devoluções e a prevenção de empréstimos simultâneos do mesmo livro.

## 🌐 Acesso à API

- **API em produção:** https://biblioteca-avancada-backend.onrender.com
- **Documentação interativa (Swagger):** https://biblioteca-avancada-backend.onrender.com/docs
- **Repositório:** https://github.com/flaviopcsilva/biblioteca-avancada-backend

> Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub para completar o link do repositório.

## 🚀 Tecnologias utilizadas

- **Python** — linguagem de programação.
- **FastAPI** — desenvolvimento da API REST.
- **Uvicorn** — servidor ASGI.
- **MySQL** — banco de dados relacional.
- **MySQL Connector/Python** — conexão com o banco de dados.
- **Pydantic** — validação e estruturação dos dados.
- **PyJWT** — geração e validação de tokens JWT.
- **Argon2** — hash seguro de senhas.
- **Python Dotenv** — gerenciamento de variáveis de ambiente.
- **Swagger / OpenAPI** — documentação e testes interativos.
- **Git e GitHub** — versionamento e hospedagem do código.
- **Render** — publicação da API.
- **Aiven** — hospedagem do banco de dados MySQL.

## ✨ Funcionalidades

### 🔐 Autenticação

- Login de usuários.
- Autenticação baseada em JWT.
- Hash de senhas utilizando Argon2.
- Consulta dos dados do usuário autenticado.
- Proteção de rotas que exigem autenticação.

### 👥 Usuários

- Cadastro de usuários.
- Listagem de usuários.
- Consulta de usuário por identificador.
- Atualização de usuários.
- Exclusão de usuários.

### ✍️ Autores

- Cadastro de autores.
- Listagem de autores.
- Consulta de autor por identificador.
- Atualização de autores.
- Exclusão de autores.

### 📖 Livros

- Cadastro de livros.
- Listagem de livros.
- Consulta de livro por identificador.
- Atualização de livros.
- Exclusão de livros.

### 🔄 Empréstimos

- Cadastro de empréstimos.
- Listagem de empréstimos.
- Consulta de empréstimo por identificador.
- Atualização de empréstimos.
- Registro de devolução.
- Consulta de empréstimos por usuário.
- Consulta de empréstimos por livro.
- Prevenção de empréstimos ativos duplicados para o mesmo livro, conforme as regras implementadas no banco de dados.

## 📌 Endpoints principais

### Autenticação

| Método | Endpoint      | Descrição                      |
| ------ | ------------- | ------------------------------ |
| POST   | `/auth/login` | Realiza login                  |
| GET    | `/auth/me`    | Consulta o usuário autenticado |

### Usuários

| Método | Endpoint                 | Descrição        |
| ------ | ------------------------ | ---------------- |
| POST   | `/usuarios`              | Cadastra usuário |
| GET    | `/usuarios`              | Lista usuários   |
| GET    | `/usuarios/{id_usuario}` | Consulta usuário |
| PUT    | `/usuarios/{id_usuario}` | Atualiza usuário |
| DELETE | `/usuarios/{id_usuario}` | Exclui usuário   |

### Autores

| Método | Endpoint              | Descrição      |
| ------ | --------------------- | -------------- |
| POST   | `/autores`            | Cadastra autor |
| GET    | `/autores`            | Lista autores  |
| GET    | `/autores/{id_autor}` | Consulta autor |
| PUT    | `/autores/{id_autor}` | Atualiza autor |
| DELETE | `/autores/{id_autor}` | Exclui autor   |

### Livros

| Método | Endpoint             | Descrição      |
| ------ | -------------------- | -------------- |
| POST   | `/livros`            | Cadastra livro |
| GET    | `/livros`            | Lista livros   |
| GET    | `/livros/{id_livro}` | Consulta livro |
| PUT    | `/livros/{id_livro}` | Atualiza livro |
| DELETE | `/livros/{id_livro}` | Exclui livro   |

### Empréstimos

| Método | Endpoint                                 | Descrição                        |
| ------ | ---------------------------------------- | -------------------------------- |
| POST   | `/emprestimos`                           | Cadastra empréstimo              |
| GET    | `/emprestimos`                           | Lista empréstimos                |
| GET    | `/emprestimos/{id_emprestimo}`           | Consulta empréstimo              |
| PUT    | `/emprestimos/{id_emprestimo}`           | Atualiza empréstimo              |
| PATCH  | `/emprestimos/{id_emprestimo}/devolucao` | Registra devolução               |
| DELETE | `/emprestimos/{id_emprestimo}`           | Exclui empréstimo                |
| GET    | `/emprestimos/usuario/{id_usuario}`      | Consulta empréstimos por usuário |
| GET    | `/emprestimos/livro/{id_livro}`          | Consulta empréstimos por livro   |

> Os requisitos de autenticação e os formatos dos dados de cada endpoint podem ser consultados diretamente na documentação Swagger.

## 🗂️ Estrutura do projeto

```text
biblioteca-avancada-backend/
├── conexoes/
│   └── mysql.py
├── schemas/
│   └── ...
├── seguranca/
│   └── ...
├── .env                  # Configurações locais e segredos
├── .gitignore
├── main.py               # Aplicação e endpoints FastAPI
├── requirements.txt      # Dependências Python
├── schema.sql            # Estrutura do banco de dados
└── teste_conexao.py      # Teste de conexão com MySQL
```

A estrutura acima é ilustrativa. Os nomes e arquivos internos das pastas `schemas/` e `seguranca/` podem variar conforme a organização atual do projeto.

O ambiente virtual `.venv/` é criado localmente e não deve ser enviado ao GitHub.

## ⚙️ Como executar localmente

### 1. Pré-requisitos

- Python 3.13 ou outra versão compatível com as dependências do projeto.
- MySQL local ou remoto.
- Git.
- Visual Studio Code ou outra IDE de sua preferência.

### 2. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/biblioteca-avancada-backend.git
cd biblioteca-avancada-backend
```

Substitua `SEU_USUARIO` pelo seu usuário do GitHub.

### 3. Criar o ambiente virtual

No Windows, usando PowerShell:

```powershell
py -3.13 -m venv .venv
```

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto, utilizando o seguinte modelo:

```env
DB_HOST=seu_host_mysql
DB_PORT=3306
DB_NAME=biblioteca
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
JWT_SECRET=sua_chave_secreta
JWT_ALGORITHM=HS256
```

Preencha as variáveis com os dados reais do seu ambiente.

**Importante:** não compartilhe o arquivo `.env` nem envie credenciais para o GitHub.

Para gerar uma chave secreta JWT forte, você pode utilizar:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Guarde o resultado em `JWT_SECRET`, tanto no ambiente local quanto nas variáveis de ambiente do serviço de produção, conforme necessário.

### 6. Configurar o banco de dados

Crie o banco de dados MySQL e aplique o esquema definido em `schema.sql`, caso ele represente a estrutura atual da aplicação.

Confira também se o usuário do banco tem as permissões necessárias e se o servidor permite a conexão a partir do ambiente em que a API será executada.

Se o banco já estiver criado e configurado, não execute novamente scripts que possam apagar ou recriar dados sem antes conferir seu conteúdo.

### 7. Testar a conexão com o MySQL

Se o arquivo `teste_conexao.py` estiver disponível:

```powershell
python teste_conexao.py
```

### 8. Executar a API

```powershell
python -m uvicorn main:app --reload
```

A API ficará disponível localmente em:

- **Aplicação:** http://127.0.0.1:8000
- **Swagger:** http://127.0.0.1:8000/docs
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json

## 🔑 Autenticação com JWT

Para utilizar endpoints protegidos:

1. Acesse a documentação Swagger.
2. Localize o endpoint de login.
3. Envie as credenciais de um usuário válido no formato solicitado pela API.
4. Copie o token JWT retornado.
5. Utilize o botão **Authorize** do Swagger, se disponível, para autorizar as chamadas.
6. Execute os endpoints protegidos.

As credenciais e o token devem ser mantidos em segurança. Não os publique em exemplos, capturas de tela ou repositórios.

## ☁️ Deploy

A aplicação está publicada no Render e utiliza um banco de dados MySQL hospedado no Aiven.

**Configuração de referência para o Render:**

- **Runtime:** Python.
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

Configure no painel do Render as variáveis de ambiente necessárias, como `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET` e `JWT_ALGORITHM`.

As credenciais devem ser configuradas diretamente no ambiente de produção, nunca no código-fonte.

## 🛡️ Boas práticas de segurança

- Armazenamento de senhas por hash com Argon2.
- Autenticação baseada em JWT.
- Configuração por variáveis de ambiente.
- Exclusão de segredos e arquivos locais do controle de versão.
- Validação dos dados recebidos pela API.
- Proteção das rotas que exigem autenticação.

A segurança efetiva depende também das configurações de autorização, das permissões do banco de dados, da gestão dos tokens e da validação de cada endpoint.

## 🧪 Testes

A API pode ser explorada por meio do Swagger:

https://biblioteca-avancada-backend.onrender.com/docs

Os testes automatizados com `pytest` podem ser adicionados para validar os endpoints, a autenticação, as regras de empréstimos e o tratamento de erros.

## 📈 Melhorias futuras

- Implementação de testes automatizados.
- Paginação e filtros nas listagens.
- Melhorias no tratamento e registro de erros.
- Pipeline de integração contínua.
- Interface frontend para gerenciamento da biblioteca.
- Monitoramento e observabilidade da aplicação.

## 👨‍💻 Autor

**Flávio Peres**

Desenvolvedor com foco em desenvolvimento backend, APIs REST e integração com bancos de dados relacionais.

**Tecnologias de interesse:** Python, FastAPI, Node.js, TypeScript, Angular, React, MySQL e PostgreSQL.

- **GitHub:** https://github.com/flaviopcsilva
- **LinkedIn:** https://www.linkedin.com/in/fl%C3%A1vio-cardoso-093391139

---

Desenvolvido como projeto de portfólio para praticar desenvolvimento de APIs REST, autenticação, persistência de dados, documentação e deploy em nuvem.
