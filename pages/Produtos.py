from nicegui import ui, app
from style import aplicar_estilo_global
from utils import get_connection
import queries
from datetime import date
from datetime import datetime

@ui.page('/produtos')
async def show_produtos():
    aplicar_estilo_global()
    app.storage.user['rota_atual'] = '/produtos'

    # Conexão e execução da query
    session = app.storage.user
    schema = session.get("schema")



# Corrigido para garantir string 'YYYY-MM-DD'
    data_inicio = session.get("filtro_data_inicio")
    data_fim = session.get("filtro_data_fim")

    if isinstance(data_inicio, (datetime, date)):
        data_inicio = data_inicio.strftime('%Y-%m-%d')
    if isinstance(data_fim, (datetime, date)):
        data_fim = data_fim.strftime('%Y-%m-%d')

    # fallback padrão
    if not data_inicio:
        data_inicio = "2024-01-01"
    if not data_fim:
        data_fim = date.today().strftime('%Y-%m-%d')

    resultado = queries.get_produto_campeao(schema, data_inicio, data_fim)
    produto_campeao = resultado[0] if resultado else '-'
    faturamento_produto = resultado[1] if resultado else 0.0

    with ui.column().classes('w-full p-4 gap-10'):
        # LINHA 1 - CARDS DE INDICADORES
        with ui.row().classes('w-full gap-2'):
            titulos = [
                ('🏆 Produto Campeão de Vendas', produto_campeao, faturamento_produto),
                ('💰 Produto Mais Rentável', '-', 0.0),
                ('📦 Total Produtos Vendidos', '-', 0.0),
                ('📥 Produto com Mais Devoluções', '-', 0.0),
                ('🛑 Total de Produtos Sem Vendas', '-', 0.0),
            ]
            for titulo, descricao, valor in titulos:
                with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl').classes('flex-1'):
                    ui.label(titulo).classes('text-sm text-gray-400')
                    ui.label(descricao).classes('text-2xl font-bold')
                    ui.label(f"R$ {valor:,.2f}").classes("text-sm")

        # LINHA 2 - GRÁFICOS
        with ui.row().classes('w-full gap-2'):
            with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl').style('width: 29%; height: 320px'):
                ui.label('🌡️ Mapa de Calor de Faturamento').classes('text-sm text-gray-400')
                ui.label('Gráfico aqui')

            with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl').style('width: 69%; height: 320px'):
                ui.label('📊 Curva ABC (Pareto)').classes('text-sm text-gray-400')
                ui.label('Gráfico aqui')

        # FILTROS + TÍTULO
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

        # INDICADORES ABAIXO DOS FILTROS
        with ui.row().classes('w-full gap-4'):
            for titulo in ['🏦 Capital Investido', '📈 Potencial de Retorno']:
                with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl flex-1'):
                    ui.label(titulo).classes('text-sm text-gray-400')
                    ui.label("-").classes('text-2xl font-bold')

        # TABELA
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

        print(data_inicio)
        print(data_fim)
        print(produto_campeao)
        print(resultado)
        print(faturamento_produto)
        print(titulo)
        print(descricao)