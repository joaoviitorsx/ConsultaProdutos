from db.db_manager import DBManager

def criar_empresa_com_usuario(razao_social: str, usuario: str, senha: str) -> tuple[bool, str]:
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar se a razão social já existe
            cursor.execute("SELECT id FROM empresas WHERE razao_social = %s", (razao_social,))
            if cursor.fetchone():
                return False, "Já existe uma empresa com essa razão social."

            # Verificar se o usuário já existe
            cursor.execute("SELECT id FROM users WHERE nome = %s", (usuario,))
            if cursor.fetchone():
                return False, "Esse nome de usuário já está em uso."

            # Inserir a empresa
            cursor.execute("INSERT INTO empresas (razao_social) VALUES (%s)", (razao_social,))
            conn.commit()

            # Obter o ID da empresa inserida
            cursor.execute("SELECT LAST_INSERT_ID()")
            empresa_id = cursor.fetchone()[0]

            # Inserir o usuário vinculado à empresa
            cursor.execute("""
                INSERT INTO users (nome, senha, empresa_id)
                VALUES (%s, %s, %s)
            """, (usuario, senha, empresa_id))
            conn.commit()

        return True, "Empresa criada com sucesso"
    except Exception as e:
        return False, f"Erro ao criar empresa e usuário: {e}"
    finally:
        conn.close()
    
def remover_empresa(empresa_id: int) -> bool:
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE empresa_id = %s", (empresa_id,))
            cursor.execute("DELETE FROM empresas WHERE id = %s", (empresa_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao remover empresa: {e}")
        return False
    finally:
        conn.close()
  
def listar_empresas() -> list[dict]:
    conn = DBManager.instance().get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, razao_social FROM empresas ORDER BY razao_social")
            return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar empresas: {e}")
        return []
    finally:
        conn.close()

   