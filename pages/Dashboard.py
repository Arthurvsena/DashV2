# Arquivo: Dashboard.py
from nicegui import ui, app
import pandas as pd
import datetime
from components.grafico_marketplace import plot_pizza_marketplace
from components.grafico_categoria import plot_faturamento_por_categoria
from utils import load_data, logout_usuario, comparar_periodos
from style import aplicar_estilo_global
from queries import (
    get_orders_query,
    get_valor_total_faturado_query,
    get_categorias_query,
)

aplicar_estilo_global()



async def show_dashboard():
    session = app.storage.user
    if not session.get("username"):  # ✅ VERIFICA SE ESTÁ LOGADO
        ui.notify("Sessão expirada. Faça login novamente.")
        ui.navigate.to("/login")
        return

    schema = session.get("schema")
    if not schema:
        ui.notify("Schema inválido. Faça login novamente.")
        ui.navigate.to("/login")
        return
    
    start_date = datetime.date.today().replace(day=1)
    end_date = datetime.date.today()
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    with ui.row().classes("w-full items-center justify-between px-4 py-2").style("border-bottom: 1px solid #333;"):
        ui.icon('menu').classes('text-white cursor-pointer')  # Ícone menu à esquerda

        ui.label("Help Seller").classes("text-xl font-bold text-center text-[#08C5A1]").style("flex: 1; text-align: center;")

        with ui.row().classes("items-center gap-4"):
            ui.label(f"Schema: {session.get('schema', '')}").classes("text-sm text-gray-400")
            ui.link("Logout", "/login").classes("text-[#08C5A1] hover:text-[#00ffd5] hover:underline")

        with ui.row().classes("w-full mt-4"):
    # Corrigido: passa a função que calcula o valor total do faturamento
            valor_atual, valor_anterior, indicador, cor = comparar_periodos(schema, get_valor_total_faturado_query)

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-full max-w-md"):
                ui.label("💰 Faturamento Mês Atual").classes("text-lg text-white")
                ui.label(f"R$ {valor_atual:,.2f}").classes(f"text-2xl font-bold {cor}")
                ui.label(f"{indicador} em relação ao mês anterior").classes(f"text-sm {cor}")
    start_date = datetime.date.today().replace(day=1)
    end_date = datetime.date.today()
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    with ui.row().classes("w-full mt-6"):
        with ui.column().classes("w-1/2"):
            df_categoria = load_data(get_categorias_query(schema))
            plot_faturamento_por_categoria(schema, start_date, end_date)

        with ui.column().classes("w-1/2"):
            df_marketplace = load_data(get_orders_query(schema, start_str, end_str))
            plot_pizza_marketplace(df_marketplace)

    with ui.row().classes("w-full mt-6"):
        print('Tirado o mapa de calor')
        #df_mapa = load_data(get_mapa_query(schema))
        #plot_mapa_faturamento(df_mapa)

