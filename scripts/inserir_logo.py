import os
import psycopg2
from dotenv import load_dotenv

# 🔄 Carrega variáveis do .env
load_dotenv(dotenv_path=".env")

# Caminho absoluto da imagem no seu computador
CAMINHO_IMAGEM = r"C:\Users\Petronio - Dados\Documents\GitHub\Dashboards_V1\scripts\logo_help.png"

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRESQL_DB"),
        user=os.getenv("POSTGRESQL_USER"),
        password=os.getenv("POSTGRESQL_PASSWORD"),
        host=os.getenv("POSTGRESQL_HOST"),
        port=os.getenv("POSTGRESQL_PORT", "5432")
    )

def inserir_logo():
    with open(CAMINHO_IMAGEM, "rb") as f:
        imagem_bytes = f.read()

    conn = get_connection()
    cur = conn.cursor()

    # 🔁 Insere ou atualiza a logo na linha com id = 1
    cur.execute("""
        INSERT INTO public.global_config (id, logo)
        VALUES (1, %s)
        ON CONFLICT (id) DO UPDATE SET logo = EXCLUDED.logo;
    """, (psycopg2.Binary(imagem_bytes),))

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Logo inserida/atualizada com sucesso no banco de dados.")

if __name__ == "__main__":
    inserir_logo()
