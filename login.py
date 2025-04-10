from nicegui import ui, app
from auth import gerar_token, get_user, verify_password
from style import aplicar_estilo_global, estilizar_botao_animado
from components.loading import mostrar_loading
from logger import log_sucesso, log_falha
from database import buscar_usuario_por_email, atualizar_senha_temporaria
from utils import gerar_senha_provisoria, enviar_email, listar_todos_schemas
from functools import partial
import asyncio

async def login_page():
    aplicar_estilo_global()

    with ui.card().classes('absolute-center login-card') as card:
        ui.image('Logo.png').classes('w-48 animate-pulse')
        ui.label('Login - HelpSeller Dashboard').classes('text-xl text-white mb-4')

        username = ui.input('Usuário').props('outlined dense').classes('w-full')
        password = ui.input('Senha', password=True).props('outlined dense').classes('w-full')
        message = ui.label().classes('text-red-500 mt-2')

        async def redirecionar(schema_escolhido, user_data):
            app.storage.user.update({
                'username': username.value,
                'is_master': user_data[2],
                'schemas_autorizados': user_data[3],
                'schema': schema_escolhido,
            })
            token = gerar_token(username.value, schema_escolhido)
            app.storage.user['token'] = token
            loading = mostrar_loading()
            await asyncio.sleep(1.5)
            loading.delete()
            if user_data[2]:
                ui.navigate.to('/painel-master')
            else:
                ui.navigate.to('/dashboard')

        async def escolher_schema(schema_escolhido, user_data, dialog):
            dialog.close()
            await redirecionar(schema_escolhido, user_data)

        async def tentar_login():
            app.storage.user.clear()
            try:
                print("🚀 Tentando login...")
                print(f"🧾 Usuário digitado: {username.value}")
                print(f"🔑 Senha digitada: {password.value}")

                user = get_user(username.value)  # [usuario, senha_hash, is_master, schemas_autorizados]
                print(f"📦 Resultado do get_user: {user}")

                if user:
                    senha_valida = verify_password(password.value, user[1])
                    print(f"✅ Resultado da verificação da senha: {senha_valida}")

                    if senha_valida:
                        log_sucesso(username.value)
                        schemas_autorizados = user[3] or []

                        # Admin acessa todos os schemas do banco
                        if username.value.lower() == 'admin':
                            schemas_autorizados = listar_todos_schemas()

                        if not schemas_autorizados:
                            message.text = '❌ Nenhum schema autorizado para este usuário.'
                            return

                        # Master com múltiplos schemas → abre pop-up
                        if user[2] and len(schemas_autorizados) > 1:
                            with ui.dialog() as dialog, ui.card().classes('bg-gray-900 text-white'):
                                ui.label('Escolha o schema que deseja acessar:').classes('text-lg mb-2')
                                for s in schemas_autorizados:
                                    ui.button(
                                        s.upper(),
                                        on_click=partial(escolher_schema, s, user, dialog)
                                    ).classes('mb-1')
                            dialog.open()
                        else:
                            # Apenas 1 schema autorizado
                            await redirecionar(schemas_autorizados[0], user)
                        return
                    else:
                        print("❌ Senha inválida.")
                else:
                    print("❌ Usuário não encontrado.")
                log_falha(username.value)
                message.text = '❌ Usuário ou senha incorretos'

            except Exception as e:
                print(f"❌ Erro no login: {e}")
                message.text = f'Erro no login: {e}'

        btn_login = ui.button("ENTRAR", on_click=tentar_login).classes('w-full mt-4 animated-button')
        estilizar_botao_animado(btn_login)

        def abrir_dialog_esqueci_senha():
            with ui.dialog() as dialog, ui.card().classes('bg-gray-900 text-white'):
                ui.label('Recuperação de Senha').classes('text-lg mb-2')
                email_input = ui.input('Digite seu e-mail').props('outlined dense').classes('w-full')
                mensagem = ui.label().classes('text-red-400 mt-2')

                def enviar_senha():
                    usuario = buscar_usuario_por_email(email_input.value)
                    if usuario:
                        senha_temp = gerar_senha_provisoria()
                        from auth import hash_password
                        senha_hash = hash_password(senha_temp)
                        atualizar_senha_temporaria(email_input.value, senha_hash)
                        enviar_email(email_input.value, senha_temp)
                        mensagem.text = '✅ Verifique seu e-mail. Enviamos uma senha provisória.'
                    else:
                        mensagem.text = '❌ E-mail não encontrado'

                ui.button('Enviar senha provisória', on_click=enviar_senha).classes('mt-3')

            dialog.open()

        ui.button('Esqueci minha senha', on_click=abrir_dialog_esqueci_senha).props('flat').classes('mt-2 text-white')
