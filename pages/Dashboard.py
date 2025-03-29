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

    filtro_padrao = {
        'inicio': datetime.date.today().replace(day=1),
        'fim': datetime.date.today()
    }

    # Verifica se já existe filtro salvo na sessão
    if 'filtro' in app.storage.user:
        try:
            filtro = {
                'inicio': pd.to_datetime(app.storage.user['filtro']['inicio']).date(),
                'fim': pd.to_datetime(app.storage.user['filtro']['fim']).date()
            }
        except Exception as e:
            print(f"[ERRO] Falha ao recuperar filtro salvo: {e}")
            filtro = filtro_padrao
    else:
        filtro = filtro_padrao


    def abrir_modal():
        with ui.dialog() as dialog:
            with ui.card().classes("bg-[#1E1E1E] text-white p-6"):
                ui.label("Selecionar Período").classes("text-lg mb-2")
                date_range = ui.date(value=[filtro['inicio'], filtro['fim']]).props('range').classes("bg-[#1E1E1E] text-white")

                def aplicar():
                    valor = date_range.value
                    if isinstance(valor, dict) and 'from' in valor and 'to' in valor:
                        try:
                            data_inicio = pd.to_datetime(valor['from']).date()
                            data_fim = pd.to_datetime(valor['to']).date()

                            filtro['inicio'] = data_inicio
                            filtro['fim'] = data_fim

                            ui.notify(f"[DEBUG] Datas atualizadas para: {data_inicio} até {data_fim}")
                            dialog.close()
                            app.storage.user['filtro'] = {
                                'inicio': str(data_inicio),
                                'fim': str(data_fim)
                            }
                            ui.navigate.to('/dashboard')  # Redireciona para recarregar com as novas datas
                        except Exception as e:
                            ui.notify(f"Erro ao converter datas: {e}", type='negative')
                    else:
                        ui.notify("Selecione uma data de início e fim válidas.", type='warning')

                ui.button("Aplicar Filtro", on_click=aplicar).classes("mt-4 bg-[#08C5A1] hover:bg-[#00ffd5] text-white")
        dialog.open()

    def atualizar_kpis():
        inicio_str = filtro['inicio'].strftime("%Y-%m-%d")
        fim_str = filtro['fim'].strftime("%Y-%m-%d")
        ui.notify(f"[DEBUG] Atualizando KPIs de {inicio_str} até {fim_str}")

        valor_atual, valor_anterior, indicador, cor = comparar_periodos(schema, get_valor_total_faturado_query, inicio_str, fim_str)
        valor_frete_atual, valor_frete_anterior, indicador_frete, cor_frete = comparar_periodos(schema, get_valor_total_frete_query, inicio_str, fim_str)
        valor_devolucao_atual, valor_devolucao_anterior, indicador_devolucao, cor_devolucao = comparar_periodos(schema, get_valor_total_devolucao_query, inicio_str, fim_str)

        df_order_item = load_data(get_order_item_query(schema, inicio_str, fim_str))
        df_products = load_data(get_products_query(schema))
        codigos_vendidos = df_order_item["sku"].unique()
        produtos_nunca_vendidos = df_products[~df_products["codigo"].isin(codigos_vendidos)]
        produtos_nunca_vendidos = produtos_nunca_vendidos[produtos_nunca_vendidos["estoque"].fillna(0) > 0]
        quantidade_nunca_vendidos = produtos_nunca_vendidos.shape[0]

        df_marketplace = get_faturamento_por_marketplace_query(schema, inicio_str, fim_str)

        with ui.row().classes("w-full flex-wrap"):
            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("💰 Faturamento do Período").classes("text-lg text-white")
                ui.label(f"R$ {valor_atual:,.2f}").classes(f"text-2xl font-bold {cor}")
                ui.label(indicador).classes("text-sm text-gray-400")

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("🚚 Valor Total do Frete").classes("text-md text-white")
                ui.label(f"R$ {valor_frete_atual:,.2f}").classes(f"text-2xl font-bold {cor_frete}")
                ui.label(indicador_frete).classes("text-sm text-gray-400")

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("🔁 Valor Total de Devoluções").classes("text-md text-white")
                ui.label(f"R$ {valor_devolucao_atual:,.2f}").classes(f"text-2xl font-bold {cor_devolucao}")
                ui.label(indicador_devolucao).classes("text-sm text-gray-400")

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[380px] h-[150px] m-2 flex flex-col justify-between"):
                ui.label("📦 Produtos Sem Vendas").classes("text-md text-white")
                ui.label(f"{quantidade_nunca_vendidos}").classes("text-2xl font-bold text-yellow-400")
                ui.button("🔍 Ver produtos", on_click=lambda: ui.navigate.to('/produtos-sem-vendas')).classes("mt-2 bg-[#08C5A1] text-white rounded-lg px-3 py-1 hover:bg-[#00ffd5]")

            with ui.card().classes("bg-[#1a1d23] rounded-2xl p-4 shadow-lg w-[200px] h-[150px] m-2 flex flex-col justify-center items-center"):
                ui.label("Filtro por Período").classes("text-md text-white")
                ui.button("Selecionar Período", on_click=abrir_modal).classes("text-sm px-3 py-2 bg-[#08C5A1] text-white rounded-md hover:bg-[#00ffd5]")

        with ui.row().classes("w-full flex-nowrap items-start gap-4"):
            with ui.column().classes("w-[50%]"):
                grafico_categoria_interativo(inicio_str, fim_str, schema)
            with ui.column().classes("w-[50%]"):
                plot_linha_marketplace(df_marketplace)

        with ui.row().classes("w-full mt-6"):
            plot_faturamento_mensal(schema)

    with ui.row().classes("w-full items-center justify-between px-4 py-2").style("border-bottom: 1px solid #333;"):
        ui.icon('menu').classes('text-white cursor-pointer')
        ui.label("Help Intelligence").classes("text-xl font-bold text-center text-[#08C5A1]").style("flex: 1; text-align: center;")
        with ui.row().classes("items-center gap-2"):
            ui.icon("logout").classes("text-[#08C5A1]")
            ui.button("Sair", on_click=logout_usuario).classes("bg-transparent text-[#08C5A1] hover:text-[#00ffd5] hover:underline shadow-none px-0")

    atualizar_kpis()
