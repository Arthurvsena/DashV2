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

def comparar_periodos(schema, func_query_faturamento):
    """
    Calcula os faturamentos do mês atual e anterior usando a função de query fornecida.
    
    Retorna: faturamento_atual, faturamento_anterior, indicador (🔼 ou 🔽), cor (classe CSS)
    """
    hoje = date.today()

    # Mês atual
    inicio_mes_atual = hoje.replace(day=1)
    fim_mes_atual = hoje

    # Mês anterior
    inicio_mes_anterior = (inicio_mes_atual - timedelta(days=1)).replace(day=1)
    fim_mes_anterior = inicio_mes_atual - timedelta(days=1)

    # Datas formatadas
    atual_de = inicio_mes_atual.strftime("%Y-%m-%d")
    atual_ate = fim_mes_atual.strftime("%Y-%m-%d")
    anterior_de = inicio_mes_anterior.strftime("%Y-%m-%d")
    anterior_ate = fim_mes_anterior.strftime("%Y-%m-%d")

    # Faturamento usando a função de query fornecida
    atual = func_query_faturamento(schema, atual_de, atual_ate)
    anterior = func_query_faturamento(schema, anterior_de, anterior_ate)

    # Indicador

    if anterior is None or anterior == 0:
        return atual, anterior, "⚠️", "text-yellow-400"

    if atual > anterior:
        return atual, anterior, "⬆️", "text-green-500"
    elif atual < anterior:
        return atual, anterior, "⬇️", "text-red-500"
    else:
        return atual, anterior, "➡️", "text-gray-400"

