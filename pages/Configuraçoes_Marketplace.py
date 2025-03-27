from nicegui import ui, app
import pandas as pd
from utils import get_connection

MARKETPLACES = [
    "Mercado Livre", "Magazine Luiza", "Shopee", "Via Varejo", "Nuvem Shop",
    "Shein", "Web Continental", "Kabum", "Netshoes", "Amazon", 
    "Centauro", "Madeira Madeira"
]

TIPOS_FRETE = ["%", "R$"]

async def show_config_marketplace():
    session = app.storage.user
    if not session.get("username"):
        ui.notify("Você precisa estar logado.")
        ui.open("/login")
        return

    schema = session.get("schema")
    ui.label("⚙️ Configurações do Marketplace").classes("text-2xl")

    conn = get_connection()
    cur = conn.cursor()

    tabela_config = pd.DataFrame(columns=["Marketplace", "Frete", "Tipo"])
    try:
        cur.execute(f'SELECT marketplace, frete, tipo FROM {schema}.marketplace_config')
        dados = cur.fetchall()
        tabela_config = pd.DataFrame(dados, columns=["Marketplace", "Frete", "Tipo"])
    except:
        ui.notify("Tabela de configuração não encontrada.")

    selects = []
    for mp in MARKETPLACES:
        with ui.row().classes("items-center gap-4"):
            ui.label(mp).classes("w-64")
            frete = ui.input("Frete", value="0.0").props("type=number").classes("w-32")
            tipo = ui.select(TIPOS_FRETE, value="%")
            selects.append((mp, frete, tipo))

    def salvar():
        cur.execute(f"DELETE FROM {schema}.marketplace_config")
        for mp, frete, tipo in selects:
            cur.execute(
                f"INSERT INTO {schema}.marketplace_config (marketplace, frete, tipo) VALUES (%s, %s, %s)",
                (mp, frete.value, tipo.value)
            )
        conn.commit()
        ui.notify("Configurações salvas com sucesso!")

    ui.button("💾 Salvar Configurações", on_click=salvar).classes("mt-4")