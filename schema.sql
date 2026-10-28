create database biblioteca;

CREATE TABLE autores(
id_autor int primary key auto_increment,
nome varchar(100) not null,
nacionalidade varchar(50)
);

CREATE TABLE livros(
id_livros int primary key auto_increment,
titulo varchar (150) not null,
ano_publicacao int,
id_autor int,
FOREIGN KEY (id_autor) REFERENCES autores (id_autor)
);

CREATE TABLE USUARIOS (
		id_usuario int primary key auto_increment,
		nome varchar(100) not null,
		email varchar(50) not null unique
		);

alter table livros add categoria varchar(50);

ALTER TABLE livros
CHANGE COLUMN id_livros id_livro INT AUTO_INCREMENT;

create table emprestimos(
  id_emprestimo int primary key auto_increment,
  id_usuario int,
  foreign key (id_usuario) references usuarios (id_usuario),
  id_livro int,
  foreign key (id_livro) references livros (id_livro),
  data_emprestimo date,
  data_devolucao date
);

ALTER TABLE usuarios
ADD COLUMN senha_hash VARCHAR(255) NOT NULL;

ALTER TABLE usuarios
MODIFY COLUMN senha VARCHAR(30) NULL;