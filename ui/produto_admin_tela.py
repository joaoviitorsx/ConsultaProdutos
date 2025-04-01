from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QComboBox, QMessageBox, QHeaderView, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from repository.produto_admin_repository import listar_empresas, listar_produtos_por_empresa, inserir_produto, atualizar_produto, remover_produto

class ProdutoAdminTela(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1A1F2C;")
        self.setWindowTitle("Produtos")
        self.setGeometry(200, 100, 900, 600)
        self.empresa_id = None
        self.produtos_carregados = [] 
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        titulo = QLabel("Produtos")
        titulo.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        layout.addWidget(titulo)

        # Frame de filtros (empresa + atualizar)
        filtro_frame = QFrame()
        filtro_frame.setStyleSheet("background-color: #1F2536; border-radius: 8px;")
        filtro_layout = QHBoxLayout(filtro_frame)
        filtro_layout.setContentsMargins(10, 10, 10, 10)

        self.empresa_combo = QComboBox()
        self.empresa_combo.setStyleSheet("background-color: #2C3144; color: white; padding: 6px;")
        self.empresa_combo.atualizar_empresas = self.atualizar_empresas
        self.empresa_combo.currentIndexChanged.connect(self.filtrar_por_empresa)
        filtro_layout.addWidget(self.empresa_combo)

        self.btn_atualizar_empresas = QPushButton("")
        self.btn_atualizar_empresas.setIcon(QIcon("images/recarregar.png"))
        self.btn_atualizar_empresas.setIconSize(QSize(24, 24))
        self.btn_atualizar_empresas.setCursor(Qt.PointingHandCursor)
        self.btn_atualizar_empresas.setFixedSize(36, 36)
        self.btn_atualizar_empresas.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #5c1414;
            }
        """)
        self.btn_atualizar_empresas.clicked.connect(self.carregar_empresas)
        filtro_layout.addWidget(self.btn_atualizar_empresas)

        layout.addWidget(filtro_frame)

        # ⬅️ BARRA DE PESQUISA
        self.input_pesquisa = QLineEdit()
        self.input_pesquisa.setPlaceholderText("Buscar por código, nome ou NCM")
        self.input_pesquisa.setStyleSheet("""
            QLineEdit {
                background-color: #2C3144;
                color: white;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 10pt;
            }
        """)
        self.input_pesquisa.textChanged.connect(self.filtrar_tabela)
        layout.addWidget(self.input_pesquisa)

        # Tabela
        tabela_container = QFrame()
        tabela_container.setStyleSheet("background-color: #1F2536; border: 1px solid #2C3144; border-radius: 8px;")
        tabela_layout = QVBoxLayout(tabela_container)

        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["Código", "Produto", "NCM", "Alíquota"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setStyleSheet("""
            QTableWidget { color: white; background-color: #1F2536; gridline-color: #2C3144; }
            QHeaderView::section { background-color: #353A4F; color: white; font-weight: bold; padding: 6px; border: 1px solid #2C3144; }
        """)
        header = self.tabela.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        tabela_layout.addWidget(self.tabela)
        layout.addWidget(tabela_container)

        self.carregar_empresas()

    def carregar_empresas(self):
        from repository.empresa_repository import listar_empresas
        empresas = listar_empresas()

        self.empresa_combo.clear()
        self.empresas_map = {e['razao_social']: e['id'] for e in empresas}
        self.empresa_combo.addItems(self.empresas_map.keys())

        if self.empresa_combo.count() > 0:
            self.empresa_combo.setCurrentIndex(0)
            self.filtrar_por_empresa()

    def filtrar_por_empresa(self):
        nome = self.empresa_combo.currentText()
        self.empresa_id = self.empresas_map.get(nome)
        self.produtos_carregados = listar_produtos_por_empresa(self.empresa_id)
        self.filtrar_tabela()

    def filtrar_tabela(self):
        termo = self.input_pesquisa.text().lower()
        self.tabela.setRowCount(0)

        for prod in self.produtos_carregados:
            if (
                termo in str(prod["codigo"]).lower() or
                termo in prod["produto"].lower() or
                termo in prod["ncm"].lower()
            ):
                row = self.tabela.rowCount()
                self.tabela.insertRow(row)
                self.tabela.setItem(row, 0, QTableWidgetItem(str(prod['codigo'])))
                self.tabela.setItem(row, 1, QTableWidgetItem(prod['produto']))
                self.tabela.setItem(row, 2, QTableWidgetItem(prod['ncm']))
                self.tabela.setItem(row, 3, QTableWidgetItem(prod['aliquota']))

    def atualizar_empresas(self):
        self.carregar_empresas()

    def showEvent(self, event):
        super().showEvent(event)
        self.carregar_empresas()
