from db.db_manager import DBManager
from collections import defaultdict

def listar_empresas():
    conn = DBManager.instance().get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, razao_social FROM empresas")
            return cursor.fetchall()
    except Exception as e:
        print("Erro ao listar empresas:", e)
        return []
    finally:
        conn.close()

def listar_usuarios(empresa_id):
    conn = DBManager.instance().get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, nome, empresa_id FROM users WHERE empresa_id = %s", (empresa_id,))
            return cursor.fetchall()
    except Exception as e:
        print("Erro ao listar usuarios:", e)
        return []
    finally:
        conn.close()

def adicionar_usuario(nome, senha, empresa_id):
    conn = DBManager.instance().get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (nome, senha, empresa_id) VALUES (%s, %s, %s)", (nome, senha, empresa_id))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao adicionar usuario:", e)
        return False
    finally:
        conn.close()

def remover_usuario(user_id):
    conn = DBManager.instance().get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao remover usuario:", e)
        return False
    finally:
        conn.close()

def buscar_todos_usuarios(conn):
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT users.id, users.nome, users.email, empresas.razao_social AS empresa
            FROM users
            LEFT JOIN empresas ON users.empresa_id = empresas.id
            ORDER BY users.nome
        """)
        return cursor.fetchall()

def contar_usuarios():
    conn = DBManager.instance().get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

def listar_ultimos_usuarios(limit=4):
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT nome, criado_em
                FROM users
                ORDER BY criado_em DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
    finally:
        conn.close()

def contar_usuarios_mes_atual() -> int:
    conn = DBManager.instance().get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM users
        WHERE MONTH(data_cadastro) = MONTH(NOW())
          AND YEAR(data_cadastro) = YEAR(NOW())
    """)
    total = cursor.fetchone()[0]
    conn.close()
    return total
