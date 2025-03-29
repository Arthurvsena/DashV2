from nicegui import ui 
import pandas as pd
from queries import get_faturamento_mensal_query
from utils import load_data

def plot_faturamento_mensal(schema: str):
    # 🧠 Carregando os dados diretamente da query
    df = load_data(get_faturamento_mensal_query(schema))

    # 🔎 Validação básica
    if df.empty or 'faturamento' not in df.columns or 'total_pedidos' not in df.columns:
        ui.label('Nenhum dado de faturamento mensal encontrado.').classes('text-red-500')
        return

    # 🕹️ Garantindo que os campos sejam numéricos
    df['faturamento'] = pd.to_numeric(df['faturamento'], errors='coerce').fillna(0)
    df['total_pedidos'] = pd.to_numeric(df['total_pedidos'], errors='coerce').fillna(0).astype(int)

    with ui.card().classes("w-full bg-[#1a1d23] text-white shadow-md p-4"):
        ui.label("📊 Faturamento Mensal (últimos 12 meses)").classes("text-lg font-bold mb-4")

        ui.echart({
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "#1f1f1f",
                "borderColor": "#555",
                "textStyle": {"color": "#fff", "fontSize": 14},
                "formatter": """
                    function(params) {
                        const p = params[0].data;
                        return `
                            📅 ${p.name}<br>
                            📦 Pedidos: ${p.total_pedidos}<br>
                            💰 Faturamento: R$ ${p.faturamento.toLocaleString('pt-BR')}
                        `;
                    }
                """
            },
            "xAxis": {
                "type": "category",
                "data": df['mes'].tolist(),
                "axisLabel": {"color": "white"}
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "white"}
            },
            "series": [{
                "type": "bar",
                "data": [
                    {
                        "name": row["mes"],
                        "value": row["faturamento"],
                        "faturamento": row["faturamento"],
                        "total_pedidos": row["total_pedidos"]
                    }
                    for _, row in df.iterrows()
                ],
                "itemStyle": {
                    "color": "#00e5c0"
                }
            }]
        }).classes("w-full h-full").style("min-height: 615px")