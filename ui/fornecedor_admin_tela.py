from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QFrame
from PySide6.QtCore import Qt
from repository.fornecedor_repository import listar_todos_fornecedores

class FornecedorAdminTela(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1A1F2C;")
        self.setWindowTitle("Fornecedores")
        self.setGeometry(200, 100, 900, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        titulo = QLabel("Fornecedores")
        titulo.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        layout.addWidget(titulo)

        busca_frame = QFrame()
        busca_frame.setStyleSheet("background-color: #1F2536; border-radius: 8px;")
        busca_layout = QHBoxLayout(busca_frame)
        busca_layout.setContentsMargins(10, 10, 10, 10)

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar fornecedores...")
        self.input_busca.setStyleSheet("background-color: #2C3144; color: white; padding: 6px; border-radius: 6px;")
        self.input_busca.textChanged.connect(self.aplicar_filtro)
        busca_layout.addWidget(self.input_busca)
        layout.addWidget(busca_frame)

        tabela_container = QFrame()
        tabela_container.setStyleSheet("background-color: #1F2536; border: 1px solid #2C3144; border-radius: 8px;")
        tabela_layout = QVBoxLayout(tabela_container)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["CNPJ", "Razão Social", "CNAE", "UF", "Simples", "Isento"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setStyleSheet("QTableWidget { color: white; background-color: #1F2536; gridline-color: #2C3144; } QHeaderView::section { background-color: #353A4F; color: white; font-weight: bold; padding: 6px; border: 1px solid #2C3144; }")

        header = self.tabela.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        tabela_layout.addWidget(self.tabela)
        layout.addWidget(tabela_container)

        self.carregar_todos()

    def carregar_todos(self):
        fornecedores = listar_todos_fornecedores()
        self.popular_tabela(fornecedores)

    def aplicar_filtro(self):
        termo = self.input_busca.text().strip().lower()
        todos = listar_todos_fornecedores()
        filtrados = [f for f in todos if termo in f['cnpj'] or termo in f['razao_social'].lower()]
        self.popular_tabela(filtrados)

    def popular_tabela(self, fornecedores):
        self.tabela.setRowCount(0)
        for f in fornecedores:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(f["cnpj"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(f["razao_social"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(f["cnae_codigo"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(f["uf"]))
            self.tabela.setItem(row, 4, QTableWidgetItem("Sim" if f["simples"] else "Não"))
            self.tabela.setItem(row, 5, QTableWidgetItem("Sim" if f["isento"] else "Não"))