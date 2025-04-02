from nicegui import ui, app
from utils import logout_usuario, get_connection
import base64

def criar_menu_lateral():
    # Overlay escuro que fecha o menu ao clicar fora
    overlay = ui.element('div').classes(
        'fixed inset-0 z-40 hidden'
    ).style(
        'background-color: rgba(0, 0, 0, 0.4); backdrop-filter: blur(3px);'
    )

    # Menu lateral customizado
    menu = ui.element('aside').props('id=menu_lateral').classes(
        'fixed top-0 left-[-300px] h-full w-[250px] z-50 bg-[#111111] text-white shadow-xl transition-all duration-300'
    ).style(
        'padding-top: 20px;'  # Aumento do padding superior para adicionar espaço no topo
    )

    # Controle de estado interno
    menu_aberto = False

    # Recupera dados da sessão e do banco de dados
    session = app.storage.user
    usuario = session.get('username')

    nome_usuario = 'Usuário'
    foto_base64 = None

    if usuario:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT nome, foto FROM public.usuarios WHERE usuario = %s;", (usuario,))
            result = cur.fetchone()
            if result:
                nome_usuario = result[0] or 'Usuário'
                if result[1]:
                    foto_base64 = base64.b64encode(result[1]).decode()
            cur.close()
            conn.close()
        except Exception as e:
            print(f'⚠️ Erro ao carregar info do usuário: {e}')

    # Função de abrir/fechar
    def toggle_menu():
        nonlocal menu_aberto
        if not menu_aberto:
            menu.classes(remove='left-[-300px]')
            menu.classes(add='left-0')
            overlay.classes(remove='hidden')
        else:
            menu.classes(remove='left-0')
            menu.classes(add='left-[-300px]')
            overlay.classes(add='hidden')
        menu_aberto = not menu_aberto

    # Escuta o evento emitido pela topbar
    ui.on('toggle_menu', toggle_menu)

    # Clicar no overlay fecha o menu
    overlay.on('click', toggle_menu)

    # Conteúdo do menu
    with menu:
        with ui.row().classes('items-center gap-3 px-4 pb-4 border-b border-white/10'):
            if foto_base64:
                ui.image(f'data:image/png;base64,{foto_base64}').classes('w-10 h-10 rounded-full')
            else:
                ui.image(f'https://ui-avatars.com/api/?name={nome_usuario}&background=0D8ABC&color=fff&rounded=true').classes('w-10 h-10 rounded-full')

            with ui.column():
                ui.label(nome_usuario).classes('text-base font-semibold')
                ui.label('Ver perfil').classes('text-xs text-gray-400 cursor-pointer').on('click', lambda: (ui.navigate.to('/perfil'), toggle_menu()))

        ui.separator().classes('my-4')

        def menu_item(label: str, route: str, icon: str):
            with ui.row().classes(
                'w-full text-white cursor-pointer px-4 py-2 rounded transition-all duration-300 hover:bg-[#1E1E1E] hover:text-[#08C5A1]'
            ).on('click', lambda: (ui.navigate.to(route), toggle_menu())):
                ui.icon(icon).classes('text-white mr-2')
                ui.label(label).classes('text-sm')

        menu_item('Home', '/dashboard', 'house')
        menu_item('Produtos', '/produtos', 'widgets')
        menu_item('Vendas', '/produtos-sem-vendas', 'sell')
        menu_item('Financeiro', '/financeiro', 'attach_money')
        if app.storage.user.get('is_master'):
            menu_item('Painel Master', '/painel-master', 'business')

        ui.separator().classes('my-4')

        with ui.row().classes('text-red-400 hover:text-red-300 cursor-pointer px-2 py-2 rounded'):
            ui.element().on('click', lambda: (logout_usuario(), toggle_menu()))

        return toggle_menu
