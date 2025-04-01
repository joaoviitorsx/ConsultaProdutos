from repository.produto_repository import buscar_produto_por_empresa, buscar_produto_globalmente
from models.produto import Produto
from utils.logger import logger

def buscar_produto_por_codigo_service(codigo: str, empresa_id: int | None) -> Produto | None:
    try:
        if empresa_id is None:
            # Acesso de administrador: busca sem filtro por empresa
            logger.info(f"Consulta de produto como admin: código={codigo}")
            return buscar_produto_globalmente(codigo)
        else:
            logger.info(f"Consulta de produto: código={codigo} | empresa_id={empresa_id}")
            return buscar_produto_por_empresa(codigo, empresa_id)

    except Exception as e:
        logger.error(f"Erro no serviço de produto: {e}")
        return None
