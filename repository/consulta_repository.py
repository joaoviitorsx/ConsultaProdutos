from db.db_manager import DBManager
from models.fornecedor import Fornecedor
from models.produto import Produto
from datetime import datetime

def registrar_consulta(empresa_id, user, fornecedor: Fornecedor, produto: Produto):
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            print("[ERRO] Conexão com o banco de dados falhou.")
            return

        aliquota_adicional = 3.00 if fornecedor.simples else 0.00

        # Conversão segura da alíquota
        try:
            if isinstance(produto.aliquota, str):
                aliquota_str = produto.aliquota.strip().replace("%", "").replace(",", ".")
                aliquota_float = float(aliquota_str)
            else:
                aliquota_float = float(produto.aliquota)
        except Exception as err:
            print(f"[WARN] Erro ao converter alíquota '{produto.aliquota}': {err}")
            aliquota_float = 0.00

        aliquota_total = aliquota_float + aliquota_adicional

        # Garantir que os campos valor_base e valor_total existam
        valor_base = getattr(produto, 'valor_base', 0.00)
        valor_total = getattr(produto, 'valor_total', 0.00)

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO consultas (
                    empresa_id, user, cnpj_fornecedor, nome_fornecedor,
                    cod_produto, nome_produto,
                    aliquota, aliquota_adicional, aliquota_total,
                    valor_base, valor_total,
                    data_consulta
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                empresa_id,
                user,
                fornecedor.cnpj,
                fornecedor.razao_social,
                produto.codigo,
                produto.nome,
                aliquota_float,
                aliquota_adicional,
                aliquota_total,
                valor_base,
                valor_total,
                datetime.now()
            ))

            conn.commit()
            print(f"[INFO] Consulta registrada com sucesso para produto {produto.codigo}")

    except Exception as e:
        print(f"[ERRO][registrar_consulta] Erro ao registrar consulta para produto {produto.codigo}: {e}")
    finally:
        if conn:
            conn.close()

def buscar_consultas_por_data(empresa_id: int, mes: int, ano: int):
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            print("[ERRO] Conexão com o banco de dados falhou.")
            return []

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT * FROM consultas
                WHERE empresa_id = %s
                AND MONTH(data_consulta) = %s
                AND YEAR(data_consulta) = %s
                ORDER BY data_consulta DESC
            """, (empresa_id, mes, ano))

            resultados = cursor.fetchall()
            print(f"[INFO] {len(resultados)} consultas encontradas para {mes:02}/{ano}")
            return resultados

    except Exception as e:
        print(f"[ERRO] Erro ao buscar consultas por data: {e}")
        return []
    finally:
        if conn:
            conn.close()
