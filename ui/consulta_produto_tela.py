from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QScrollArea, QGridLayout
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt
from utils.mensagem import mensagem_error
import asyncio

from utils.cnpj import remover_caracteres_nao_numericos

# Importação adiada para evitar erro de import circular
buscar_informacoes = None

class ConsultaProdutoTela(QWidget):
    def __init__(self, user: str, empresa_id: int):
        super().__init__()
        global buscar_informacoes
        if buscar_informacoes is None:
            from utils.cnpj import buscar_informacoes

        self.setWindowTitle("Consulta de Produtos")
        self.setGeometry(300, 100, 1200, 800)
        self.setStyleSheet("background-color: #f8fafc;")
        self.user = user
        self.empresa_id = empresa_id
        self.max_fornecedores = 4
        self.contador = 0
        self.cards = []
        self.resultados = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Lado esquerdo (Entrada)
        self.container_esquerda = QVBoxLayout()

        titulo = QLabel("Consultar Produtos")
        titulo.setFont(QFont("Arial", 22, QFont.Bold))
        titulo.setStyleSheet("color: #111827;")
        self.container_esquerda.addWidget(titulo)

        subtitulo = QLabel("Fornecedores")
        subtitulo.setFont(QFont("Arial", 14, QFont.Bold))
        self.container_esquerda.addWidget(subtitulo)

        self.area_cards = QVBoxLayout()
        self.container_esquerda.addLayout(self.area_cards)

        self.btn_adicionar = QPushButton("+ Adicionar fornecedor para comparação")
        self.btn_adicionar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px dashed #ccc;
                color: #111827;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.btn_adicionar.clicked.connect(self.adicionar_card)
        self.container_esquerda.addWidget(self.btn_adicionar)

        demonstracao = QLabel("Para fins de demonstração, use o CNPJ: 12.345.678/0001-90")
        demonstracao.setStyleSheet("color: #6b7280; font-size: 12px;")
        self.container_esquerda.addWidget(demonstracao)

        # Lado direito (Resultados)
        self.container_direita = QVBoxLayout()

        resultado_titulo = QLabel("Resultado da Análise")
        resultado_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        self.container_direita.addWidget(resultado_titulo)

        self.resultado_frame = QFrame()
        self.resultado_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #cbd5e1;
                background-color: white;
                padding: 30px;
            }
        """)
        self.resultado_layout = QVBoxLayout(self.resultado_frame)

        self.msg_placeholder = QLabel("Nenhum produto processado")
        self.msg_placeholder.setFont(QFont("Arial", 12, QFont.Bold))
        self.msg_placeholder.setAlignment(Qt.AlignCenter)
        self.resultado_layout.addWidget(self.msg_placeholder)

        self.container_direita.addWidget(self.resultado_frame)

        layout.addLayout(self.container_esquerda, 40)
        layout.addSpacing(30)
        layout.addLayout(self.container_direita, 60)

        self.adicionar_card()  # Adiciona o primeiro card automaticamente

    def adicionar_card(self):
        if self.contador >= self.max_fornecedores:
            mensagem_error("Limite de 4 fornecedores atingido.")
            return

        index = self.contador + 1
        card = self.criar_card_fornecedor(index)
        self.area_cards.addWidget(card)
        self.cards.append(card)
        self.contador += 1

    def criar_card_fornecedor(self, numero):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        card.setMinimumWidth(400)
        layout = QVBoxLayout(card)

        titulo = QLabel(f"Fornecedor {numero}")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(titulo)

        input_cnpj = QLineEdit()
        input_cnpj.setPlaceholderText("CNPJ do Fornecedor")
        layout.addWidget(input_cnpj)

        input_valor = QLineEdit()
        input_valor.setPlaceholderText("Valor do Produto (ex: 123.45)")
        layout.addWidget(input_valor)

        btn_processar = QPushButton("🔍 Processar")
        btn_processar.setCursor(QCursor(Qt.PointingHandCursor))
        btn_processar.setStyleSheet("""
            QPushButton {
                background-color: #0f766e;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #115e59;
            }
        """)
        btn_processar.clicked.connect(lambda: asyncio.create_task(
            self.processar_fornecedor(input_cnpj.text(), input_valor.text(), numero)
        ))
        layout.addWidget(btn_processar)

        return card

    async def processar_fornecedor(self, cnpj: str, valor_str: str, index: int):
        try:
            valor_base = float(valor_str.replace(',', '.'))
        except ValueError:
            mensagem_error("Valor inválido para o produto.")
            return

        global buscar_informacoes
        if buscar_informacoes is None:
            from utils.cnpj import buscar_informacoes

        razao_social, cnae, isento, uf, simples = await buscar_informacoes(cnpj)
        if not razao_social:
            mensagem_error("Não foi possível obter dados do CNPJ informado.")
            return

        aliquota = 4.0
        adicional = 3.0 if simples else 0.0
        total_imposto = (aliquota + adicional) / 100 * valor_base
        valor_total = valor_base + total_imposto

        resultado = {
            "cnpj": cnpj,
            "regime": "Simples Nacional" if simples else "Lucro Presumido",
            "isento": isento,
            "valor_base": valor_base,
            "impostos": total_imposto,
            "valor_total": valor_total,
            "index": index
        }

        self.resultados = [r for r in self.resultados if r['index'] != index]
        self.resultados.append(resultado)
        self.atualizar_resultado()

    def atualizar_resultado(self):
        for i in reversed(range(self.resultado_layout.count())):
            widget = self.resultado_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.resultados:
            self.resultado_layout.addWidget(QLabel("Nenhum produto processado"))
            return

        menor = min(self.resultados, key=lambda x: x['valor_total'])

        tabela = QVBoxLayout()
        header = QLabel("<b>Fornecedor | Regime | Valor Base | Impostos | Valor Total</b>")
        tabela.addWidget(header)

        for r in self.resultados:
            impostos_texto = f"R$ {r['impostos']:.2f}"
            if not r['isento']:
                impostos_texto += " (Não Isento)"

            info = QLabel(f"{r['cnpj']} | {r['regime']} | R$ {r['valor_base']:.2f} | {impostos_texto} | <b>R$ {r['valor_total']:.2f}</b>")
            if r == menor:
                info.setStyleSheet("background-color: #dcfce7; padding: 6px; border-radius: 6px;")
            tabela.addWidget(info)

        comparativo = QLabel(f"<b>Análise Comparativa:</b><br>O fornecedor com CNPJ <b>{menor['cnpj']}</b> apresenta o menor custo total de <b>R$ {menor['valor_total']:.2f}</b>.")
        comparativo.setStyleSheet("background-color: #dcfce7; padding: 10px; border-radius: 8px;")

        self.resultado_layout.addLayout(tabela)
        self.resultado_layout.addSpacing(15)
        self.resultado_layout.addWidget(comparativo)
