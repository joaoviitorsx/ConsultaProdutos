from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from models.fornecedor import Fornecedor

class FornecedorInfoTela(QWidget):
    def __init__(self, user: str, empresa_id: int, fornecedor: Fornecedor):
        super().__init__()
        self.user = user
        self.empresa_id = empresa_id
        self.fornecedor = fornecedor
        self.setWindowTitle("Informações do Fornecedor")
        self.setGeometry(300, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Dados do Fornecedor")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        layout.addWidget(titulo)

        layout.addWidget(QLabel(f"Razão Social: {self.fornecedor.razao_social}"))
        layout.addWidget(QLabel(f"CNPJ: {self.fornecedor.cnpj}"))
        layout.addWidget(QLabel(f"CNAE: {self.fornecedor.cnae_codigo}"))
        layout.addWidget(QLabel(f"UF: {self.fornecedor.uf}"))
        layout.addWidget(QLabel(f"Decreto: {'Sim' if self.fornecedor.isento else 'Não'}"))
        layout.addWidget(QLabel(f"Simples Nacional: {'Sim' if self.fornecedor.simples else 'Não'}"))

        voltar = QPushButton("🔙 Voltar ao Dashboard")
        voltar.clicked.connect(self.voltar_dashboard)
        layout.addWidget(voltar)

        self.setStyleSheet("QLabel { color: white; font-size: 14px; }")

    def voltar_dashboard(self):
        from ui.dashboardinicial import DashboardInicial
        self.dashboard = DashboardInicial(self.user, self.empresa_id)
        self.dashboard.showMaximized()
        self.close()
