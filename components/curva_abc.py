from nicegui import ui
import pandas as pd
import queries
import io


def classificar_abc(df):
    df['faturamento'] = df['faturamento'].round(2)
    df['% acumulado'] = df['faturamento'].cumsum() / df['faturamento'].sum() * 100
    df['% acumulado'] = df['% acumulado'].round(2)
    df['classe_abc'] = df['% acumulado'].apply(lambda p: 'A' if p <= 80 else ('B' if p <= 95 else 'C'))
    return df


def plot_curva_abc_echarts(df):
    df = classificar_abc(df)
    produtos = df['produto'].tolist()
    faturamento = df['faturamento'].tolist()
    acumulado = df['% acumulado'].tolist()
    cor_map = {'A': '#00BFFF', 'B': '#FFA500', 'C': '#DC143C'}
    cores = [cor_map[cls] for cls in df['classe_abc']]

    tooltips = [
        f"{produto}<br/>Faturamento: R$ {fat:,.2f}<br/>% Acumulado: {perc:.2f}%"
        for produto, fat, perc in zip(produtos, faturamento, acumulado)
    ]

    option = {
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "#1e1e1e",
            "borderColor": "#444",
            "borderWidth": 1,
            "textStyle": {"color": "#fff"},
        },
        "legend": {
            "data": ["Faturamento", "% Acumulado"],
            "textStyle": {"color": "white"}
        },
        "xAxis": [
            {
                "type": "category",
                "data": produtos,
                "axisLabel": {"rotate": 45, "color": "white"}
            }
        ],
        "yAxis": [
            {
                "type": "value",
                "name": "Faturamento",
                "axisLabel": {"color": "white"}
            },
            {
                "type": "value",
                "name": "% Acumulado",
                "max": 100,
                "axisLabel": {"color": "white"}
            }
        ],
        "series": [
            {
                "name": "Faturamento",
                "type": "bar",
                "data": [
                    {
                        "value": v,
                        "tooltip": {"formatter": t},
                        "itemStyle": {"color": c}
                    }
                    for v, t, c in zip(faturamento, tooltips, cores)
                ],
                "barMaxWidth": 30
            },
            {
                "name": "% Acumulado",
                "type": "line",
                "yAxisIndex": 1,
                "data": acumulado,
                "smooth": True,
                "lineStyle": {"color": "#FF5733"},
                "itemStyle": {"color": "#FF5733"}
            }
        ]
    }

    with ui.row().classes("w-full overflow-x-auto"):
        ui.echart(options=option).classes('min-w-[1200px] h-96')


def curva_abc_com_filtros(schema: str, data_inicio: str, data_fim: str):
    with ui.column().classes('w-full gap-2'):
        modo_select = ui.select(
            ['Por produto pai', 'Por marca'],
            value='Por produto pai',
            label='Agrupar por'
        ).classes('bg-[#1e1e1e] text-white').props('dense dark')

        marca_select = ui.select([], label='Filtrar marca') \
            .classes('bg-[#1e1e1e] text-white').props('dense dark')

        resultado_area = ui.row().classes('w-full')

        df_base = queries.get_curva_abc(schema, data_inicio, data_fim)
        df_base['codigo_base'] = df_base['sku'].str.split('-').str[0]

        # Traz os dados dos produtos pai com marca e nome
        df_products = queries.get_produtos(schema)
        df_pais = df_products[df_products["tipoVariacao"] == "P"].copy()
        df_pais["codigo_base"] = df_pais["codigo"].str.split("-").str[0]
        df_pais = df_pais.rename(columns={"nome": "descricao_pai"})

        # Agrupa por produto pai
        df_agrupado = df_base.groupby("codigo_base")["faturamento"].sum().reset_index()
        df_agrupado = df_agrupado.merge(df_pais[["codigo_base", "descricao_pai", "marca"]], on="codigo_base", how="left")
        df_agrupado["descricao_pai"] = df_agrupado["descricao_pai"].fillna(df_agrupado["codigo_base"])
        df_agrupado["marca"] = df_agrupado["marca"].fillna("Sem marca")

        # Popula o select de marcas
        marcas_disponiveis = df_agrupado['marca'].dropna().unique().tolist()
        marca_select.options = ['Todas'] + sorted(marcas_disponiveis)

        def carregar():
            modo = modo_select.value
            marca = marca_select.value

            df = df_agrupado.copy()
            if marca and marca != 'Todas':
                df = df[df['marca'] == marca]

            if modo == 'Por marca':
                df = df.groupby('marca')["faturamento"].sum().reset_index()
                df['produto'] = df['marca']
            else:
                df['produto'] = df['descricao_pai']

            df['faturamento'] = df['faturamento'].astype(float)
            df = df.sort_values(by='faturamento', ascending=False).reset_index(drop=True)
            df['% acumulado'] = df['faturamento'].cumsum() / df['faturamento'].sum() * 100
            df['% acumulado'] = df['% acumulado'].round(2)

            resultado_area.clear()
            with resultado_area:
                if not df.empty:
                    plot_curva_abc_echarts(df)

                    # ✅ Gera CSV e botão para download
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    csv_bytes = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))

                    ui.button('⬇ Exportar CSV', on_click=lambda: ui.download(
                        content=csv_bytes,
                        filename=f'curva_abc_{pd.Timestamp.now().date()}.csv',
                        mime_type='text/csv'
                    )).props('flat').classes('mt-4 text-white')
                else:
                    ui.label('Nenhum dado para exibir.').classes('text-yellow-400')

        modo_select.on("update:model-value", lambda e: carregar())
        marca_select.on("update:model-value", lambda e: carregar())
        carregar()
