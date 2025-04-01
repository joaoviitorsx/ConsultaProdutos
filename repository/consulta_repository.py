from db.db_manager import DBManager
from models.fornecedor import Fornecedor
from models.produto import Produto
from datetime import datetime

def registrar_consulta(empresa_id, user, fornecedor: Fornecedor, produto: Produto):
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return

        aliquota_adicional = 3.00 if fornecedor.simples else 0.00
        aliquota_total = produto.aliquota + aliquota_adicional

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO consultas (
                    empresa_id, user, cnpj_fornecedor, nome_fornecedor,
                    cod_produto, nome_produto,
                    aliquota, aliquota_adicional, aliquota_total,
                    data_consulta
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                empresa_id,
                user,
                fornecedor.cnpj,
                fornecedor.razao_social,
                produto.codigo,
                produto.nome,
                produto.aliquota,
                aliquota_adicional,
                aliquota_total,
                datetime.now()
            ))

            conn.commit()

    except Exception as e:
        print(f"Erro ao registrar consulta: {e}")
    finally:
        if conn:
            conn.close()

def buscar_consultas_por_data(empresa_id: int, mes: int, ano: int):
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return []

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM consultas
                WHERE empresa_id = %s
                AND MONTH(data_consulta) = %s
                AND YEAR(data_consulta) = %s
                ORDER BY data_consulta DESC
            """, (empresa_id, mes, ano))

            return cursor.fetchall()

    except Exception as e:
        print(f"Erro ao buscar consultas por data: {e}")
        return []
    finally:
        if conn:
            conn.close()
