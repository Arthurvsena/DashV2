# Arquivo: Painel_Master.py
from nicegui import ui, app
import pandas as pd
from utils import get_connection
from auth import hash_password

async def show_painel_master():
    session = app.storage.user
    if not session.get('username'):
        ui.notify('Sessão expirada')
        ui.open('/login')
        return

    if not session.get("is_master", False):
        ui.notify("Acesso restrito ao Master")
        ui.open("/dashboard")
        return

    schema = session.get("schema")
    ui.label(f"🔧 Painel Master - Schema atual: {schema}").classes("text-2xl")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT usuario, is_master, schema_autorizado, nome FROM public.usuarios")
    usuarios = cur.fetchall()
    df = pd.DataFrame(usuarios, columns=["Usuário", "Master", "Schema", "Nome"])

    with ui.expansion("Usuários cadastrados", value=True).classes("w-full"):
        ui.table(columns=[
            {'name': col, 'label': col, 'field': col} for col in df.columns
        ], rows=df.to_dict("records"), row_key='Usuário').classes("w-full")

    with ui.expansion("Cadastrar novo usuário"):
        novo_user = ui.input("Novo usuário").classes("w-full")
        nome = ui.input("Nome").classes("w-full")
        senha = ui.input("Senha", password=True).classes("w-full")
        schema_aut = ui.input("Schema autorizado").classes("w-full")
        is_master_input = ui.checkbox("É master?")

        def cadastrar():
            try:
                senha_hash = hash_password(senha.value)
                cur.execute(
                    """
                    INSERT INTO public.usuarios (usuario, senha_hash, is_master, schema_autorizado, nome)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (novo_user.value, senha_hash, is_master_input.value, schema_aut.value, nome.value)
                )
                conn.commit()
                ui.notify("Usuário cadastrado com sucesso!")
            except Exception as e:
                ui.notify(f"Erro ao cadastrar: {e}", type='negative')

        ui.button("Salvar", on_click=cadastrar).classes("mt-4")