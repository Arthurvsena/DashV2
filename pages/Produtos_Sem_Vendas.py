# Arquivo: Produtos_Sem_Venda.py
from nicegui import ui, app
import datetime
import pandas as pd
from utils import load_data
from queries import get_products_query, get_order_item_query

async def show_produtos_sem_vendas():
    session = app.storage.user
    if not session.get("username"):
        ui.notify("Você precisa estar logado.")
        ui.open("/login")
        return

    schema = session.get("schema")
    ui.label("📦 Produtos sem venda").classes("text-2xl")

    today = datetime.date.today()
    data_inicio = ui.date(value=today.replace(day=1), label="Data Início").classes("w-1/3")
    data_fim = ui.date(value=today, label="Data Fim").classes("w-1/3")
    tabela_area = ui.column().classes("w-full")

    def atualizar():
        start_str = data_inicio.value.strftime("%Y-%m-%d")
        end_str = data_fim.value.strftime("%Y-%m-%d")

        produtos_df = load_data(get_products_query(schema))
        vendidos_df = load_data(get_order_item_query(schema, start_str, end_str))

        vendidos_set = set(vendidos_df["produto_id"].unique())
        nao_vendidos = produtos_df[~produtos_df["produto_id"].isin(vendidos_set)]

        tabela_area.clear()
        if not nao_vendidos.empty:
            with tabela_area:
                ui.table(columns=[{'name': c, 'label': c, 'field': c} for c in nao_vendidos.columns],
                         rows=nao_vendidos.to_dict("records"), row_key='produto_id').classes("w-full")
        else:
            with tabela_area:
                ui.label("Nenhum produto sem venda encontrado no período.")

    ui.button("🔄 Atualizar", on_click=atualizar).classes("mt-4")
    atualizar()