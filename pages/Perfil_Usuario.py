# Arquivo: Perfil_Usuario.py
from nicegui import ui, app
from utils import get_connection
from auth import hash_password
import base64

async def show_profile():
    session = app.storage.user
    if not session.get("username"):
        ui.notify("Você precisa estar logado.")
        ui.open("/login")
        return

    usuario_logado = session.get("username")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT nome, foto, custos_fixos FROM public.usuarios WHERE usuario = %s", (usuario_logado,))
    result = cur.fetchone()
    nome_atual, foto_base64, custos_fixos = result if result else ("", "", 0)

    ui.label("👤 Perfil do Usuário").classes("text-2xl")
    nome_input = ui.input("Nome", value=nome_atual).classes("w-full")
    senha_input = ui.input("Nova senha", password=True).classes("w-full")
    custo_input = ui.input("Custos fixos", value=str(custos_fixos)).props("type=number").classes("w-full")

    foto_input = ui.upload(label="Nova foto (opcional)", max_files=1)
    if foto_base64:
        ui.image(f"data:image/png;base64,{foto_base64}").classes("w-32")

    def salvar():
        try:
            if senha_input.value:
                senha_hash = hash_password(senha_input.value)
                cur.execute("UPDATE public.usuarios SET senha_hash = %s WHERE usuario = %s", (senha_hash, usuario_logado))

            cur.execute("UPDATE public.usuarios SET nome = %s, custos_fixos = %s WHERE usuario = %s", (nome_input.value, custo_input.value, usuario_logado))

            if foto_input.files:
                conteudo = foto_input.files[0].content.read()
                base64_foto = base64.b64encode(conteudo).decode("utf-8")
                cur.execute("UPDATE public.usuarios SET foto = %s WHERE usuario = %s", (base64_foto, usuario_logado))

            conn.commit()
            ui.notify("Dados atualizados com sucesso!")
        except Exception as e:
            ui.notify(f"Erro ao atualizar: {e}", type='negative')

    ui.button("Salvar", on_click=salvar).classes("mt-4")