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
    schema = session.get("schema", "public")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT nome, foto, is_master FROM public.usuarios WHERE usuario = %s", (usuario_logado,))
    result = cur.fetchone()
    nome_atual, foto_base64, is_master = result if result else ("", "", False)

    def salvar():
        try:
            if senha_input.value:
                senha_hash = hash_password(senha_input.value)
                cur.execute("UPDATE public.usuarios SET senha_hash = %s WHERE usuario = %s", (senha_hash, usuario_logado))

            if foto_input.files:
                conteudo = foto_input.files[0].content.read()
                base64_foto = base64.b64encode(conteudo).decode("utf-8")
                cur.execute("UPDATE public.usuarios SET foto = %s WHERE usuario = %s", (base64_foto, usuario_logado))

            conn.commit()
            ui.notify("Dados atualizados com sucesso!", duration=5000)
        except Exception as e:
            ui.notify(f"Erro ao atualizar: {e}", type='negative', duration=5000)

    # === POPUP DE DADOS DA EMPRESA ===
    popup_empresa = ui.dialog()
    with popup_empresa, ui.card().classes('w-full max-w-2xl p-6').style('background-color: #1e1e1e; color: white; border-radius: 8px;'):
        ui.label("🏢 Dados da Empresa").classes("text-xl font-bold mb-4 text-center")

        nome_input_e = ui.input(label="Nome da Empresa").props('dense').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')
        cnpj_input = ui.input(label="CNPJ").props('dense').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')
        tel_input = ui.input(label="Telefone").props('dense').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')
        end_input = ui.input(label="Endereço").props('dense').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')

        regime_input = ui.select(
            label="Regime Tributário",
            options=["MEI", "Simples", "Regime Lucro Real", "Regime Lucro Presumido"]
        ).props('dense dark').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')
        
        custo_input = ui.input(label="Custo Operacional").props('dense').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')
        lucro_b_input = ui.input(label="Lucro Bruto Desejado (%)").props('dense').classes("w-full mb-3 text-white").style('background-color: #2a2a2a; border-radius: 8px;')
        lucro_l_input = ui.input(label="Lucro Líquido Mínimo (%)").props('dense').classes("w-full mb-4 text-white").style('background-color: #2a2a2a; border-radius: 8px;')

        def salvar_empresa():
            try:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s AND table_name = 'empresa'
                    );
                """, (schema,))
                existe_empresa = cur.fetchone()[0]

                if not existe_empresa:
                    cur.execute(f"""
                        CREATE TABLE {schema}.empresa (
                            id SERIAL PRIMARY KEY,
                            nome_empresa TEXT,
                            cnpj TEXT,
                            telefone TEXT,
                            endereco TEXT,
                            regime_tributario TEXT,
                            custo_operacional NUMERIC,
                            lucro_bruto_desejado NUMERIC,
                            lucro_liquido_minimo NUMERIC
                        );
                    """)

                cur.execute(f"SELECT COUNT(*) FROM {schema}.empresa;")
                empresa_existe = cur.fetchone()[0] > 0

                if empresa_existe:
                    cur.execute(
                        f"""UPDATE {schema}.empresa 
                            SET nome_empresa=%s, cnpj=%s, telefone=%s, endereco=%s, regime_tributario=%s,
                                custo_operacional=%s, lucro_bruto_desejado=%s, lucro_liquido_minimo=%s""",
                        (nome_input_e.value, cnpj_input.value, tel_input.value, end_input.value, regime_input.value,
                         custo_input.value, lucro_b_input.value, lucro_l_input.value)
                    )
                else:
                    cur.execute(
                        f"""INSERT INTO {schema}.empresa 
                            (nome_empresa, cnpj, telefone, endereco, regime_tributario, custo_operacional, lucro_bruto_desejado, lucro_liquido_minimo)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (nome_input_e.value, cnpj_input.value, tel_input.value, end_input.value, regime_input.value,
                         custo_input.value, lucro_b_input.value, lucro_l_input.value)
                    )

                conn.commit()
                popup_empresa.close()
                ui.notify("Dados da empresa salvos com sucesso!", duration=5000)
            except Exception as e:
                ui.notify(f"Erro ao salvar dados da empresa: {e}", type='negative')

        with ui.row().classes("justify-end"):
            ui.button("Salvar", on_click=salvar_empresa).classes("w-full").style('background-color: #22c55e; opacity: 0.8; color: white; border-radius: 6px;').on('mouseover', lambda e: e.sender.style('opacity: 1'))

    # === TELA DE PERFIL ===
    with ui.card().classes('w-full max-w-3xl mx-auto mt-8 p-6 rounded-lg shadow-xl').style('background-color: #1e1e1e; color: white;'):
        ui.label("👤 Perfil do Usuário").classes("text-2xl font-bold mb-6 text-center")

        nome_input = ui.input(label="Nome", value=nome_atual).classes("w-full mb-4 text-white").props('dense').style('background-color: #2a2a2a; border-radius: 8px;')
        senha_input = ui.input(label="Nova senha", password=True).classes("w-full mb-4 text-white").props('dense').style('background-color: #2a2a2a; border-radius: 8px;')

        if foto_base64:
            ui.image(f"data:image/png;base64,{foto_base64}").classes("w-32 h-32 rounded-full mb-4")

        foto_input = ui.upload(label="Nova foto (opcional)", max_files=1).classes("w-full mb-6 q-uploader--dark text-white").props('flat bordered').style("""
            background-color: #2a2a2a;
            border-radius: 8px;
            color: white;
            border: 1px solid #444;
        """)

        if is_master:
            ui.button("Dados da Empresa", on_click=popup_empresa.open).classes("w-full mb-3").style(
                'background-color: #4A90E2; opacity: 0.8; color: white; border-radius: 6px;'
            ).on('mouseover', lambda e: e.sender.style('opacity: 1'))

            ui.button("Configuração dos Marketplaces", on_click=lambda: ui.notify("Abrindo configuração dos marketplaces...")).classes("w-full mb-6").style('background-color: #4A90E2; opacity: 0.8; color: white; border-radius: 6px;').on('mouseover', lambda e: e.sender.style('opacity: 1'))

        ui.button("Salvar", on_click=salvar).classes("w-full").style('background-color: #22c55e; opacity: 0.8; color: white; border-radius: 6px;').on('mouseover', lambda e: e.sender.style('opacity: 1'))