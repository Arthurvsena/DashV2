from nicegui import ui
import pandas as pd

def plot_linha_marketplace(df: pd.DataFrame):
    # 🔎 Verificação de colunas mínimas
    if df.empty or not {'marketplace', 'data', 'valor_total'}.issubset(df.columns):
        ui.label("Sem dados válidos para exibir o gráfico.").classes("text-red-500")
        return

    # 🧹 Limpa dados nulos e padroniza
    df = df.dropna(subset=["marketplace", "data", "valor_total"])
    df["marketplace"] = df["marketplace"].astype(str).str.strip().str.title()
    df["data"] = pd.to_datetime(df["data"]).dt.strftime("%d/%m")

    # 🧱 Cria a estrutura pivot
    try:
        df_pivot = df.pivot(index="data", columns="marketplace", values="valor_total").fillna(0)
    except Exception as e:
        ui.label(f"Erro ao montar gráfico: {e}").classes("text-red-500")
        return

    if df_pivot.empty:
        ui.label("Nenhum dado encontrado após o processamento.").classes("text-red-500")
        return

    # 📈 Renderiza o gráfico com ECharts
    with ui.card().classes("bg-[#1a1d23] text-white shadow-md h-full w-full flex-grow").style("min-height: 320px"):
        ui.label("📈 Faturamento por Marketplace").classes("text-lg font-bold mb-4")

        ui.echart({
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "#1f1f1f",
                "borderColor": "#555",
                "textStyle": {
                    "color": "#fff",
                    "fontSize": 14
                }
            },
            "legend": {
                "data": list(df_pivot.columns),
                "textStyle": {"color": "white"}
            },
            "xAxis": {
                "type": "category",
                "data": df_pivot.index.tolist(),
                "axisLabel": {"color": "white"}
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "white"}
            },
            "series": [
                {
                    "name": marketplace,
                    "type": "line",
                    "data": df_pivot[marketplace].tolist(),
                    "smooth": True
                }
                for marketplace in df_pivot.columns
            ]
        }).classes("w-full h-full").style("min-height: 615px")

