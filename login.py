from nicegui import ui, app
from auth import gerar_token
from auth import get_user, verify_password
from style import aplicar_estilo_global, estilizar_botao_animado
from components.loading import mostrar_loading
from logger import log_sucesso, log_falha
import asyncio

async def login_page():
    aplicar_estilo_global()

    with ui.card().classes('absolute-center login-card') as card:  # <-- aplica classe do estilo global
        ui.image('Logo.png').classes('w-48 animate-pulse')  # Adiciona animação suave
        ui.label('Login - HelpSeller Dashboard').classes('text-xl text-white mb-4')

        # Inputs com props e classes padrão, o CSS global cuidará do resto
        username = ui.input('Usuário').props('outlined dense').classes('w-full')
        password = ui.input('Senha', password=True).props('outlined dense').classes('w-full')
        message = ui.label().classes('text-red-500 mt-2')

        async def tentar_login():
            try:
                user = get_user(username.value)
                if user and verify_password(password.value, user[1]):
                    app.storage.user.update({
                        'username': username.value,
                        'schema': user[2],
                        'is_master': user[3],
                    })
                    print("📦 Sessão após login:", app.storage.user)
                    log_sucesso(username.value)


                    token = gerar_token(username.value, user[2])
                    app.storage.user['token'] = token
                    # Mostra tela de loading e navega para dashboard
                    loading = mostrar_loading()
                    await asyncio.sleep(1.5)
                    loading.delete()
                    ui.navigate.to('/dashboard')
                else:
                    log_falha(username.value)
                    message.text = '❌ Usuário ou senha incorretos'
            except Exception as e:
                message.text = f'Erro no login: {e}'

        btn_login = ui.button("ENTRAR", on_click=tentar_login).classes('w-full mt-4 animated-button')
        estilizar_botao_animado(btn_login)
