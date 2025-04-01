from db.db_manager import DBManager
from models.produto import Produto

def parse_aliquota(valor):
    if valor is None:
        return 0.0
    try:
        valor_limpo = str(valor).replace('%', '').replace(',', '.').strip()
        return float(valor_limpo)
    except Exception as e:
        print(f"Erro ao converter alíquota: {valor} -> {e}")
        return 0.0

def buscar_produto_por_empresa(codigo: str, empresa_id: int) -> Produto | None:
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return None

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT codigo, produto, ncm, aliquota
                FROM tabela_tributacao
                WHERE empresa_id = %s AND codigo = %s
                LIMIT 1
            """, (empresa_id, codigo))
            resultado = cursor.fetchone()

            if resultado:
                return Produto(
                    codigo=resultado['codigo'],
                    nome=resultado['produto'],
                    ncm=resultado['ncm'],
                    aliquota=parse_aliquota(resultado['aliquota'])
                )
            return None

    except Exception as e:
        print(f"Erro no repository (produto por empresa): {e}")
        return None
    finally:
        conn.close()

def buscar_produto_globalmente(codigo: str) -> Produto | None:
    try:
        conn = DBManager.instance().get_connection()
        if not conn:
            return None

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT codigo, produto, ncm, aliquota
                FROM tabela_tributacao
                WHERE codigo = %s
                LIMIT 1
            """, (codigo,))
            resultado = cursor.fetchone()

            if resultado:
                return Produto(
                    codigo=resultado['codigo'],
                    nome=resultado['produto'],
                    ncm=resultado['ncm'],
                    aliquota=parse_aliquota(resultado['aliquota'])
                )
            return None

    except Exception as e:
        print(f"Erro no repository (produto global): {e}")
        return None
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