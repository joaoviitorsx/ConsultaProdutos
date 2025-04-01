from db.db_manager import DBManager
from collections import defaultdict
from datetime import datetime

def obter_atividades_por_dia(tabela, coluna_data="criado_em", dias=7):
    conn = DBManager.instance().get_connection()
    dados = defaultdict(int)

    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT DATE({coluna_data}) as data
            FROM {tabela}
            WHERE {coluna_data} >= CURDATE() - INTERVAL {dias} DAY
        """)
        for row in cursor.fetchall():
            if row[0]:
                data_str = row[0].strftime("%d/%m")
                dados[data_str] += 1
    return dados
