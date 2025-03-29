# Arquivo: utils.py
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import os
from io import BytesIO
from PIL import Image
from nicegui import app, ui
from datetime import date, timedelta



def exibir_loader(msg="🔄 Carregando dados..."):
    html = f"""
    <style>
    #customLoader {{
        position: fixed;
        z-index: 9999;
        top: 0; left: 0; right: 0; bottom: 0;
        background: #0e1117;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 1.6em;
        color: #08C5A1;
        font-family: 'Segoe UI', sans-serif;
    }}
    .loader-spinner {{
        border: 6px solid #f3f3f3;
        border-top: 6px solid #08C5A1;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }}
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    <div id="customLoader">
        <div class="loader-spinner"></div>
        <div>{msg}</div>
    </div>
    """
    ui.html(html)

def parar_carregamento():
    ui.html("""
    <script>
        const el = window.parent.document.getElementById("customLoader");
        if (el) {
            el.style.transition = "opacity 0.5s ease";
            el.style.opacity = 0;
            setTimeout(() => el.remove(), 500);
        }
    </script>
    """)

def checar_login():
    if not app.storage.user.get('username'):
        ui.notify('Você precisa estar logado para acessar esta página.', color='negative')
        ui.navigate.to('/')
        return False
    return True

def carregar_logo_global():
    from database import get_connection
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT logo FROM public.global_config WHERE id = 1;")
        result = cur.fetchone()
        if result and result[0]:
            imagem = BytesIO(result[0])
            return Image.open(imagem)
    except Exception as e:
        print("Erro ao carregar logo:", e)
    finally:
        cur.close()
        conn.close()
    return None

def get_engine():
    user = os.getenv("POSTGRESQL_USER")
    password = os.getenv("POSTGRESQL_PASSWORD")
    host = os.getenv("POSTGRESQL_HOST")
    db = os.getenv("POSTGRESQL_DB")
    port = os.getenv("POSTGRESQL_PORT", "5432")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(url)
    return engine

def get_connection():
    user = os.getenv("POSTGRESQL_USER")
    password = os.getenv("POSTGRESQL_PASSWORD")
    host = os.getenv("POSTGRESQL_HOST")
    db = os.getenv("POSTGRESQL_DB")
    port = os.getenv("POSTGRESQL_PORT", "5432")

    return psycopg2.connect(
        dbname=db,
        user=user,
        password=password,
        host=host,
        port=port
    )

def load_data(query: str) -> pd.DataFrame:
    if isinstance(query, pd.DataFrame):
        return query

    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    except UnicodeDecodeError:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=colnames)
            cur.close()
            conn.close()
            return df
        except Exception as e2:
            print("Erro ao executar a query (LATIN1 fallback):", e2)
            return pd.DataFrame()
    except Exception as e:
        print("Erro inesperado ao executar a query:", e)
        return pd.DataFrame()

def convert_to_datetime(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    if col_name in df.columns:
        df[col_name] = pd.to_datetime(df[col_name], errors="coerce", dayfirst=True)
        if pd.api.types.is_datetime64tz_dtype(df[col_name]):
            df[col_name] = df[col_name].dt.tz_localize(None)
    return df

def logout_usuario():
    app.storage.user.clear()
    ui.notify('Logout realizado com sucesso ✅', color='positive') 
    ui.navigate.to('/login')  # volta para login


from datetime import datetime, timedelta

def comparar_periodos(schema, func, inicio_str, fim_str):
    from datetime import datetime, timedelta
    hoje = datetime.today().date()

    inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
    fim = datetime.strptime(fim_str, "%Y-%m-%d").date()
    intervalo = fim - inicio

    # Verifica se o período é futuro
    if inicio > hoje:
        # Projeção: média dos últimos 6 meses
        total_meses = 6
        soma = 0

        for i in range(1, total_meses + 1):
            inicio_mes = (hoje.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            fim_mes = (inicio_mes.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            inicio_mes_str = inicio_mes.strftime("%Y-%m-%d")
            fim_mes_str = fim_mes.strftime("%Y-%m-%d")

            valor_mes = func(schema, inicio_mes_str, fim_mes_str)
            soma += valor_mes or 0

        media = soma / total_meses

        qtd_meses_futuros = max(1, intervalo.days // 30)
        valor_projetado = media * qtd_meses_futuros

        return valor_projetado, media, f"Projeção com base nos últimos {total_meses} meses", "text-yellow-400"

    else:
        # Cálculo normal (comparação com período anterior)
        inicio_anterior = inicio - intervalo - timedelta(days=1)
        fim_anterior = inicio - timedelta(days=1)

        inicio_anterior_str = inicio_anterior.strftime("%Y-%m-%d")
        fim_anterior_str = fim_anterior.strftime("%Y-%m-%d")

        valor_atual = func(schema, inicio_str, fim_str)
        valor_anterior = func(schema, inicio_anterior_str, fim_anterior_str)

        if not valor_anterior or valor_anterior == 0:
            indicador = "↑ 100%" if valor_atual > 0 else "0%"
            cor = "text-blue-500" if valor_atual >= 0 else "text-red-500"
        else:
            variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
            seta = "↑" if variacao >= 0 else "↓"
            cor = "text-blue-500" if variacao >= 0 else "text-red-500"
            indicador = f"{seta} {abs(variacao):.2f}%"

        return valor_atual, valor_anterior, indicador, cor
    
def prever_valor_futuro(schema, func, data_inicio, data_fim):
    hoje = datetime.today().date()
    intervalo_futuro = (data_fim - data_inicio).days
    meses_futuros = max(1, intervalo_futuro // 30)

    soma = 0
    valores = []

    for i in range(1, 7):  # últimos 6 meses
        inicio_mes = (hoje.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        fim_mes = (inicio_mes.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        inicio_mes_str = inicio_mes.strftime("%Y-%m-%d")
        fim_mes_str = fim_mes.strftime("%Y-%m-%d")

        valor = func(schema, inicio_mes_str, fim_mes_str) or 0
        valores.append(valor)
        soma += valor

    media = soma / 6
    valor_projetado = media * meses_futuros

    # Comparar os últimos dois meses para detectar tendência
    if len(valores) >= 2:
        seta = "🔺" if valores[-1] > valores[-2] else "🔻"
        cor = "text-green-500" if valores[-1] > valores[-2] else "text-red-500"
    else:
        seta = "➖"
        cor = "text-gray-400"

    return valor_projetado, media, seta, cor