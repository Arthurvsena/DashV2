# Arquivo: components/loading.py
from nicegui import ui

def mostrar_loading():
    with ui.dialog() as dialog, ui.column().classes('items-center'):
        ui.image('Logo.png').classes('w-20 animate-pulse')
        ui.label('Carregando seu dashboard...').classes('text-white text-lg mt-2')
    
    dialog.open()
    return dialog
