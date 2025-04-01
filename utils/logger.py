import logging
from logging.handlers import RotatingFileHandler
import os

# Garantir que a pasta de logs existe
os.makedirs("logs", exist_ok=True)

# Caminho do arquivo de log
log_path = os.path.join("logs", "acoes.log")

# Configuração do logger
logger = logging.getLogger("acoes_logger")
logger.setLevel(logging.INFO)

# Evita adicionar múltiplos handlers em recarregamentos
if not logger.handlers:
    handler = RotatingFileHandler(log_path, maxBytes=500000, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
