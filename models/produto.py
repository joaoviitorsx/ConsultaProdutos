class Produto:
    def __init__(self, codigo, nome, ncm, aliquota):
        self.codigo = codigo
        self.nome = nome
        self.ncm = ncm
        self.aliquota = aliquota

    def __repr__(self):
        return f"<Produto {self.nome} ({self.codigo})>"
