class Fornecedor:
    def __init__(self, cnpj, razao_social, cnae_codigo, isento, uf, simples, empresa_id=None):
        self.empresa_id = empresa_id
        self.cnpj = cnpj
        self.razao_social = razao_social
        self.cnae_codigo = cnae_codigo
        self.isento = isento
        self.uf = uf
        self.simples = simples

    def __repr__(self):
        return f"<Fornecedor {self.razao_social} ({self.cnpj})>"
