# === Painel_Master.py Corrigido com lógica funcional ===

from nicegui import ui, app
from functools import partial
from components.menu_lateral import criar_menu_lateral
from components.topbar import criar_topbar
from style import aplicar_estilo_global
from utils import logout_usuario, executar_query_lista
from database import executar_comando
from auth import hash_password  # Importado para gerar senha segura

@ui.page('/painel-master')
async def painel_master():
    session = app.storage.user
    if not session.get('username'):
        ui.navigate.to('/login')
        return

    aplicar_estilo_global()
    toggle_menu = criar_menu_lateral()
    criar_topbar(toggle_menu=toggle_menu, com_filtro=False)

    if not session.get('is_master'):
        ui.notify('Acesso restrito ao Master')
        ui.navigate.to('/dashboard')
        return

    def carregar_pagina():
        ui.navigate.to('/painel-master')

    query_usuarios = "SELECT id, nome, usuario FROM usuarios ORDER BY nome;"
    usuarios = executar_query_lista(query_usuarios)

    with ui.row().classes("flex flex-wrap w-full px-8 mt-10 gap-6 items-start"):
        # Lista de usuários
        with ui.column().classes("flex-1 min-w-[300px] max-w-[50%] bg-[#1E1E1E] rounded-lg shadow-lg p-4 text-white"):
            ui.label("Usuários Cadastrados").classes("text-lg font-semibold mb-4")
            for user_id, nome_usuario, login_usuario in usuarios:
                with ui.row().classes("items-center gap-3 bg-[#2A2A2A] px-3 py-2 rounded mb-2 shadow-sm"):
                    ui.label(f"👤 {nome_usuario} ({login_usuario})").classes("flex-grow")

                    def excluir_usuario(uid=user_id):
                        executar_comando("DELETE FROM usuarios WHERE id = %s", (uid,))
                        ui.notify("Usuário excluído", type="positive")
                        carregar_pagina()

                    ui.icon('edit').classes("cursor-pointer text-yellow-400").tooltip("Editar")
                    ui.button(icon='close', on_click=excluir_usuario).props('flat dense round').classes("text-red-500").tooltip("Excluir")

        # Formulário
        with ui.column().classes("flex-1 min-w-[300px] max-w-[50%] bg-[#1E1E1E] rounded-lg shadow-lg p-6 text-white"):
            ui.label("Cadastro de Usuários").classes("text-2xl font-bold mb-4")

            nome = ui.input("Nome").classes("w-full mb-4").props("outlined")
            usuario = ui.input("Usuário").classes("w-full mb-4").props("outlined")
            senha = ui.input("Senha", password=True).props("outlined").classes("w-full mb-4")

            ui.label("Schema de Acesso").classes("text-white text-sm mb-2")
            schema_options = executar_query_lista(r'''
                SELECT schema_name FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'public')
                AND schema_name LIKE '%\_tiny'
                ORDER BY schema_name;
            ''')

            schema_choices = [schema[0] for schema in schema_options]
            selected_schema = {'value': ''}
            schema_buttons = {}

            def selecionar(s, b):
                selected_schema['value'] = s
                for btn in schema_buttons.values():
                    btn.classes(remove='bg-green-500')
                    btn.classes(add='bg-blue-500')
                    btn.update()
                b.classes(remove='bg-blue-500')
                b.classes(add='bg-green-500')
                b.update()
                ui.notify(f"Schema {s} selecionado")

            with ui.row().classes("flex flex-wrap gap-2 mb-4"):
                for schema in schema_choices:
                    display_name = schema.replace('_tiny', '').replace('_', ' ').title()
                    button = ui.button(display_name.upper()).classes("bg-blue-500 text-white")
                    button.on("click", partial(selecionar, s=schema, b=button))
                    schema_buttons[schema] = button

            is_master = ui.checkbox("Usuário Master").classes("mb-4")

            def cadastrar_usuario():
                if not all([nome.value, usuario.value, senha.value, selected_schema['value']]):
                    ui.notify("Preencha todos os campos", type='warning')
                    return

                try:
                    print("📝 Dados do cadastro:", nome.value, usuario.value, senha.value, selected_schema['value'], is_master.value)
                    senha_hash = hash_password(senha.value)
                    query = """
                        INSERT INTO usuarios (nome, usuario, senha_hash, schema_autorizado, is_master)
                        VALUES (%s, %s, %s, %s, %s);
                    """
                    executar_comando(query, (nome.value, usuario.value, senha_hash, selected_schema['value'], is_master.value))
                    ui.notify("Usuário cadastrado com sucesso!", type='positive')
                    carregar_pagina()
                except Exception as e:
                    print("❌ Erro ao cadastrar usuário:", e)
                    ui.notify("Erro ao cadastrar usuário", type='negative')

            ui.button("Cadastrar", on_click=cadastrar_usuario).classes("bg-gradient-to-r from-green-500 to-green-700 text-white w-full")

    # Listagem de schemas (Empresas)
    ui.label("Selecionar Empresa").classes("text-2xl font-bold text-white mb-4 mt-10 ml-4")

    query = r'''
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'public')
        ORDER BY schema_name;
    '''

    schemas = executar_query_lista(query)

    def acessar_empresa(schema):
        app.storage.user['schema'] = schema
        ui.navigate.to('/dashboard')

    with ui.row().classes("flex-wrap gap-4 p-4"):
        for (schema_name,) in schemas:
            if not schema_name.endswith('_tiny'):
                continue
            nome_formatado = schema_name.replace('_tiny', '').replace('_', ' ').title()
            with ui.card().classes("bg-[#1E1E1E] text-white w-[250px] h-[140px] p-4 flex flex-col justify-between shadow-lg hover:scale-[1.02] transition-transform"):
                ui.label(f"Empresa: {nome_formatado}").classes("text-md font-semibold")
                ui.button("Acessar", on_click=lambda s=schema_name: acessar_empresa(s)).classes("self-end bg-blue-600 text-white")
