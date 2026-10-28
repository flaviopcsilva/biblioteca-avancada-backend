import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        ssl_disabled=False,
        connection_timeout=10
    )