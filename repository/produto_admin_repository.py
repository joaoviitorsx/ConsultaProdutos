from db.db_manager import DBManager
from collections import defaultdict

def listar_empresas():
    conn = DBManager.instance().get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, razao_social AS nome FROM empresas")
            return cursor.fetchall()
    except Exception as e:
        print("Erro ao listar empresas:", e)
        return []
    finally:
        conn.close()

def listar_produtos_por_empresa(empresa_id):
    conn = DBManager.instance().get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT codigo, produto, ncm, aliquota
                FROM tabela_tributacao
                WHERE empresa_id = %s
            """, (empresa_id,))
            return cursor.fetchall()
    except Exception as e:
        print("Erro ao listar produtos:", e)
        return []
    finally:
        conn.close()

def inserir_produto(empresa_id, codigo, produto, ncm, aliquota):
    conn = DBManager.instance().get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tabela_tributacao (empresa_id, codigo, produto, ncm, aliquota)
                VALUES (%s, %s, %s, %s, %s)
            """, (empresa_id, codigo, produto, ncm, aliquota))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao inserir produto:", e)
        return False
    finally:
        conn.close()

def atualizar_produto(empresa_id, codigo, produto, ncm, aliquota):
    conn = DBManager.instance().get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE tabela_tributacao
                SET produto = %s, ncm = %s, aliquota = %s
                WHERE empresa_id = %s AND codigo = %s
            """, (produto, ncm, aliquota, empresa_id, codigo))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao atualizar produto:", e)
        return False
    finally:
        conn.close()

def remover_produto(empresa_id, codigo):
    conn = DBManager.instance().get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM tabela_tributacao
                WHERE empresa_id = %s AND codigo = %s
            """, (empresa_id, codigo))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao remover produto:", e)
        return False
    finally:
        conn.close()

def contar_produtos():
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tabela_tributacao")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
    finally:
        conn.close()

def listar_ultimos_produtos(limit=4):
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT t.codigo, t.produto, e.razao_social AS empresa, t.id
                FROM tabela_tributacao t
                LEFT JOIN empresas e ON e.id = t.empresa_id
                ORDER BY t.id DESC
                LIMIT %s
            """, (limit,))
            return [
                {
                    "codigo": row["codigo"],
                    "produto": row["produto"],
                    "empresa": row["empresa"],
                    "criado_em": row["id"]  # ⚠️ Simulando criado_em para não quebrar o dashboard
                }
                for row in cursor.fetchall()
            ]
    finally:
        conn.close()

def contar_produtos_mes_atual() -> int:
    conn = DBManager.instance().get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM tabela_tributacao
        WHERE MONTH(data_cadastro) = MONTH(NOW())
          AND YEAR(data_cadastro) = YEAR(NOW())
    """)
    total = cursor.fetchone()[0]
    conn.close()
    return total
