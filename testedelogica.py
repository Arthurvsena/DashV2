from auth import hash_password
from database import get_connection

def criar_usuario(usuario: str, senha: str, email: str, is_master: bool, schemas: list[str]):
    senha_hash = hash_password(senha)

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO public.usuarios (usuario, senha_hash, is_master, email, schemas_autorizados)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (usuario) DO UPDATE
            SET senha_hash = EXCLUDED.senha_hash,
                is_master = EXCLUDED.is_master,
                email = EXCLUDED.email,
                schemas_autorizados = EXCLUDED.schemas_autorizados
        """, (usuario, senha_hash, is_master, email, schemas))
        conn.commit()
        print(f"✅ Usuário '{usuario}' criado/atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
    finally:
        cur.close()
        conn.close()

# ============================
# EXEMPLO DE USO:
# ============================
if __name__ == "__main__":
    criar_usuario(
        usuario='helpseller',
        senha='help2025',
        email='helpseller@helpseller.com',
        is_master=True,
        schemas=[
            'apj_tiny',
            'asthouse_tiny',
            'bike_mania_tiny',
            'bike_mania_tiny_serverapi',
            'ceu_azul_tiny',
            'chic_bacanizado_tiny',
            'paraiso_fab_brinq_tiny',
            'rio_branco_tiny',
            'the_prime_place_tiny'
        ]
    )
