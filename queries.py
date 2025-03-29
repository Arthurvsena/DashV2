# Arquivo: queries.py
import pandas as pd
from utils import get_connection

def execute_query(schema, query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=columns)

def get_orders_query(schema, start_date, end_date):
    query = f"""
        SELECT id, data_pedido, cliente_cpf_cnpj, numero_ecommerce, forma_pagamento, forma_envio
        FROM {schema}.tiny_orders
        WHERE TO_DATE(data_pedido, 'DD/MM/YYYY') BETWEEN '{start_date}' AND '{end_date}';
    """
    return execute_query(schema, query)

def get_nfs_query(schema, start_date, end_date):
    query = f"""
        SELECT 
            id,
            cliente_cpf_cnpj,
            tipo,
            valor_frete,
            valor,
            numero_ecommerce,
            endereco_entrega_uf,
            "createdAt",
            numero
        FROM {schema}.tiny_nfs
        WHERE DATE("createdAt") BETWEEN '{start_date}' AND '{end_date}';
    """
    return execute_query(schema, query)

def get_order_item_query(schema, start_date, end_date):
    query = f"""
        SELECT 
            oi.order_id,
            oi.codigo AS sku,
            oi.descricao,
            oi.quantidade,
            oi.valor_unitario,
            (CAST(oi.valor_unitario AS NUMERIC) * CAST(oi.quantidade AS NUMERIC)) AS valor_total
        FROM {schema}.tiny_order_item oi
        JOIN {schema}.tiny_orders o ON oi.order_id = o.id
        WHERE DATE(oi."createdAt") BETWEEN '{start_date}' AND '{end_date}';
    """
    return execute_query(schema, query)

