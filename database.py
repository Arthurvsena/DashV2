# Arquivo: database.py
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import psycopg2

# Carrega variáveis de ambiente do .env
load_dotenv(dotenv_path=".env")

# Leitura segura das credenciais
user = os.getenv("POSTGRESQL_USER")
password = os.getenv("POSTGRESQL_PASSWORD")
host = os.getenv("POSTGRESQL_HOST")
port = os.getenv("POSTGRESQL_PORT", "5432")
db = os.getenv("POSTGRESQL_DB")

# URL padrão SQLAlchemy
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

# Cria a engine para uso com pandas/sqlalchemy
engine = create_engine(DATABASE_URL)

def get_connection():
    """Conexão direta via psycopg2."""
    return psycopg2.connect(
        dbname=db,
        user=user,
        password=password,
        host=host,
        port=port
    )

def executar_comando(query, params=None):
    """Executa um comando SQL (INSERT, UPDATE, DELETE) com commit automático."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
