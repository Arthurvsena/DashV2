from nicegui import ui, app
import pandas as pd
import datetime
from utils import load_data
from queries import get_products_query, get_order_item_query

async def show_produtos():
    session = app.storage.user
    if not session.get("username"):
        ui.notify("Você precisa estar logado.")
        ui.open("/login")
        return

    schema = session.get("schema")
    ui.label("🛒 Produtos cadastrados").classes("text-2xl")

    hoje = datetime.date.today()
    data_inicio = ui.date(value=hoje.replace(day=1), label="Data Início").classes("w-1/3")
    data_fim = ui.date(value=hoje, label="Data Fim").classes("w-1/3")

    tabela_area = ui.column().classes("w-full")

    def atualizar():
        start_str = data_inicio.value.strftime("%Y-%m-%d")
        end_str = data_fim.value.strftime("%Y-%m-%d")

        produtos_df = load_data(get_products_query(schema))
        pedidos_df = load_data(get_order_item_query(schema, start_str, end_str))

        resumo = pedidos_df.groupby("produto_id").agg({"quantidade": "sum", "preco": "mean"}).reset_index()
        df_final = pd.merge(produtos_df, resumo, on="produto_id", how="left")
        df_final.fillna({"quantidade": 0, "preco": 0}, inplace=True)

        tabela_area.clear()
        with tabela_area:
            ui.table(columns=[{'name': c, 'label': c, 'field': c} for c in df_final.columns],
                     rows=df_final.to_dict("records"),
                     row_key='produto_id').classes("w-full")

    ui.button("🔄 Atualizar", on_click=atualizar).classes("mt-4")
    atualizar()