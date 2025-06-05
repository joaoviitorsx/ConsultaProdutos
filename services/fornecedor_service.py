from repository.fornecedor_repository import buscar_fornecedor_por_cnpj, buscar_fornecedor_global, inserir_fornecedor
from models.fornecedor import Fornecedor
from utils.validacao import validar_cnpj, limpar_cnpj
from utils.logger import logger
from utils.cnpj import buscar_informacoes
import asyncio

def consultar_dados_fornecedor(cnpj: str, empresa_id: int | None) -> Fornecedor | None:
    if not validar_cnpj(cnpj):
        raise ValueError("CNPJ inválido")

    cnpj_limpo = limpar_cnpj(cnpj)
    logger.info(f"Consulta de fornecedor: CNPJ={cnpj_limpo} | empresa_id={empresa_id}")

    try:
        # 1. Busca local no banco
        if empresa_id is None:
            resultado_db = buscar_fornecedor_global(cnpj_limpo)
        else:
            resultado_db = buscar_fornecedor_por_cnpj(empresa_id, cnpj_limpo)

        if resultado_db:
            logger.info("🔁 Fornecedor encontrado no banco, não será feita chamada à API.")
            return Fornecedor(
                cnpj=resultado_db["cnpj"],
                razao_social=resultado_db["razao_social"],
                cnae_codigo=resultado_db["cnae_codigo"],
                isento=bool(int(resultado_db["isento"])),
                uf=resultado_db["uf"],
                simples=bool(int(resultado_db["simples"]))
            )

        # 2. Se não encontrou, chama a API
        logger.info("🌐 Fornecedor não encontrado. Chamando API...")
        resultado_api = asyncio.run(buscar_informacoes(cnpj_limpo))
        logger.info(f"📦 Dados recebidos da API: {resultado_api}")

        if not resultado_api or resultado_api[0] is None:
            logger.warning("⚠️ API retornou dados incompletos ou inválidos.")
            return None

        razao_social, cnae_codigo, isento, uf, simples = resultado_api

        # 3. Inserir no banco (se empresa informada)
        if empresa_id is not None:
            sucesso = inserir_fornecedor(
                empresa_id=empresa_id,
                cnpj=cnpj_limpo,
                razao_social=razao_social,
                cnae_codigo=cnae_codigo,
                isento=isento,
                uf=uf,
                simples=simples
            )
            if not sucesso:
                logger.warning("⚠️ Não foi possível salvar fornecedor no banco.")

        # 4. Retornar objeto
        return Fornecedor(
            cnpj=cnpj_limpo,
            razao_social=razao_social,
            cnae_codigo=cnae_codigo,
            isento=bool(int(isento)),
            uf=uf,
            simples=bool(int(simples))
        )

    except Exception as e:
        logger.error(f"❌ Erro inesperado em fornecedor_service: {e}")
        return None
