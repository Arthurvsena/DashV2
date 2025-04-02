# === topbar.py ===
from nicegui import ui, app
from utils import logout_usuario


def criar_topbar(toggle_menu=None,com_filtro=True):
    with ui.row().classes("w-full items-center justify-between px-4 py-2").style("position: sticky; top: 0; z-index: 40;"):
        # Botão do menu
        with ui.row().classes("items-center gap-4"):
            ui.button(
                icon='menu',
                on_click=toggle_menu or (lambda: app.emit('toggle_menu')),
            ).props('flat color=white').classes("transition-transform hover:scale-105")

            ui.label("Help Seller").classes("text-white text-lg font-bold")

        # Info do schema e botão de filtro
        with ui.row().classes("items-center gap-4"):
            if not app.storage.user.get('is_master'):
                schema = app.storage.user.get("schema", "não definido")
                ui.label(f"Schema: {schema}").classes("text-white text-sm")

            if com_filtro:
                ui.button("📅 FILTRO POR PERÍODO", on_click=lambda: app.storage.user['abrir_modal_filtro'](), icon="calendar_today") \
                    .classes("bg-blue-600 text-white")

            ui.button("LOGOUT", on_click=logout_usuario).classes("bg-blue-500 text-white")