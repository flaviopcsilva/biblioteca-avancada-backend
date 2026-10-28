
from conexoes.mysql import conectar

try:
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT DATABASE()")
    print("Banco conectado:", cursor.fetchone()[0])

    cursor.execute("SHOW TABLES")
    print("\nTabelas encontradas:")

    for tabela in cursor.fetchall():
        print("-", tabela[0])

    cursor.close()
    conexao.close()

except Exception as erro:
    print("Erro na conexão:", erro)
