from models.fornecedor import Fornecedor
from models.produto import Produto
from services.fornecedor_service import consultar_dados_fornecedor
from repository.produto_repository import buscar_produto_por_empresa

def calcular_impostos_detalhados(cnpj: str, codigo: str, valor: float, empresa_id: int) -> dict:
    fornecedor = consultar_dados_fornecedor(cnpj, empresa_id)
    if not fornecedor:
        raise ValueError("Fornecedor não encontrado.")

    produto = buscar_produto_por_empresa(codigo, empresa_id)
    if not produto:
        raise ValueError("Produto não encontrado.")

    icms_valor = "Não paga"
    simples_valor = "Não paga"
    aliquota_float = 0.00
    aliquota_str = "0.00"

    # Se a empresa estiver no decreto/isenta, não calcula nada
    if fornecedor.isento:
        total = valor
    else:
        # Tratamento da alíquota
        raw_aliquota = str(produto.aliquota).strip().upper()

        if raw_aliquota in ["ST", "ISENTO"]:
            total = valor  # Produto não paga imposto
        else:
            try:
                aliquota_str = raw_aliquota.replace("%", "").replace(",", ".")
                aliquota_float = float(aliquota_str)
            except ValueError:
                aliquota_float = 0.00

            # Cálculo do ICMS
            if aliquota_float > 0:
                icms_valor = valor * (aliquota_float / 100)

            # Adicional do Simples se for Simples Nacional
            if fornecedor.simples:
                simples_valor = valor * 0.03

            total = valor
            if isinstance(icms_valor, float):
                total += icms_valor
            if isinstance(simples_valor, float):
                total += simples_valor

    impostos = {
        "ICMS": f"R$ {icms_valor:.2f}" if isinstance(icms_valor, float) else "Não paga",
        "Adicional Simples": f"R$ {simples_valor:.2f}" if isinstance(simples_valor, float) else "Sem Adicional"
    }

    return {
        "cnpj": fornecedor.cnpj,
        "razao_social": fornecedor.razao_social,
        "nome_produto": produto.nome,
        "aliquota": aliquota_float,
        "ncm": produto.ncm,
        "regime": "Simples Nacional" if fornecedor.simples else "Lucro Presumido",
        "isento": fornecedor.isento,
        "valor_base": valor,
        "valor_total": total,
        "impostos": impostos
    }
