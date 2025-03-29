from nicegui import ui
import pandas as pd
from queries import (
    get_orders_query,
    get_nfs_query,
    get_order_item_query,
    get_products_query
)

def grafico_categoria_interativo(start_date, end_date, schema):
    with ui.card().classes('bg-gray-900 text-white w-full'):
        ui.label('📊 Gráfico Interativo por Categoria').classes('text-lg font-bold mb-4')

        # Carrega dados
        df_nfs = get_nfs_query(schema, start_date, end_date)
        df_orders = get_orders_query(schema, start_date, end_date)
        df_items = get_order_item_query(schema, start_date, end_date)
        df_products = get_products_query(schema)

        # Filtra notas de saída
        df_nfs = df_nfs[df_nfs['tipo'].str.upper() == 'S'].copy()

        # Junta tudo
        df_merged = df_items.merge(df_orders, left_on='order_id', right_on='id') \
                             .merge(df_nfs, on='cliente_cpf_cnpj') \
                             .merge(df_products, left_on='sku', right_on='codigo')

        df_merged['quantidade'] = pd.to_numeric(df_merged['quantidade'], errors='coerce')
        df_merged['valor_unitario'] = pd.to_numeric(df_merged['valor_unitario'], errors='coerce')
        df_merged['faturamento'] = df_merged['quantidade'] * df_merged['valor_unitario']
        df_merged['faturamento'] = df_merged['faturamento'].fillna(0)

        df_merged['categoria'] = df_merged['categoria'].astype(str).str.strip()
        df_merged[['categoria_base', 'subcategoria']] = df_merged['categoria'].str.split('>>', expand=True)
        df_merged['categoria_base'] = df_merged['categoria_base'].str.strip().fillna('Sem categoria')
        df_merged['subcategoria'] = df_merged['subcategoria'].str.strip().fillna('Sem subcategoria')

        df_categoria = df_merged.groupby("categoria_base")["faturamento"].sum().reset_index()
        df_subcategoria = df_merged.groupby(["categoria_base", "subcategoria"])["faturamento"].sum().reset_index()

        def atualizar_grafico(dados, titulo, label_col):
            return {
                "tooltip": {"trigger": "item", "backgroundColor": "#000000", "textStyle": {"color": "#FFFFFF"}},
                "legend": {"top": "5%", "left": "center", "textStyle": {"color": "#FFFFFF"}},
                "series": [{
                    "top": 40,
                    "name": titulo,
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "label": {"show": False, "position": "center"},
                    "emphasis": {"label": {"show": True, "fontSize": 18, "fontWeight": "bold"}},
                    "labelLine": {"show": False},
                    "data": [
                        {"name": row[label_col], "value": row['faturamento']} for _, row in dados.iterrows()
                    ]
                }]
            }

        # Layout lado a lado
        with ui.row().classes("w-full justify-between items-start gap-4").style("display: flex"):
            # Gráfico de categorias
            categoria_inicial = df_categoria.iloc[0]['categoria_base'] if not df_categoria.empty else 'Sem categoria'
            dados_iniciais = df_subcategoria[df_subcategoria['categoria_base'] == categoria_inicial]

            chart_categoria = ui.echart(
                options=atualizar_grafico(df_categoria, 'Faturamento por Categoria', 'categoria_base')
            ).classes("w-full").style("height: 300px")

            chart_subcategoria = ui.echart(
                options=atualizar_grafico(dados_iniciais, f'Subcategorias de {categoria_inicial}', 'subcategoria')
            ).classes("w-full").style("height: 300px")

        # Evento de clique
        def on_click_categoria(e):
            categoria_selecionada = e.args.get('name') or (e.args.get('data') or {}).get('name')
            if not categoria_selecionada:
                ui.notify('Clique inválido.', color='red')
                return

            dados_filtrados = df_subcategoria[df_subcategoria['categoria_base'] == categoria_selecionada]

            if dados_filtrados.empty:
                ui.notify(f'Nenhuma subcategoria encontrada para "{categoria_selecionada}".', color='orange')
                return

            chart_subcategoria.options = atualizar_grafico(
                dados_filtrados,
                f'Subcategorias de {categoria_selecionada}',
                'subcategoria'
            )

        chart_categoria.on('chart:click', on_click_categoria)
