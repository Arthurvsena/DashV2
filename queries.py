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

def get_produto_campeao(schema, data_inicio, data_fim):
    from utils import get_connection
    conn = get_connection()
    cur = conn.cursor()
    print("Executando busca do produto campeão")
    print("Schema:", schema)
    print("Data início:", data_inicio)
    print("Data fim:", data_fim)


    query = f'''
        WITH notas_saida AS (
    SELECT REGEXP_REPLACE(cliente_cpf_cnpj, '[^0-9]', '', 'g') AS cpf_cnpj
    FROM {schema}.tiny_nfs
        WHERE tipo = 'S' AND "createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
    ),
    pedidos_filtrados AS (
        SELECT id FROM {schema}.tiny_orders
        WHERE REGEXP_REPLACE(cliente_cpf_cnpj, '[^0-9]', '', 'g') IN (SELECT cpf_cnpj FROM notas_saida)
    ),
    itens_venda AS (
        SELECT descricao, valor_unitario FROM {schema}.tiny_order_item
        WHERE order_id IN (SELECT id FROM pedidos_filtrados)
    )
    SELECT descricao, SUM(valor_unitario::numeric) AS total
    FROM itens_venda
    GROUP BY descricao
    ORDER BY total DESC
    LIMIT 1;

    '''
    print("DEBUG QUERY:", query)
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_total_produtos_vendidos(schema, data_inicio, data_fim):
    from utils import get_connection
    conn = get_connection()
    cur = conn.cursor()

    query = f"""
        WITH notas_saida AS (
            SELECT cliente_cpf_cnpj FROM {schema}.tiny_nfs
            WHERE tipo = 'S' AND "createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        ),
        pedidos_filtrados AS (
            SELECT id FROM {schema}.tiny_orders
            WHERE cliente_cpf_cnpj IN (SELECT cliente_cpf_cnpj FROM notas_saida)
        ),
        itens_venda AS (
            SELECT quantidade FROM {schema}.tiny_order_item
            WHERE order_id IN (SELECT id FROM pedidos_filtrados)
        )
        SELECT SUM(quantidade::numeric) FROM itens_venda;
    """
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return int(result[0]) if result and result[0] else 0

def get_produto_mais_devolvido(schema, data_inicio, data_fim):
    from utils import get_connection
    conn = get_connection()
    cur = conn.cursor()

    print("🔍 Executando busca do produto mais devolvido")
    print(f"Schema: {schema}")
    print(f"Data início: {data_inicio}")
    print(f"Data fim: {data_fim}")

    query = f"""
        WITH notas_saida AS (
            SELECT cliente_cpf_cnpj
            FROM {schema}.tiny_nfs
            WHERE tipo = 'S'
            AND "createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        ),
        notas_entrada AS (
            SELECT cliente_cpf_cnpj
            FROM {schema}.tiny_nfs
            WHERE tipo = 'E'
            AND "createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        ),
        pedidos_com_devolucao AS (
            SELECT id, cliente_cpf_cnpj
            FROM {schema}.tiny_orders
            WHERE cliente_cpf_cnpj IN (SELECT cliente_cpf_cnpj FROM notas_saida)
              AND cliente_cpf_cnpj IN (SELECT cliente_cpf_cnpj FROM notas_entrada)
        ),
        itens_devolvidos AS (
            SELECT codigo, descricao
            FROM {schema}.tiny_order_item
            WHERE order_id IN (SELECT id FROM pedidos_com_devolucao)
        )
        SELECT descricao, COUNT(*) AS total_devolucoes
        FROM itens_devolvidos
        GROUP BY descricao
        ORDER BY total_devolucoes DESC
        LIMIT 1;
    """

    try:
        cur.execute(query)
        result = cur.fetchone()
    except Exception as e:
        print(f"Erro na consulta de devoluções: {e}")
        result = None
    finally:
        cur.close()
        conn.close()

    # 🔐 Retorno seguro, sempre uma tupla
    if isinstance(result, tuple) and len(result) == 2:
        return result
    return ('-', 0)

def get_top_devolved_products_query(schema):
    query = f"""
    WITH devolucoes AS (
        SELECT oi.descricao, COUNT(*) AS num_devolucoes
        FROM {schema}.tiny_nfs nf
        INNER JOIN {schema}.tiny_orders o ON nf.cliente_cpf_cnpj = o.cliente_cpf_cnpj
        INNER JOIN {schema}.tiny_order_item oi ON o.id = oi.order_id
        WHERE nf.tipo = 'E'
        GROUP BY oi.descricao
    )
    SELECT descricao, num_devolucoes
    FROM devolucoes
    ORDER BY num_devolucoes DESC
    LIMIT 3;
    """
    return execute_query(schema, query)

def get_total_produtos_sem_venda(schema, data_inicio, data_fim):
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        WITH notas_saida AS (
            SELECT REGEXP_REPLACE(cliente_cpf_cnpj, '[^0-9]', '', 'g') AS cpf_cnpj
            FROM {schema}.tiny_nfs
            WHERE tipo = 'S' AND "createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        ),
        pedidos_filtrados AS (
            SELECT id
            FROM {schema}.tiny_orders
            WHERE REGEXP_REPLACE(cliente_cpf_cnpj, '[^0-9]', '', 'g') IN (SELECT cpf_cnpj FROM notas_saida)
        ),
        produtos_vendidos AS (
            SELECT DISTINCT codigo
            FROM {schema}.tiny_order_item
            WHERE order_id IN (SELECT id FROM pedidos_filtrados)
        )
        SELECT COUNT(*) AS total_sem_venda
        FROM {schema}.tiny_products
        WHERE codigo IS NOT NULL
        AND codigo NOT IN (SELECT codigo FROM produtos_vendidos);
    """
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else 0

def get_faturamento_por_estado(schema, data_inicio, data_fim):
    conn = get_connection()
    cur = conn.cursor()
    query = f"""
        WITH notas_saida AS (
            SELECT REGEXP_REPLACE(cliente_cpf_cnpj, '[^0-9]', '', 'g') AS cpf_cnpj
            FROM {schema}.tiny_nfs
            WHERE tipo = 'S' AND "createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        ),
        pedidos_filtrados AS (
            SELECT cliente_uf, total_pedido
            FROM {schema}.tiny_orders
            WHERE REGEXP_REPLACE(cliente_cpf_cnpj, '[^0-9]', '', 'g') IN (SELECT cpf_cnpj FROM notas_saida)
        )
        SELECT cliente_uf AS estado, SUM(total_pedido::numeric) AS total_faturado
        FROM pedidos_filtrados
        WHERE cliente_uf IS NOT NULL
        GROUP BY cliente_uf
        ORDER BY total_faturado DESC;
    """
    cur.execute(query)
    resultados = cur.fetchall()
    cur.close()
    conn.close()
    return [{"estado": r[0], "valor": float(r[1])} for r in resultados]
