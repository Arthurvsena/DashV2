# Arquivo: Dashboard.py
from nicegui import ui, app
import pandas as pd
import datetime
from components.grafico_linha_marketplace import plot_linha_marketplace
from components.grafico_categoria_interativo import grafico_categoria_interativo
from components.grafico_marketplace import plot_pizza_marketplace
from components.grafico_categoria import plot_faturamento_por_categoria
from components.grafico_faturamento_mensal import plot_faturamento_mensal
from utils import load_data, logout_usuario, comparar_periodos, checar_login
from style import aplicar_estilo_global
from queries import (
    get_orders_query,
    get_valor_total_frete_query,
    get_valor_total_faturado_query,
    get_categorias_query,
    get_valor_total_devolucao_query,
    get_order_item_query,
    get_products_query,
    get_faturamento_por_marketplace_query,
    get_faturamento_mensal_query
)

async def show_dashboard():
    session = app.storage.user
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

        ui.label("Help Intelligence").classes("text-xl font-bold text-center text-[#08C5A1]").style("flex: 1; text-align: center;")

        with ui.row().classes("items-center gap-2"):
            ui.icon("logout").classes("text-[#08C5A1]")
            ui.button("Sair", on_click=logout_usuario) \
                .classes("bg-transparent text-[#08C5A1] hover:text-[#00ffd5] hover:underline shadow-none px-0")

        with ui.row().classes("w-full mt-4"):
    # Corrigido: passa a função que calcula o valor total do faturamento
            valor_atual, valor_anterior, indicador, cor = comparar_periodos(schema, get_valor_total_faturado_query)
            # Novo KPI: Valor Total do Frete
            df_mensal = load_data(get_faturamento_mensal_query(schema))
            valor_frete_atual, valor_frete_anterior, indicador_frete, cor_frete = comparar_periodos(schema, get_valor_total_frete_query)
            valor_devolucao_atual, valor_devolucao_anterior, indicador_devolucao, cor_devolucao = comparar_periodos(schema, get_valor_total_devolucao_query)
            df_order_item = load_data(get_order_item_query(schema, start_str, end_str))
            df_products = load_data(get_products_query(schema))
            codigos_vendidos = df_order_item["sku"].unique()
            produtos_nunca_vendidos = df_products[~df_products["codigo"].isin(codigos_vendidos)]
            produtos_nunca_vendidos = produtos_nunca_vendidos[produtos_nunca_vendidos["estoque"].fillna(0) > 0]
            quantidade_nunca_vendidos = produtos_nunca_vendidos.shape[0]
            df_marketplace = get_faturamento_por_marketplace_query(schema, start_str, end_str)

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("💰 Faturamento Mês Atual").classes("text-lg text-white")
                ui.label(f"R$ {valor_atual:,.2f}").classes(f"text-2xl font-bold {cor}")
                ui.label(f"{indicador} em relação ao mês anterior").classes(f"text-sm {cor}")
            
            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("🚚 Valor Total do Frete").classes("text-md text-white")
                ui.label(f"R$ {valor_frete_atual:,.2f}").classes(f"text-2xl font-bold {cor_frete}")
                ui.label(f"Comparado ao mês anterior: R$ {valor_frete_anterior:,.2f} {indicador_frete}").classes("text-sm text-gray-400")

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("🔁 Valor Total de Devoluções").classes("text-md text-white")
                ui.label(f"R$ {valor_devolucao_atual:,.2f}").classes(f"text-2xl font-bold {cor_devolucao}")
                ui.label(f"Comparado ao mês anterior: R$ {valor_devolucao_anterior:,.2f} {indicador_devolucao}").classes("text-sm text-gray-400")

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("📦 Produtos Sem Vendas").classes("text-md text-white")
                ui.label(f"{quantidade_nunca_vendidos}").classes("text-2xl font-bold text-yellow-400")
                ui.button("🔍 Ver produtos", on_click=lambda: ui.navigate.to('/produtos-sem-vendas')).classes("mt-2 bg-[#08C5A1] text-white rounded-lg px-3 py-1 hover:bg-[#00ffd5]")


    start_date = datetime.date.today().replace(day=1)
    end_date = datetime.date.today()
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    with ui.row().classes("w-full flex-nowrap items-start gap-4").style("display: flex;"):

        with ui.column().classes("w-[50%]"):
            grafico_categoria_interativo(start_str, end_str, schema)

        with ui.column().classes("w-[50%]"):
            df_marketplace = get_faturamento_por_marketplace_query(schema, start_str, end_str)
            plot_linha_marketplace(df_marketplace)

    with ui.row().classes("w-full mt-6"):
        plot_faturamento_mensal(schema)

    with ui.row().classes("w-full mt-6"):
        print('Tirado o mapa de calor')
        #df_mapa = load_data(get_mapa_query(schema))
        #plot_mapa_faturamento(df_mapa)

