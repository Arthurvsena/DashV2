# Arquivo: grafico_marketplace.py
import plotly.express as px
import pandas as pd
from nicegui import ui
from queries import get_order_item_query
from datetime import date
from utils import load_data


def plot_pizza_marketplace(df_marketplace):
    if df_marketplace.empty or 'marketplace' not in df_marketplace.columns or 'valor_total' not in df_marketplace.columns:
        ui.label("⚠️ Dados de marketplace inválidos ou ausentes.")
        return

    df_grouped = df_marketplace.groupby('marketplace')['valor_total'].sum().reset_index()
    df_grouped = df_grouped.sort_values(by='valor_total', ascending=False)

    data = [
        {"value": float(row["valor_total"]), "name": row["marketplace"]}
        for _, row in df_grouped.iterrows()
    ]

    ui.label("🛒 Faturamento por Marketplace").classes("text-lg text-white mt-4")

    ui.echart({
        "tooltip": {"trigger": "item", "formatter": "{b}<br/>R$ {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "textStyle": {"color": "#e0e0e0"}},
        "series": [{
            "name": "Marketplace",
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
            "labelLine": {"show": True},
            "data": data
        }],
        "backgroundColor": "#0e1117",
        "textStyle": {"color": "#e0e0e0"}
    }).classes("w-full h-96")
