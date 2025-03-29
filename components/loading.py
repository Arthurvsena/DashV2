# Arquivo: components/loading.py
from nicegui import ui

def mostrar_loading(msg="🔄 Carregando dados..."):
    with ui.dialog() as dialog:
        with ui.column().classes('items-center justify-center p-10').style('background-color: #0e1117; border-radius: 12px;'):
            ui.image('Logo.png').classes('w-24 animate-pulse')
            ui.label(msg).classes('text-white text-lg mt-4')
    dialog.open()
    return dialog