def get_valor_total_faturado_query(schema, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        SELECT SUM(CAST(nfs.valor AS NUMERIC)) AS valor_total_faturado
        FROM {schema}.tiny_nfs nfs
        WHERE nfs.tipo = 'S'
          AND nfs.cliente_cpf_cnpj IN (
              SELECT cliente_cpf_cnpj
              FROM {schema}.tiny_orders
              WHERE cliente_cpf_cnpj IS NOT NULL
          )
          AND nfs."createdAt" BETWEEN '{start_date}' AND '{end_date}';
    """
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result or 0

def get_products_query(schema):
    query = f"""
        SELECT 
            codigo, 
            nome, 
            categoria,
            estoque,
            preco_custo,
            preco,
            "tipoVariacao",
            marca
        FROM {schema}.tiny_products;
    """
    return execute_query(schema, query)

def get_pareto_data_query(schema, start_date, end_date):
    query = f"""
        SELECT 
            oi.codigo AS sku,
            p.nome AS descricao,
            p."tipoVariacao",
            SUM(CAST(oi.quantidade AS NUMERIC)) AS quantidade_total,
            SUM(CAST(oi.valor_unitario AS NUMERIC) * CAST(oi.quantidade AS NUMERIC)) AS faturamento
        FROM {schema}.tiny_order_item oi
        JOIN {schema}.tiny_orders o ON oi.order_id = o.id
        JOIN {schema}.tiny_nfs nfs ON o.cliente_cpf_cnpj = nfs.cliente_cpf_cnpj
        JOIN {schema}.tiny_products p ON oi.codigo = p.codigo
        WHERE nfs.tipo = 'S' 
          AND nfs.numero_ecommerce IS NOT NULL
          AND nfs."createdAt" BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY oi.codigo, p.nome, p."tipoVariacao"
        ORDER BY faturamento DESC;
    """
    return execute_query(schema, query)

def get_ticket_medio_query(schema, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        SELECT 
            SUM(CAST(oi.valor_unitario AS NUMERIC) * CAST(oi.quantidade AS NUMERIC)) AS total_faturado,
            SUM(CAST(oi.quantidade AS NUMERIC)) AS total_quantidade
        FROM {schema}.tiny_order_item oi
        JOIN {schema}.tiny_orders o ON oi.order_id = o.id
        JOIN {schema}.tiny_nfs nfs ON o.cliente_cpf_cnpj = nfs.cliente_cpf_cnpj
        WHERE nfs.tipo = 'S'
          AND nfs."createdAt" BETWEEN '{start_date}' AND '{end_date}';
    """
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return {
        "total_faturado": result[0] or 0,
        "total_quantidade": result[1] or 0
    }

#def get_mapa_query(schema):
  #  query = f'''
   #     SELECT estado, quantidade, preco
    #    FROM {schema}.tiny_order_item
     #   WHERE estado IS NOT NULL
    #'''
    #return execute_query(schema, query)

def get_top_10_produtos_query(schema):
    query = f'''
         SELECT codigo AS produto_id, SUM(CAST(quantidade AS NUMERIC)) AS total_vendido
         FROM {schema}.tiny_order_item
         GROUP BY codigo
         ORDER BY total_vendido DESC
         LIMIT 10
     '''  
    return query  # Apenas retorna a string, a execução fica com load_data(query)

def get_categorias_query(schema):
    query = f'''
        SELECT p.categoria, SUM(CAST(oi.quantidade AS NUMERIC)) as quantidade_total
        FROM {schema}.tiny_order_item oi
        JOIN {schema}.tiny_products p ON oi.codigo = p.codigo
        GROUP BY p.categoria
        ORDER BY quantidade_total DESC
    '''
    return execute_query(schema, query)
def get_valor_total_frete_query(schema: str, start_date: str, end_date: str):
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        SELECT SUM(CAST(nfs.valor_frete AS NUMERIC)) AS valor_total_frete
        FROM {schema}.tiny_nfs nfs
        WHERE nfs.tipo = 'S'
          AND nfs.cliente_cpf_cnpj IN (
              SELECT cliente_cpf_cnpj
              FROM {schema}.tiny_orders
              WHERE cliente_cpf_cnpj IS NOT NULL
          )
          AND nfs."createdAt" BETWEEN '{start_date}' AND '{end_date}';
    """
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result or 0

def get_valor_total_devolucao_query(schema: str, start_date: str, end_date: str):
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        SELECT SUM(CAST(nfs.valor AS NUMERIC)) AS valor_total_devolucao
        FROM {schema}.tiny_nfs nfs
        WHERE nfs.tipo = 'E'
          AND nfs.cliente_cpf_cnpj IN (
              SELECT cliente_cpf_cnpj
              FROM {schema}.tiny_orders
              WHERE cliente_cpf_cnpj IS NOT NULL
          )
          AND nfs."createdAt" BETWEEN '{start_date}' AND '{end_date}';
    """
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result or 0

def get_faturamento_por_marketplace_query(schema: str, start_date: str, end_date: str):
    query = f"""
        SELECT
            o.forma_pagamento AS marketplace,
            DATE(nfs."createdAt") AS data,
            SUM(CAST(nfs.valor AS NUMERIC)) AS valor_total
        FROM {schema}.tiny_nfs nfs
        JOIN {schema}.tiny_orders o
          ON o.cliente_cpf_cnpj = nfs.cliente_cpf_cnpj
        WHERE nfs.tipo = 'S'
          AND nfs."createdAt" BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY o.forma_pagamento, DATE(nfs."createdAt")
        ORDER BY data ASC;
    """
    return execute_query(schema, query)

def get_faturamento_mensal_query(schema: str):
    return f"""
        SELECT
            TO_CHAR(nfs."createdAt", 'YYYY-MM') AS mes,
            COUNT(DISTINCT o.id) AS total_pedidos,
            SUM(CAST(oi.quantidade AS NUMERIC) * CAST(oi.valor_unitario AS NUMERIC)) AS faturamento
        FROM {schema}.tiny_nfs nfs
        JOIN {schema}.tiny_orders o ON o.cliente_cpf_cnpj = nfs.cliente_cpf_cnpj
        JOIN {schema}.tiny_order_item oi ON oi.order_id = o.id
        WHERE nfs.tipo = 'S'
        AND nfs."createdAt" >= (CURRENT_DATE - INTERVAL '12 months')
        GROUP BY mes
        ORDER BY mes
    """