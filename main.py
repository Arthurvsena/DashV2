# Arquivo: main.py
from nicegui import ui, app
from login import login_page
from pages.Dashboard import show_dashboard
from pages.Perfil_Usuario import show_profile
from pages.Produtos import show_produtos
from pages.Produtos_Sem_Vendas import show_produtos_sem_vendas
from pages.Painel_Master import show_painel_master
from style import aplicar_estilo_global

# ✅ Aplica os estilos globais uma vez para todo o app


@ui.page('/')
async def index():
        ui.navigate.to('/login')

@ui.page('/login')
async def login():
    aplicar_estilo_global()
    await login_page()

@ui.page('/dashboard')
async def dashboard():
    aplicar_estilo_global()
    
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
        return  # ⛔ Impede execução se não estiver logado
    
    await show_dashboard()

@ui.page('/perfil')
async def perfil():
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
    else:
        await show_profile()

@ui.page('/produtos')
async def produtos():
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
    else:
        await show_produtos()

@ui.page('/produtos-sem-vendas')
async def produtos_sem_vendas():
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
    else:
        await show_produtos_sem_vendas()

@ui.page('/painel-master')
async def painel_master():
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
    elif not session.get('is_master'):
        ui.notify('Acesso restrito ao Master')
        ui.navigate.to('/dashboard')
    else:
        await show_painel_master()

ui.run(storage_secret='helpseller2025')
