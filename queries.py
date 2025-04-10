# Arquivo: queries.py
import pandas as pd
import queries
from utils import get_connection
from database import executar_query_lista
from database import executar_query_df

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

def get_curva_abc(schema: str, data_inicio: str, data_fim: str):
    from database import executar_query_df

    query = f'''
        SELECT 
            oi.codigo AS sku,
            p.nome AS descricao,
            p."tipoVariacao",
            p.marca,
            SUM(CAST(oi.quantidade AS NUMERIC)) AS quantidade_total,
            SUM(CAST(oi.valor_unitario AS NUMERIC) * CAST(oi.quantidade AS NUMERIC)) AS faturamento
        FROM {schema}.tiny_order_item oi
        JOIN {schema}.tiny_orders o ON oi.order_id = o.id
        JOIN {schema}.tiny_nfs nfs ON o.cliente_cpf_cnpj = nfs.cliente_cpf_cnpj
        JOIN {schema}.tiny_products p ON oi.codigo = p.codigo
        WHERE nfs.tipo = 'S' 
          AND nfs.numero_ecommerce IS NOT NULL
          AND nfs."createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        GROUP BY oi.codigo, p.nome, p.marca, p."tipoVariacao"
        ORDER BY faturamento DESC
    '''
    return executar_query_df(query)

def get_curva_abc_por_pai(schema: str, data_inicio: str, data_fim: str):
    query = f"""
        SELECT 
            SPLIT_PART(i.codigo, '-', 1) AS codigo_base
            p.nome,
            p.marca,
            SUM(CAST(i.quantidade AS NUMERIC) * CAST(i.valor_unitario AS NUMERIC)) AS faturamento
        FROM {schema}.tiny_order_item i
        JOIN {schema}.tiny_orders o ON o.id = i.order_id
        JOIN {schema}.tiny_products p ON p.codigo = i.codigo
        WHERE o."createdAt" BETWEEN %s AND %s
        AND p."tipoVariacao" = 'P'
        GROUP BY codigo_base, p.nome, p.marca
        ORDER BY faturamento DESC;
    """
    dados = executar_query_lista(query, (data_inicio, data_fim))
    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados, columns=['produto', 'nome', 'marca', 'faturamento'])
    return df

def get_curva_abc_por_pai(schema: str, data_inicio: str, data_fim: str, marca: str = None):
    filtro_marca = "AND p.marca = %s" if marca and marca != 'Todas' else ""
    params = (data_inicio, data_fim) if not filtro_marca else (data_inicio, data_fim, marca)

    query = f"""
        SELECT 
            LEFT(i.codigo, POSITION('-' IN i.codigo) - 1) AS codigo_base,
            SUM(CAST(i.quantidade AS NUMERIC) * CAST(i.valor_unitario AS NUMERIC)) AS faturamento
        FROM {schema}.tiny_order_item i
        JOIN {schema}.tiny_orders o ON o.id = i.order_id
        JOIN {schema}.tiny_products p ON p.codigo = i.codigo
        WHERE o."createdAt" BETWEEN %s AND %s
        {filtro_marca}
        AND p."tipoVariacao" = 'P'
        GROUP BY codigo_base
        ORDER BY faturamento DESC;
    """
    dados = executar_query_lista(query, params)
    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados, columns=['produto', 'faturamento'])
    return df

def get_curva_abc_por_marca(schema: str, data_inicio: str, data_fim: str, marca: str = None):
    filtro_marca = "AND p.marca = %s" if marca and marca != 'Todas' else ""
    params = (data_inicio, data_fim) if not filtro_marca else (data_inicio, data_fim, marca)

    query = f"""
        SELECT 
            p.marca,
            SUM(CAST(i.quantidade AS NUMERIC) * CAST(i.valor_unitario AS NUMERIC)) AS faturamento
        FROM {schema}.tiny_order_item i
        JOIN {schema}.tiny_orders o ON o.id = i.order_id
        JOIN {schema}.tiny_products p ON p.codigo = i.codigo
        WHERE o."createdAt" BETWEEN %s AND %s
        {filtro_marca}
        AND p."tipoVariacao" = 'P'
        GROUP BY p.marca
        ORDER BY faturamento DESC;
    """
    dados = executar_query_lista(query, params)
    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados, columns=['marca', 'faturamento'])
    df['produto'] = df['marca']
    return df[['produto', 'marca', 'faturamento']]

