from nicegui import ui, app
from style import aplicar_estilo_global
from utils import get_connection
import queries
from datetime import date, timedelta
import pandas as pd
import json
import os
import plotly.express as px
import plotly.io as pio
from components.curva_abc import curva_abc_com_filtros

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
    data_3_meses_atras = (hoje - timedelta(days=90)).strftime('%Y-%m-%d')
    data_1_ano_atras = (hoje - timedelta(days=365)).strftime('%Y-%m-%d')

    media_vendas_diarias = queries.get_media_vendas_diarias(schema, data_3_meses_atras, end_str)
    ultimas_vendas = queries.get_ultima_venda_por_produto(schema, data_1_ano_atras, end_str)

    resultado_campeao = queries.get_produto_campeao(schema, start_str, end_str)
    if isinstance(resultado_campeao, (list, tuple)) and len(resultado_campeao) > 1:
        produto_campeao = resultado_campeao[0]
        faturamento_produto = resultado_campeao[1]
    else:
        produto_campeao = '-'
        faturamento_produto = 0.0

    resultado_vendidos = queries.get_total_produtos_vendidos(schema, start_str, end_str)
    try:
        total_vendidos = int(resultado_vendidos[0] if isinstance(resultado_vendidos, (list, tuple)) else resultado_vendidos)
    except Exception:
        total_vendidos = 0

    resultado_devolvido = queries.get_produto_mais_devolvido(schema, start_str, end_str)
    if isinstance(resultado_devolvido, tuple) and len(resultado_devolvido) == 2:
        produto_mais_devolvido, total_devolucoes = resultado_devolvido
    else:
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

    status_ref = None
    categoria_ref = None
    subcategoria_ref = None
    tabela_component = None

    async def aplicar_filtro():
        status = status_ref.value or 'Todos'
        categoria = categoria_ref.value
        subcategoria = subcategoria_ref.value

        produtos_raw = queries.get_produtos_por_status(schema, start_str, end_str, status)
        nova_lista = []

        for produto in produtos_raw:
            if produto['estoque'] == 0:
                continue

            codigo = produto['codigo']
            estoque = produto['estoque']
            media_diaria = media_vendas_diarias.get(codigo, 0)

            cobertura = round(estoque / media_diaria, 1) if media_diaria > 0 else '-'

            if 'categoria' in produto and produto['categoria']:
                partes = produto['categoria'].split('>>')
                cat = partes[0].strip() if len(partes) > 0 else ''
                sub = partes[1].strip() if len(partes) > 1 else ''
                if categoria and categoria != 'Todas' and cat != categoria:
                    continue
                if subcategoria and subcategoria != 'Todas' and sub != subcategoria:
                    continue

            ultima_venda_raw = ultimas_vendas.get(codigo)
            if ultima_venda_raw:
                try:
                    data_venda = pd.to_datetime(ultima_venda_raw).date()
                    dias_ultima_venda = (date.today() - data_venda).days
                    ultima_venda = f"{dias_ultima_venda} dias atrás"
                except Exception:
                    ultima_venda = '-'
            else:
                ultima_venda = '-'

            cmv = produto.get('preco_custo_medio')
            sugestao = round(float(cmv) * 2.6, 2) if cmv is not None else '-'

            nova_lista.append({
                'sku': codigo,
                'titulo': produto['nome'],
                'cobertura': cobertura,
                'cmv': round(float(cmv), 2) if cmv is not None else '-',
                'lucro': '-',
                'estoque': estoque,
                'preco': produto['preco'],
                'sugestao': sugestao,
                'ultima': ultima_venda,
            })

        tabela_component.rows = nova_lista
        ui.notify('Filtro aplicado com sucesso!', type='positive', position='top-right')

    def atualizar_subcategorias(e):
        categoria_escolhida = e.value
        status_atual = status_ref.value or 'Todos'
        produtos_filtrados = queries.get_produtos_por_status(schema, start_str, end_str, status_atual)

        subcategorias = []
        for produto in produtos_filtrados:
            if 'categoria' in produto and produto['categoria'] and '>>' in produto['categoria']:
                partes = produto['categoria'].split('>>')
                categoria = partes[0].strip()
                subcategoria = partes[1].strip()
                if categoria == categoria_escolhida:
                    subcategorias.append(subcategoria)

        subcategoria_ref.options = ['Todas'] + sorted(set(subcategorias))
        subcategoria_ref.visible = True

    produtos_raw = queries.get_produtos_por_status(schema, start_str, end_str, status='Todos')
    produtos_raw = [p for p in produtos_raw if p['estoque'] > 0]

    rows = []
    potencial_retorno = sum(produto['preco'] * produto['estoque'] for produto in produtos_raw if produto['estoque'] and produto['preco'])
    capital_investido = sum(produto['preco_custo_medio'] * produto['estoque'] for produto in produtos_raw if produto['estoque'] and produto.get('preco_custo_medio'))
    for produto in produtos_raw:
        codigo = produto['codigo']
        estoque = produto['estoque']
        media_diaria = media_vendas_diarias.get(codigo, 0)
        cobertura = round(estoque / media_diaria, 1) if media_diaria > 0 else '-'

        ultima_venda_raw = ultimas_vendas.get(codigo)
        if ultima_venda_raw:
            try:
                data_venda = pd.to_datetime(ultima_venda_raw).date()
                dias_ultima_venda = (date.today() - data_venda).days
                ultima_venda = f"{dias_ultima_venda} dias atrás"
            except Exception:
                ultima_venda = '-'
        else:
            ultima_venda = '-'

        cmv = produto.get('preco_custo_medio')
        sugestao = round(float(cmv) * 2.6, 2) if cmv is not None else '-'

        rows.append({
            'sku': codigo,
            'titulo': produto['nome'],
            'cobertura': cobertura,
            'cmv': round(float(cmv), 2) if cmv is not None else '-',
            'lucro': '-',
            'estoque': estoque,
            'preco': produto['preco'],
            'sugestao': sugestao,
            'ultima': ultima_venda,
        })


    with ui.column().classes('w-full p-4 gap-10'):
        with ui.row().classes('w-full gap-2'):
            titulos = [
                ('🏆 Produto Campeão de Vendas', produto_campeao, f"R$ {faturamento_produto:,.2f}"),
                ('💰 Produto Mais Rentável', '-', 'R$ 0,00'),
                ('📦 Total Produtos Vendidos', f'{total_vendidos} Produtos', ''),
                ('📥 Produto com Mais Devoluções', produto_mais_devolvido, f'{total_devolucoes} Devoluções'),
                ('⛔ Total de Produtos Sem Vendas', f'{total_sem_venda} Produtos', ''),
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
                curva_abc_com_filtros(schema, start_str, end_str)

        with ui.row().classes('w-full items-center justify-between'):
            ui.label("📟 Produtos Vendidos no Período").classes("text-lg font-semibold text-white")
            with ui.row().classes("gap-2"):
                status_ref = ui.select(
                    options=['Todos', 'Vendidos', 'Sem Venda'],
                    label='Status'
                ).props('dense popup-content-class=q-dark').classes('w-[100px] bg-[#1e1e1e] text-white rounded-xl')

                categoria_ref = ui.select(
                    options=['Todas'] + sorted({
                        p['categoria'].split('>>')[0].strip()
                        for p in produtos_raw
                        if 'categoria' in p and p['categoria'] and '>>' in p['categoria']
                    }),
                    label='Categoria'
                ).props('dense popup-content-class=q-dark').classes('w-[150px] bg-[#1e1e1e] text-white rounded-xl')

                subcategoria_ref = ui.select(
                    options=['Todas'],
                    label='Subcategoria'
                ).props('dense popup-content-class=q-dark').classes('w-[150px] bg-[#1e1e1e] text-white rounded-xl')
                subcategoria_ref.visible = False

                categoria_ref.on('change', atualizar_subcategorias)

                ui.button('FILTRAR', on_click=aplicar_filtro).classes('px-4 py-2 rounded text-white bg-[#08c5a199] hover:bg-[#08c5a1] transition')

        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl flex-1'):
                ui.label('🏦 Capital Investido').classes('text-sm text-gray-400')
                ui.label(f"R$ {capital_investido:,.2f}").classes('text-2xl font-bold text-red-500')

            with ui.card().classes('bg-[#1e1e1e] text-white p-4 rounded-xl flex-1'):
                ui.label('📈 Potencial de Retorno').classes('text-sm text-gray-400')
                ui.label(f"R$ {potencial_retorno:,.2f}").classes('text-2xl font-bold text-green-500')

        tabela_component = ui.table(
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
            rows=rows,
        ).classes('w-full text-white bg-[#1e1e1e] rounded-xl mt-2').style('max-height: 500px; overflow-y: auto')
