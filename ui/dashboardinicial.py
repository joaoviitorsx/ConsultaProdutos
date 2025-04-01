from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,QFrame, QSizePolicy, QSpacerItem
from PySide6.QtGui import QFont, QPixmap, QCursor
from PySide6.QtCore import Qt, Signal


class DashboardInicial(QWidget):
    def __init__(self, user: str, empresa_id: int):
        super().__init__()
        self.setWindowTitle("Dashboard Inicial")
        self.setStyleSheet("background-color: #f8fafc;")
        self.setGeometry(400, 100, 800, 800)
        self.user = user
        self.empresa_id = empresa_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        logo = QLabel("CONSULTOR DE PRODUTOS")
        logo.setFont(QFont("Arial", 20, QFont.Bold))
        logo.setStyleSheet("color: #111827;")

        user_info = QLabel(f"Olá, <b>{self.user}</b>")
        user_info.setStyleSheet("color: #374151; font-size: 14px;")

        btn_logout = QPushButton("Sair")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_logout.setCursor(QCursor(Qt.PointingHandCursor))
        btn_logout.clicked.connect(self.logout)

        header_right = QHBoxLayout()
        header_right.setSpacing(15)
        header_right.addWidget(user_info)
        header_right.addWidget(btn_logout)

        header_layout.addWidget(logo)
        header_layout.addStretch()
        header_layout.addLayout(header_right)
        layout.addLayout(header_layout)

        # Título
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color: #111827;")
        layout.addWidget(title)

        subtitle = QLabel("Escolha uma das opções abaixo para começar")
        subtitle.setStyleSheet("color: #6b7280; font-size: 14px;")
        layout.addWidget(subtitle)

        # Cartões
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        # Fornecedor
        card_fornecedor = self.criar_card(
            "🔍", "Consultar Fornecedor",
            "Busque informações detalhadas sobre fornecedores através do CNPJ",
            self.abrir_consulta_fornecedor
        )

        # Produto
        card_produto = self.criar_card(
            "🧮", "Consultar Produtos",
            "Compare preços e impostos entre diferentes fornecedores",
            self.abrir_tela_consultar_produtos
        )

        cards_layout.addWidget(card_fornecedor)
        cards_layout.addWidget(card_produto)

        layout.addSpacing(10)
        layout.addLayout(cards_layout)
        layout.addStretch()

        self.setLayout(layout)

    def criar_card(self, emoji, titulo, descricao, callback):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        card.setFixedSize(400, 200)
        card.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        icone = QLabel(emoji)
        icone.setFont(QFont("Arial", 26))
        icone.setAlignment(Qt.AlignCenter)

        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Arial", 14, QFont.Bold))
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setStyleSheet("color: #111827;")

        descricao_label = QLabel(descricao)
        descricao_label.setWordWrap(True)
        descricao_label.setAlignment(Qt.AlignCenter)
        descricao_label.setStyleSheet("color: #6b7280; font-size: 12px;")

        botao = QPushButton("Acessar")
        botao.setCursor(QCursor(Qt.PointingHandCursor))
        botao.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        botao.clicked.connect(callback)

        layout.addWidget(icone)
        layout.addSpacing(5)
        layout.addWidget(titulo_label)
        layout.addWidget(descricao_label)
        layout.addSpacing(10)
        layout.addWidget(botao)

        return card

    def abrir_consulta_fornecedor(self):
        from ui.fornecedor_tela import FornecedorTela
        self.nova_janela = FornecedorTela(self.user, self.empresa_id)
        self.nova_janela.showMaximized()
        self.close()

    def abrir_tela_consultar_produtos(self):
        from ui.consulta_produto_tela import ConsultaProdutoTela
        self.produto_tela = ConsultaProdutoTela(self.user, self.empresa_id)
        self.produto_tela.showMaximized()
        self.close()

    def logout(self):
        from ui.login_tela import LoginTela
        self.login_tela = LoginTela()
        self.login_tela.showMaximized()
        self.close()
