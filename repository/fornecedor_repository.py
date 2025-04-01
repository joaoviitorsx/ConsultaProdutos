from db.db_manager import DBManager
from collections import defaultdict

def buscar_fornecedor_por_cnpj(empresa_id: int, cnpj: str) -> dict | None:
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return None

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM fornecedores
                WHERE empresa_id = %s AND cnpj = %s
                LIMIT 1
            """, (empresa_id, cnpj))
            return cursor.fetchone()

    except Exception as e:
        print(f"Erro ao buscar fornecedor por empresa: {e}")
        return None

    finally:
        if conn:
            conn.close()


def buscar_fornecedor_global(cnpj: str) -> dict | None:
    """Busca fornecedor sem filtrar por empresa (usado por admin)."""
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return None

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM fornecedores
                WHERE cnpj = %s
                LIMIT 1
            """, (cnpj,))
            return cursor.fetchone()

    except Exception as e:
        print(f"Erro ao buscar fornecedor globalmente: {e}")
        return None

    finally:
        if conn:
            conn.close()


def inserir_fornecedor(
    empresa_id: int,
    cnpj: str,
    razao_social: str,
    cnae_codigo: str,
    isento: bool,
    uf: str,
    simples: bool
) -> tuple[bool, str]:
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return False, "Erro na conexão com o banco de dados."

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM fornecedores WHERE empresa_id = %s AND cnpj = %s
                """, (empresa_id, cnpj))

            if cursor.fetchone():
                return False, "Fornecedor já cadastrado." 

            cursor.execute("""
                INSERT INTO fornecedores (
                    empresa_id, cnpj, razao_social, cnae_codigo,
                    isento, uf, simples
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                empresa_id, cnpj, razao_social, cnae_codigo,
                isento, uf, simples
            )) 
            conn.commit()
            return True, "Fornecedor cadastrado com sucesso."

    except Exception as e:
        print(f"Erro ao inserir fornecedor: {e}")
        return False, f"Erro ao inserir fornecedor: {e}"
    finally:
        if conn:
            conn.close()

def listar_ultimos_fornecedores(limit=4):
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT razao_social, criado_em, cnpj
                FROM fornecedores
                ORDER BY criado_em DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
    finally:
        conn.close()

def contar_fornecedores():
    conn = DBManager.instance().get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM fornecedores")
        return cursor.fetchone()[0]

def contar_fornecedores_mes_atual() -> int:
    conn = DBManager.instance().get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM fornecedores
        WHERE MONTH(data_cadastro) = MONTH(NOW())
          AND YEAR(data_cadastro) = YEAR(NOW())
    """)
    total = cursor.fetchone()[0]
    conn.close()
    return total

def listar_todos_fornecedores() -> list:
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM fornecedores")
            return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar fornecedores: {e}")
        return []
    finally:
        if conn:
            conn.close()
