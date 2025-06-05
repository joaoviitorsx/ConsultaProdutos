class Produto:
    def __init__(self, codigo, nome, aliquota, ncm, valor_base=0.0, valor_total=0.0):
        self.codigo = codigo
        self.nome = nome
        self.ncm = ncm
        self.aliquota = aliquota
        self.valor_base = valor_base
        self.valor_total = valor_total

    def __repr__(self):
        return f"<Produto {self.nome} ({self.codigo})>"
