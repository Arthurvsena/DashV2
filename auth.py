# Arquivo: auth.py
import bcrypt
import jwt
import datetime
from database import get_connection

SECRET_KEY = "coloque_uma_chave_muito_secreta_aqui"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hash_password("help2025"))

def verify_password(password: str, hashed) -> bool:
    if not password or not hashed:
        return False

    if isinstance(hashed, memoryview):
        hashed = hashed.tobytes().decode()
    if isinstance(hashed, bytes):
        hashed = hashed.decode()

    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception as e:
        print(f"❌ Erro ao verificar senha: {e}")
        return False

def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT usuario, senha_hash, is_master, schemas_autorizados
            FROM public.usuarios
            WHERE usuario = %s;
            """,
            (username,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def gerar_token(usuario: str, schema: str, expiracao_min=120):
    payload = {
        "user": usuario,
        "schema": schema,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expiracao_min)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
