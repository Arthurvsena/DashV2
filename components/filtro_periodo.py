from nicegui import ui, app
import datetime

def criar_filtro_periodo(ao_filtrar):
    with ui.dialog() as dialog, ui.card().classes("bg-[#1E1E1E] text-white p-6"):
        ui.label("Filtrar por Período").classes("text-lg font-bold mb-2")

        hoje = datetime.date.today()
        primeiro_dia = hoje.replace(day=1)

        date_range = ui.date(value=[primeiro_dia, hoje]).props("range filled").classes("bg-[#1E1E1E] text-white w-full")

        async def aplicar_filtro():
            valor = date_range.value
            try:
                if isinstance(valor, dict) and 'from' in valor and 'to' in valor:
                    inicio = valor['from']
                    fim = valor['to']
                elif isinstance(valor, list) and len(valor) == 2:
                    inicio = valor[0]
                    fim = valor[1]
                else:
                    raise ValueError("Selecione um intervalo válido")

                app.storage.user.update({
                    'filtro_data_inicio': str(inicio),
                    'filtro_data_fim': str(fim),
                })

                dialog.close()
                ui.navigate.to('/dashboard')

            except Exception as e:
                ui.notify(f"Erro ao aplicar filtro: {e}", type='negative')

        with ui.row().classes("justify-end w-full pt-4"):
            ui.button("Cancelar", on_click=dialog.close).props("flat")
            ui.button("Filtrar", on_click=aplicar_filtro).classes("bg-blue-600 text-white")

    return dialog

def abrir_modal_filtro():
    dialog = criar_filtro_periodo(lambda inicio, fim: None)
    dialog.open()