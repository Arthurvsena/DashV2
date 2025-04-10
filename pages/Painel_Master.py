from nicegui import ui, app
from functools import partial
from components.menu_lateral import criar_menu_lateral
from components.topbar import criar_topbar
from style import aplicar_estilo_global
from utils import logout_usuario, executar_query_lista, get_schemas_do_usuario_logado
from database import executar_comando
from auth import hash_password

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

        with ui.column().classes("flex-1 min-w-[300px] max-w-[50%] bg-[#1E1E1E] rounded-lg shadow-lg p-6 text-white"):
            ui.label("Cadastro de Usuários").classes("text-2xl font-bold mb-4")

            nome = ui.input("Nome").classes("w-full mb-4").props("outlined")
            usuario = ui.input("Usuário").classes("w-full mb-4").props("outlined")
            senha = ui.input("Senha", password=True).props("outlined").classes("w-full mb-4")
            is_master = ui.checkbox("Usuário Master").classes("mb-4")

            ui.label("Schemas de Acesso").classes("text-white text-sm mb-2")

            botoes_disponiveis = {}
            botoes_selecionados = {}
            selected_schemas = set()

            if session.get('is_master'):
                schemas_autorizados = get_schemas_do_usuario_logado(session)
            else:
                schemas_autorizados = session.get('schemas_autorizados', [])

            schemas_mapeados = []
            for schema in schemas_autorizados:
                schema_real = schema if schema.endswith('_tiny') else f"{schema}_tiny"
                label = schema_real.replace('_tiny', '').replace('_', ' ').title()
                schemas_mapeados.append((label, schema_real))

            ui.label("Selecionados").classes("text-sm text-white font-medium mt-2")
            with ui.row().classes("gap-2 flex-wrap mb-4") as row_selecionados:
                pass

            ui.label("Disponíveis").classes("text-sm text-white font-medium mt-2")
            with ui.row().classes("gap-2 flex-wrap mb-4") as row_disponiveis:
                pass

            def adicionar_schema(schema_real):
                if not is_master.value and len(selected_schemas) >= 1:
                    ui.notify("Para selecionar mais de 1 empresa, o usuário deve ser master", type='warning', position='top', close_button='Fechar')
                    return
                if schema_real not in selected_schemas:
                    selected_schemas.add(schema_real)
                    btn_disp = botoes_disponiveis.pop(schema_real)
                    btn_disp.delete()
                    with row_selecionados:
                        btn_sel = ui.button(
                            schema_real.replace('_tiny', '').replace('_', ' ').title().upper(),
                            on_click=partial(remover_schema, schema_real)
                        ).classes("bg-green-600 bg-opacity-50 hover:bg-opacity-80 transition-all text-white px-3 py-1 rounded-md font-medium").tooltip("Clique para remover")
                        botoes_selecionados[schema_real] = btn_sel

            def remover_schema(schema_real):
                if schema_real in selected_schemas:
                    selected_schemas.remove(schema_real)
                    btn_sel = botoes_selecionados.pop(schema_real)
                    btn_sel.delete()
                    with row_disponiveis:
                        btn_disp = ui.button(
                            schema_real.replace('_tiny', '').replace('_', ' ').title().upper(),
                            on_click=partial(adicionar_schema, schema_real)
                        ).classes("bg-blue-600 bg-opacity-50 hover:bg-opacity-80 transition-all text-white px-3 py-1 rounded-md font-medium")
                        botoes_disponiveis[schema_real] = btn_disp

            for label, schema_real in schemas_mapeados:
                with row_disponiveis:
                    btn = ui.button(
                        label.upper(),
                        on_click=partial(adicionar_schema, schema_real)
                    ).classes("bg-blue-600 bg-opacity-50 hover:bg-opacity-80 transition-all text-white px-3 py-1 rounded-md font-medium")
                    botoes_disponiveis[schema_real] = btn

            def cadastrar_usuario():
                if not all([nome.value, usuario.value, senha.value, selected_schemas]):
                    ui.notify("Preencha todos os campos e selecione pelo menos um schema!", type='warning')
                    return
                try:
                    senha_hash = hash_password(senha.value)
                    schemas_salvar = [s if s.endswith('_tiny') else f"{s}_tiny" for s in selected_schemas]
                    query = """
                        INSERT INTO usuarios (nome, usuario, senha_hash, is_master, schemas_autorizados)
                        VALUES (%s, %s, %s, %s, %s);
                    """
                    executar_comando(query, (
                        nome.value, usuario.value, senha_hash, is_master.value, schemas_salvar
                    ))
                    ui.notify("Usuário cadastrado com sucesso!", type='positive')
                    carregar_pagina()
                except Exception as e:
                    ui.notify(f"Erro ao cadastrar usuário: {e}", type='negative')

            ui.button("Cadastrar", on_click=cadastrar_usuario).classes("bg-gradient-to-r from-green-500 to-green-700 text-white w-full")

    # LISTAGEM DE EMPRESAS
    ui.label("Selecionar Empresa").classes("text-2xl font-bold text-white mb-4 mt-10 ml-4")

    query = '''
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'public')
        ORDER BY schema_name;
    '''
    schemas = executar_query_lista(query)

    schemas_autorizados = session.get('schemas_autorizados', [])
    schemas_autorizados_ok = {s.strip().lower() for s in schemas_autorizados}

    def acessar_empresa(schema):
        app.storage.user['schema'] = schema
        ui.navigate.to('/dashboard')

    with ui.row().classes("flex-wrap gap-4 p-4"):
        for (schema_name,) in schemas:
            schema_name = schema_name.strip().lower()
            if not schema_name.endswith('_tiny'):
                continue
            if not session.get('is_master') and schema_name not in schemas_autorizados_ok:
                continue
            nome_formatado = schema_name.replace('_tiny', '').replace('_', ' ').title()
            with ui.card().classes("bg-[#1E1E1E] text-white w-[250px] h-[140px] p-4 flex flex-col justify-between shadow-lg hover:scale-[1.02] transition-transform"):
                ui.label(f"Empresa: {nome_formatado}").classes("text-md font-semibold")
                ui.button("Acessar", on_click=lambda s=schema_name: acessar_empresa(s)).classes("self-end bg-blue-600 text-white")
