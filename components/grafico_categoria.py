from nicegui import ui
import pandas as pd
from utils import load_data
from queries import (
    get_nfs_query,
    get_orders_query,
    get_order_item_query,
    get_products_query
)

def plot_faturamento_por_categoria(schema: str, start_date: str, end_date: str, categoria_col: str = "categoria_base"):
    df_nfs = get_nfs_query(schema, start_date, end_date)
    df_orders = get_orders_query(schema, start_date, end_date)
    df_order_item = get_order_item_query(schema, start_date, end_date)
    df_products = get_products_query(schema)

    if "tipo" not in df_nfs.columns:
        ui.label("⚠️ A coluna 'tipo' não foi encontrada na tabela de notas fiscais (nfs). Verifique o schema e os dados.")
        return

    df_nfs = df_nfs[df_nfs["tipo"].str.upper() == "S"].copy()

    if df_nfs.empty or df_orders.empty or df_order_item.empty or df_products.empty:
        ui.label("⚠️ Não há dados suficientes para gerar o gráfico.")
        return

    df_orders = df_orders[df_orders["cliente_cpf_cnpj"].isin(df_nfs["cliente_cpf_cnpj"])].copy()
    df_order_item = df_order_item[df_order_item["order_id"].isin(df_orders["id"])].copy()

    df_merged = pd.merge(
        df_order_item,
        df_products,
        how="left",
        left_on="sku",
        right_on="codigo"
    ).copy()

    df_merged["quantidade"] = pd.to_numeric(df_merged["quantidade"], errors="coerce")
    df_merged["valor_unitario"] = pd.to_numeric(df_merged["valor_unitario"], errors="coerce")
    df_merged["faturamento"] = df_merged["quantidade"] * df_merged["valor_unitario"]

    if categoria_col == "subcategoria":
        df_merged["subcategoria"] = df_merged["categoria"].str.split(">>").str[1].str.strip()
    else:
        df_merged["categoria_base"] = df_merged["categoria"].str.split(">>").str[0].str.strip()

    coluna = "subcategoria" if categoria_col == "subcategoria" else "categoria_base"
    df_categoria = df_merged.groupby(coluna)["faturamento"].sum().reset_index()
    df_categoria = df_categoria.sort_values(by="faturamento", ascending=False)

    if df_categoria.empty:
        ui.label("⚠️ Nenhuma categoria encontrada com dados de faturamento.")
        return

    # Criar dados para ECharts
    data = [
        {"value": float(row["faturamento"]), "name": row[coluna]}
        for _, row in df_categoria.iterrows()
    ]

    ui.label(f"📊 Faturamento por {'Subcategoria' if categoria_col == 'subcategoria' else 'Categoria'}").classes("text-lg text-white mt-2")

    ui.echart({
        "title": {"text": "", "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}<br/>R$ {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "textStyle": {"color": "#e0e0e0"}},
        "series": [{
            "name": "Faturamento",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#0e1117",
                "borderWidth": 2
            },
            "label": {
                "show": True,
                "formatter": "{b}: {d}%",
                "color": "#e0e0e0",
                "fontSize": 14
            },

            "emphasis": {
                "label": {"show": True, "fontSize": "18", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": data
        }],
        "backgroundColor": "#0e1117",
        "textStyle": {"color": "#e0e0e0"}
    }).classes("w-full h-96")
