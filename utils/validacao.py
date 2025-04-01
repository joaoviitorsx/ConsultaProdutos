def validar_cnpj(cnpj: str) -> bool:
    """
    Verifica se o CNPJ está limpo e com 14 dígitos.
    """
    cnpj = ''.join(filter(str.isdigit, cnpj))
    return len(cnpj) == 14 and cnpj.isdigit()

def validar_codigo(codigo: str) -> bool:
    """
    Verifica se o código do produto é numérico e não está vazio.
    """
    return codigo.isdigit()

def limpar_cnpj(cnpj: str) -> str:
    return ''.join(filter(str.isdigit, cnpj))