def get_marcas_disponiveis(schema: str):
    query = f"""
        SELECT DISTINCT marca
        FROM {schema}.tiny_products
        WHERE "tipoVariacao" = 'P'
        ORDER BY marca;
    """
    dados = executar_query_lista(query)
    return [linha[0] for linha in dados if linha[0]]

def get_produtos(schema: str) -> pd.DataFrame:
    query = f"""
        SELECT codigo, nome, marca, "tipoVariacao"
        FROM {schema}.tiny_products
        WHERE "tipoVariacao" IS NOT NULL
    """
    return executar_query_df(query)

def get_produtos_por_status(schema, start_date, end_date, status='Todos'):
    if status == 'Todos':
        query = f"""
            SELECT codigo, nome, estoque, preco, categoria, preco_custo_medio
            FROM {schema}.tiny_products
        """
    elif status == 'Vendidos':
        query = f"""
            SELECT DISTINCT p.codigo, p.nome, p.estoque, p.preco, p.categoria, p.preco_custo_medio
            FROM {schema}.tiny_nfs nf
            JOIN {schema}.tiny_orders o ON nf.cliente_cpf_cnpj = o.cliente_cpf_cnpj
            JOIN {schema}.tiny_order_item oi ON o.id = oi.order_id
            JOIN {schema}.tiny_products p ON oi.codigo = p.codigo
            WHERE nf.tipo = 'S'
              AND nf."createdAt" BETWEEN '{start_date}' AND '{end_date}'
        """
    elif status == 'Sem Venda':
        query = f"""
            SELECT codigo, nome, estoque, preco, categoria, preco_custo_medio
            FROM {schema}.tiny_products
            WHERE codigo NOT IN (
                SELECT DISTINCT oi.codigo
                FROM {schema}.tiny_nfs nf
                JOIN {schema}.tiny_orders o ON nf.cliente_cpf_cnpj = o.cliente_cpf_cnpj
                JOIN {schema}.tiny_order_item oi ON o.id = oi.order_id
                WHERE nf.tipo = 'S'
                  AND nf."createdAt" BETWEEN '{start_date}' AND '{end_date}'
            )
        """
    else:
        return []

    df = execute_query(schema, query)
    return df.to_dict(orient="records")

def get_media_vendas_diarias(schema, data_inicio, data_fim):
    query = f"""
        SELECT oi.codigo, SUM(oi.quantidade::numeric) / 90 AS media_diaria
        FROM {schema}.tiny_nfs nf
        JOIN {schema}.tiny_orders o ON nf.cliente_cpf_cnpj = o.cliente_cpf_cnpj
        JOIN {schema}.tiny_order_item oi ON o.id = oi.order_id
        WHERE nf.tipo = 'S'
        AND nf."createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        GROUP BY oi.codigo
    """
    df = execute_query(schema, query)
    return {row['codigo']: row['media_diaria'] for _, row in df.iterrows()}

def get_ultima_venda_por_produto(schema, data_inicio, data_fim):
    query = f"""
        SELECT oi.codigo, MAX(nf."createdAt") AS ultima_venda
        FROM {schema}.tiny_nfs nf
        JOIN {schema}.tiny_orders o ON nf.cliente_cpf_cnpj = o.cliente_cpf_cnpj
        JOIN {schema}.tiny_order_item oi ON o.id = oi.order_id
        WHERE nf.tipo = 'S'
        AND nf."createdAt" BETWEEN '{data_inicio}' AND '{data_fim}'
        GROUP BY oi.codigo
    """
    df = execute_query(schema, query)
    return {row['codigo']: row['ultima_venda'] for _, row in df.iterrows()}
