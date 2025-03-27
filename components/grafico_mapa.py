# Arquivo: grafico_mapa.py
import plotly.express as px
import pandas as pd
from nicegui import ui
import json
from queries import get_mapa_query

def plot_mapa_faturamento(df_mapa):
    from nicegui import ui
    ui.notify("🗺️ Mapa de calor temporariamente desativado.", type="warning")
