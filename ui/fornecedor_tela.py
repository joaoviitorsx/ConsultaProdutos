from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QFrame
from PySide6.QtCore import Qt, QThread, Signal
from ui.produto_tela import ProdutoTela
from services.fornecedor_service import consultar_dados_fornecedor
from utils.validacao import limpar_cnpj
from utils.mensagem import mensagem_error, mensagem_aviso
from models.fornecedor import Fornecedor
from ui.fornecedorinfo_tela import FornecedorInfoTela

class ConsultaThread(QThread):
    resultado = Signal(object)

    def __init__(self, cnpj, empresa_id):
        super().__init__()
        self.cnpj = cnpj
        self.empresa_id = empresa_id

    def run(self):
        try:
            print(f"🚀 Criando thread para consultar CNPJ: {self.cnpj}")
            fornecedor = consultar_dados_fornecedor(self.cnpj, self.empresa_id)
            self.resultado.emit(fornecedor)
        except Exception as e:
            print(f"❌ Erro na thread de consulta: {e}")
            self.resultado.emit(None)


class FornecedorTela(QWidget):
    def __init__(self, user: str, empresa_id: int | None):
        super().__init__()
        self.setWindowTitle("Consulta de Fornecedor - Fornecedor")
        self.setGeometry(400, 100, 800, 800)
        self.setStyleSheet("background-color: #181818;")
        self.user = user
        self.empresa_id = empresa_id
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Card centralizado
        card = QFrame()
        card.setObjectName("cardContainer")
        card.setFixedWidth(450)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)

        # Título
        label_titulo = QLabel("Consultar Fornecedor")
        label_titulo.setObjectName("titulo")
        label_titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label_titulo)

        # Descrição
        label_desc = QLabel("Informe o CNPJ do fornecedor para prosseguir")
        label_desc.setObjectName("descricao")
        label_desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label_desc)

        card_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Campo CNPJ
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("00.000.000/0000-00")
        self.input_cnpj.setInputMask("00.000.000/0000-00")
        self.input_cnpj.setObjectName("campoInput")
        self.input_cnpj.setAlignment(Qt.AlignCenter)
        self.input_cnpj.returnPressed.connect(self.iniciar_consulta)
        card_layout.addWidget(self.input_cnpj)

        card_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botão de consulta
        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.setObjectName("botaoPrincipal")
        self.btn_consultar.setStyleSheet("""
            QPushButton#botaoPrincipal {
                background-color: #E53935;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton#botaoPrincipal:hover {
                background-color: #C62828;
            }
            QPushButton#botaoPrincipal:disabled {
                background-color: #444444;
                color: #CCCCCC;
                border: 1px solid #333333;
            }
            """)
        self.btn_consultar.setCursor(Qt.PointingHandCursor)
        self.btn_consultar.clicked.connect(self.iniciar_consulta)
        card_layout.addWidget(self.btn_consultar)

        layout.addWidget(card)

    def iniciar_consulta(self):
        cnpj = limpar_cnpj(self.input_cnpj.text())
        if len(cnpj) != 14:
            mensagem_aviso("CNPJ inválido.")
            return

        self.btn_consultar.setEnabled(False)
        self.btn_consultar.setText("Consultando...")

        self.thread = ConsultaThread(cnpj, self.empresa_id)
        self.thread.resultado.connect(self.finalizar_consulta)
        self.thread.start()

    def finalizar_consulta(self, fornecedor: Fornecedor | None):
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("Consultar Fornecedor")

        if fornecedor is None:
            mensagem_error("Fornecedor não encontrado ou erro na consulta.")
            return

        self.info_tela = FornecedorInfoTela(self.user, self.empresa_id, fornecedor)
        self.info_tela.showMaximized()
        self.close()
