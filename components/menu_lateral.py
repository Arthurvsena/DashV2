from nicegui import ui,app
from utils import logout_usuario

def criar_menu_lateral():
    overlay = ui.element('div').classes(
        'fixed inset-0 z-40 hidden'
    ).style('background-color: rgba(0, 0, 0, 0.4); backdrop-filter: blur(3px);')

    menu = ui.left_drawer().props('overlay').classes(
        'bg-[#111111] text-white shadow-2xl z-50 px-4 pt-4'
    ).style(
        'backdrop-filter: blur(4px); box-shadow: 0 0 15px rgba(0,0,0,0.6); width: 250px;'
    )

    menu_aberto = False
    menu.toggle()

    def toggle_menu():
        nonlocal menu_aberto
        menu.toggle()
        menu_aberto = not menu_aberto
        if menu_aberto:
            overlay.classes(remove='hidden')
        else:
            overlay.classes('hidden')

    with menu:
        # Perfil
        with ui.row().classes('items-center gap-3 px-2 pb-4 border-b border-white/10'):
            ui.image('https://ui-avatars.com/api/?name=User&background=0D8ABC&color=fff&rounded=true').classes('w-10 h-10 rounded-full')
            with ui.column():
                ui.label('Usuário').classes('text-base font-semibold')
                ui.label('Ver perfil').classes('text-xs text-gray-400 cursor-pointer').on('click', lambda: (ui.navigate.to('/perfil'), toggle_menu()))

        ui.separator().classes('my-4')

        def menu_item(label: str, route: str):
            with ui.row().classes(
                'w-full text-white cursor-pointer px-2 py-2 rounded transition-all duration-300 hover:bg-[#1E1E1E] hover:text-[#08C5A1]'
            ).on('click', lambda: (ui.navigate.to(route), toggle_menu())):
                ui.label(label).classes('text-sm')

        # Itens do menu
        menu_item('Dashboard', '/dashboard')
        menu_item('Produtos', '/produtos')
        menu_item('Sem Vendas', '/produtos-sem-vendas')
        if app.storage.user.get('is_master'):
            menu_item('Alterar Empresa', '/painel-master')

        ui.separator().classes('my-4')

        # Sair
        with ui.row().classes('text-red-400 hover:text-red-300 cursor-pointer px-2 py-2 rounded'):
            ui.label('Sair').classes('text-sm')
            ui.element().on('click', lambda: (logout_usuario(), toggle_menu()))

    overlay.on('click', toggle_menu)

    return toggle_menu
