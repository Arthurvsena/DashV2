# logger.py
import logging

logging.basicConfig(
    filename='logins.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_sucesso(usuario):
    logging.info(f"✅ Login bem-sucedido para: {usuario}")

def log_falha(usuario):
    logging.warning(f"❌ Tentativa de login falhou para: {usuario}")
