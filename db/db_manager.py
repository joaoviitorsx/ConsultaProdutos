# db/db_manager.py
import mysql.connector.pooling

class DBManager:
    _instance = None

    def __init__(self):
        self.pool = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._criar_pool()
        return cls._instance

    def _criar_pool(self):
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=10,
                pool_reset_session=True,
                host="127.0.0.1",  
                port=3306,
                database="consulta_produtos",
                user="root",
                password="1234",
                autocommit=True,
                connection_timeout=3
            )
        except mysql.connector.Error as e:
            print(f"Erro ao criar pool de conexões: {e}")
            self.pool = None

    def get_connection(self):
        if self.pool is None:
            raise Exception("Pool de conexões não inicializado.")
        conn = self.pool.get_connection()
        conn.ping(reconnect=True, attempts=1, delay=0)
        return conn
