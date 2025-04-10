from nicegui import ui, app
import pandas as pd
import datetime
from components.grafico_linha_marketplace import plot_linha_marketplace
from components.grafico_categoria_interativo import grafico_categoria_interativo
from components.grafico_faturamento_mensal import plot_faturamento_mensal
from components.menu_lateral import criar_menu_lateral
from utils import load_data, logout_usuario, comparar_periodos, verificar_sessao_valida
from style import aplicar_estilo_global
from queries import (
    get_valor_total_frete_query,
    get_valor_total_faturado_query,
    get_valor_total_devolucao_query,
    get_order_item_query,
    get_products_query,
    get_faturamento_por_marketplace_query,
)

aplicar_estilo_global()


async def show_dashboard():

    if not verificar_sessao_valida():
        return

    session = app.storage.user
    username = session.get("usuario")
    schema = session.get("schema")
    schemas_autorizados = session.get("schemas_autorizados", [])
    is_master = session.get("is_master", False)

    hoje = datetime.date.today()
    primeiro_dia = hoje.replace(day=1)
    start_date = primeiro_dia
    end_date = hoje

    if 'filtro_data_inicio' in session and 'filtro_data_fim' in session:
        try:
            start_date = pd.to_datetime(session['filtro_data_inicio']).date()
            end_date = pd.to_datetime(session['filtro_data_fim']).date()
        except Exception as e:
            print(f"[ERRO] Falha ao carregar filtro da sessão: {e}")

    print(f"\n🎯 Filtro de data aplicado: {start_date} até {end_date}\n")

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')


    valor_atual, valor_anterior, indicador, cor = comparar_periodos(schema, get_valor_total_faturado_query, start_str, end_str)
    valor_frete_atual, _, _, _ = comparar_periodos(schema, get_valor_total_frete_query, start_str, end_str)
    valor_devolucao_atual, _, _, _ = comparar_periodos(schema, get_valor_total_devolucao_query, start_str, end_str)

    df_order_item = load_data(get_order_item_query(schema, start_str, end_str))
    df_products = load_data(get_products_query(schema))

    codigos_vendidos = df_order_item["sku"].unique()
    produtos_nunca_vendidos = df_products[~df_products["codigo"].isin(codigos_vendidos)]
    produtos_nunca_vendidos = produtos_nunca_vendidos[produtos_nunca_vendidos["estoque"].fillna(0) > 0]
    quantidade_nunca_vendidos = produtos_nunca_vendidos.shape[0]

    df_marketplace = load_data(get_faturamento_por_marketplace_query(schema, start_str, end_str))

    with ui.row().classes("w-full flex-wrap"):
        with ui.card().classes("bg-[#1a1d23] p-4 w-[380px] m-2"):
            ui.label("💰 Faturamento").classes("text-lg text-white")
            ui.label(f"R$ {valor_atual:,.2f}").classes(f"text-2xl font-bold {cor}")
            ui.label(indicador).classes("text-sm text-gray-400")

        with ui.card().classes("bg-[#1a1d23] p-4 w-[380px] m-2"):
            ui.label("🚚 Frete").classes("text-md text-white")
            ui.label(f"R$ {valor_frete_atual:,.2f}").classes("text-2xl font-bold text-green-500")

        with ui.card().classes("bg-[#1a1d23] p-4 w-[380px] m-2"):
            ui.label("🔁 Devoluções").classes("text-md text-white")
            ui.label(f"R$ {valor_devolucao_atual:,.2f}").classes("text-2xl font-bold text-red-500")

        with ui.card().classes("bg-[#1a1d23] p-4 w-[380px] m-2"):
            ui.label("📦 Produtos Sem Vendas").classes("text-md text-white")
            ui.label(f"{quantidade_nunca_vendidos}").classes("text-2xl font-bold text-yellow-400")

    with ui.row().classes("w-full flex-nowrap items-start gap-4"):
        with ui.column().classes("w-[50%]"):
            grafico_categoria_interativo(start_str, end_str, schema)
        with ui.column().classes("w-[50%]"):
            plot_linha_marketplace(df_marketplace)

    with ui.row().classes("w-full mt-6"):
        plot_faturamento_mensal(schema)
