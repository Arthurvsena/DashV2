from nicegui import ui, app
from style import aplicar_estilo_global
from utils import get_connection
import queries
from datetime import date
import pandas as pd
import json
import os
import plotly.express as px
import plotly.io as pio

@ui.page('/produtos')
async def show_produtos():
    aplicar_estilo_global()

    session = app.storage.user
    schema = session.get("schema")

    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    data_inicio = primeiro_dia
    data_fim = hoje

    if 'filtro_data_inicio' in session and 'filtro_data_fim' in session:
        try:
            data_inicio = pd.to_datetime(session['filtro_data_inicio']).date()
            data_fim = pd.to_datetime(session['filtro_data_fim']).date()
        except Exception as e:
            print(f"[ERRO] Falha ao carregar filtro da sessão: {e}")

    start_str = data_inicio.strftime('%Y-%m-%d')
    end_str = data_fim.strftime('%Y-%m-%d')

    resultado_campeao = queries.get_produto_campeao(schema, start_str, end_str)
    if isinstance(resultado_campeao, (list, tuple)) and len(resultado_campeao) > 1:
        produto_campeao = resultado_campeao[0]
        faturamento_produto = resultado_campeao[1]
    else:
        print("Formato inesperado de resultado_campeao:", resultado_campeao)
        produto_campeao = '-'
        faturamento_produto = 0.0

    resultado_vendidos = queries.get_total_produtos_vendidos(schema, start_str, end_str)
    try:
        total_vendidos = int(resultado_vendidos[0] if isinstance(resultado_vendidos, (list, tuple)) else resultado_vendidos)
    except Exception as e:
        print("Erro ao interpretar resultado_vendidos:", e)
        total_vendidos = 0

    resultado_devolvido = queries.get_produto_mais_devolvido(schema, start_str, end_str)
    if isinstance(resultado_devolvido, tuple) and len(resultado_devolvido) == 2:
        produto_mais_devolvido, total_devolucoes = resultado_devolvido
    else:
        print("Formato inesperado de resultado_devolvido:", resultado_devolvido)
        produto_mais_devolvido = '-'
        total_devolucoes = 0

    total_sem_venda = queries.get_total_produtos_sem_venda(schema, start_str, end_str)

    geo_path = os.path.join('data', 'brazil-states.geojson')
    with open(geo_path, encoding='utf-8') as f:
        geojson = json.load(f)

    faturamento_estados = queries.get_faturamento_por_estado(schema, start_str, end_str)
    df_estados = pd.DataFrame(faturamento_estados)
    df_estados.columns = ['estado', 'valor']

    fig = px.choropleth(
        df_estados,
        geojson=geojson,
        locations='estado',
        featureidkey="properties.sigla",
        color='valor',
        color_continuous_scale=["#ffe5d9", "#ffb07c", "#ff6f3c", "#d62828"],
        range_color=(0, df_estados['valor'].max() if not df_estados.empty else 10000),
        labels={'valor': 'Faturamento'},
        hover_name='estado',
        hover_data={'valor': ':.2f'},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        font_color='white',
        coloraxis_colorbar=dict(title='Faturamento', tickprefix='R$ ', thickness=8)
    )

    with ui.column().classes('w-full p-4 gap-10'):
        with ui.row().classes('w-full gap-2'):
            titulos = [
                ('🏆 Produto Campeão de Vendas', produto_campeao, f"R$ {faturamento_produto:,.2f}"),
                ('💰 Produto Mais Rentável', '-', 'R$ 0,00'),
                ('📦 Total Produtos Vendidos', f'{total_vendidos} Produtos', ''),
                ('📥 Produto com Mais Devoluções', produto_mais_devolvido, f'{total_devolucoes} Devoluções'),
                ('🛑 Total de Produtos Sem Vendas', f'{total_sem_venda} Produtos', ''),
            ]
            for titulo, descricao, valor in titulos:
                with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl h-[160px]').classes('flex-1'):
                    ui.label(titulo).classes('text-sm text-gray-400')
                    ui.label(descricao).classes('text-lg font-semibold whitespace-nowrap overflow-hidden text-ellipsis max-w-full')
                    if valor:
                        ui.label(valor).classes("text-sm text-green-500")

        with ui.row().classes('w-full gap-2'):
            with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl').style('width: 29%; height: 560px'):
                ui.label('🌡️ Mapa de Calor de Faturamento').classes('text-sm text-gray-400')
                ui.plotly(fig).classes('w-full h-[500px]')

            with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl').style('width: 69%; height: 560px'):
                ui.label('📊 Curva ABC (Pareto)').classes('text-sm text-gray-400')
                ui.label('Gráfico aqui')

        with ui.row().classes('w-full items-center justify-between'):
            ui.label("🧾 Produtos Vendidos no Período").classes("text-lg font-semibold text-white")
            with ui.row().classes("gap-2"):
                ui.select(
                    options=['Todos', 'Vendidos', 'Sem Venda'], 
                    label='Status'
                ).props('dense popup-content-class=q-dark').classes('w-[100px] bg-[#1e1e1e] text-white rounded-xl')
                ui.select(
                    options=['Todas'], 
                    label='Categoria'
                ).props('dense popup-content-class=q-dark').classes('w-[100px] bg-[#1e1e1e] text-white rounded-xl')
                ui.select(
                    options=['Todas'], 
                    label='Subcategoria'
                ).props('dense popup-content-class=q-dark').classes('w-[100px] bg-[#1e1e1e] text-white rounded-xl')
                ui.button('FILTRAR').classes('px-4 py-2 rounded text-white bg-[#08c5a199] hover:bg-[#08c5a1] transition')

        with ui.row().classes('w-full gap-4'):
            for titulo in ['🏦 Capital Investido', '📈 Potencial de Retorno']:
                with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl flex-1'):
                    ui.label(titulo).classes('text-sm text-gray-400')
                    ui.label("-").classes('text-2xl font-bold')

        ui.table(
            columns=[
                {'name': 'sku', 'label': 'SKU', 'field': 'sku'},
                {'name': 'titulo', 'label': 'Título', 'field': 'titulo'},
                {'name': 'cobertura', 'label': 'Cobertura de Estoque', 'field': 'cobertura'},
                {'name': 'cmv', 'label': 'C.M.V', 'field': 'cmv'},
                {'name': 'lucro', 'label': '% Lucro Atual', 'field': 'lucro'},
                {'name': 'estoque', 'label': 'Estoque', 'field': 'estoque'},
                {'name': 'preco', 'label': 'Preço Venda', 'field': 'preco'},
                {'name': 'sugestao', 'label': 'Sugestão', 'field': 'sugestao'},
                {'name': 'ultima', 'label': 'Última Venda', 'field': 'ultima'},
            ],
            rows=[],
        ).classes('w-full text-white bg-[#1e1e1e] rounded-xl mt-2')
