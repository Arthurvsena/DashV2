from nicegui import ui, app
from components.loading import mostrar_loading
from components.menu_lateral import criar_menu_lateral
from components.filtro_periodo import criar_filtro_periodo
from components.filtro_periodo import abrir_modal_filtro
from components.topbar import criar_topbar
from login import login_page
from pages.Dashboard import show_dashboard
from pages.Perfil_Usuario import show_profile
from pages.Produtos import show_produtos
from pages.Painel_Master import painel_master
from style import aplicar_estilo_global
from utils import logout_usuario


ui.add_head_html('''
<style>
  .q-menu {
    background-color: #1E1E1E !important;
    color: white !important;
  }

  .q-menu .q-item {
    color: white !important;
  }

  .q-menu .q-item--active {
    background-color: #333333 !important;
  }
</style>
''')



@ui.page('/')
async def index():
    ui.navigate.to('/login')

@ui.page('/login')
async def login():
    aplicar_estilo_global()
    app.storage.user['rota_atual'] = '/login'
    await login_page()

@ui.page('/dashboard')
async def dashboard():
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
        return

    aplicar_estilo_global()
    toggle_menu = criar_menu_lateral()

    filtro_dialog = criar_filtro_periodo(lambda inicio, fim: print(f"📅 Filtro aplicado de {inicio} até {fim}"))
    app.storage.user['rota_atual'] = '/dashboard'
    # Cabeçalho principal com menu e logout
    with ui.row().classes("w-full items-center justify-between px-4 py-2").style("border-bottom: 1px solid #333;"):
        ui.icon("menu").on("click", toggle_menu).classes("text-white cursor-pointer")
        ui.label("Help Seller").classes("text-xl font-bold text-[#08C5A1]")
        with ui.row().classes("items-center gap-2"):
            ui.label(f"Schema: {session.get('schema', '')}").classes("text-white text-sm")
            ui.button("📅 Filtro por Período", on_click=abrir_modal_filtro).classes("bg-blue-600 text-white")
            ui.button("Logout", on_click=logout_usuario).classes("bg-slate-400 text-white")

    loader = mostrar_loading("🔄 Carregando seu dashboard...")

    dashboard_container = ui.column().classes("w-full hidden")
    with dashboard_container:
        await show_dashboard()

    loader.close()
    dashboard_container.classes(remove='hidden')

@ui.page('/perfil')
async def perfil():
    aplicar_estilo_global()
    toggle_menu = criar_menu_lateral()
    app.storage.user['rota_atual'] = '/perfil'
    criar_topbar(toggle_menu=toggle_menu, com_filtro=False)

    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
    else:
        await show_profile()

@ui.page('/produtos')
async def produtos():
    aplicar_estilo_global()
    toggle_menu = criar_menu_lateral()
    app.storage.user['abrir_modal_filtro'] = abrir_modal_filtro
    app.storage.user['rota_atual'] = '/produtos'
    criar_topbar(toggle_menu=toggle_menu)

    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
    else:
        await show_produtos()

ui.run(storage_secret='helpseller2025')
