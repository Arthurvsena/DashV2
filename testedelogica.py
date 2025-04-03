import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

def main():
    load_dotenv(dotenv_path=".env")
    # Dados de conexão com o banco de dados (altere com seus dados reais)
    user = os.getenv("POSTGRESQL_USER")
    password = os.getenv("POSTGRESQL_PASSWORD")
    host = os.getenv("POSTGRESQL_HOST")
    port = os.getenv("POSTGRESQL_PORT", "5432")
    db = os.getenv("POSTGRESQL_DB")

    try:
        # Conexão com o banco de dados
        conn = psycopg2.connect(
            host=host,
            dbname=db,
            user=user,
            password=password,
            port=port
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")

        # Cursor para executar as consultas
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execução da consulta SQL
        cursor.execute("""
        WITH devolucoes AS (
            SELECT o.cliente_cpf_cnpj, oi.descricao, COUNT(*) AS num_devolucoes
            FROM apj_tiny.tiny_nfs nf
            INNER JOIN apj_tiny.tiny_orders o ON nf.cliente_cpf_cnpj = o.cliente_cpf_cnpj
            INNER JOIN apj_tiny.tiny_order_item oi ON o.id = oi.order_id
            WHERE nf.tipo = 'E' -- Notas de devolução
            GROUP BY o.cliente_cpf_cnpj, oi.descricao
        ),
        saidas AS (
            SELECT DISTINCT cliente_cpf_cnpj
            FROM apj_tiny.tiny_nfs
            WHERE tipo = 'S' -- Notas de saída
        )
        SELECT d.descricao, d.num_devolucoes
        FROM devolucoes d
        INNER JOIN saidas s ON d.cliente_cpf_cnpj = s.cliente_cpf_cnpj
        ORDER BY d.num_devolucoes DESC
        LIMIT 3;
        """)

        # Obtenção do resultado
        produtos_mais_devolvidos = cursor.fetchall()
        if produtos_mais_devolvidos:
            print("Produtos mais devolvidos:")
            for produto in produtos_mais_devolvidos:
                print(f"- {produto['descricao']} com {produto['num_devolucoes']} devoluções.")
        else:
            print("Nenhum produto devolvido encontrado.")

    except Exception as e:
        print("Erro ao conectar com o banco de dados:", str(e))
    finally:
        # Fechar o cursor e a conexão com o banco
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()
