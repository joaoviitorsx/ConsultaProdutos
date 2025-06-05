from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFrame, QHBoxLayout, QSizePolicy, QSpacerItem, QGridLayout, QScrollArea
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from models.fornecedor import Fornecedor

class StatusBadge(QLabel):
    def __init__(self, text, is_positive=True):
        super().__init__(text)
        color = "#4CAF50" if is_positive else "#E53935"
        self.setStyleSheet(f"""
            background-color: {color}20;
            color: {color};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: bold;
        """)
        self.setMaximumHeight(25)

class FornecedorInfoTela(QWidget):
    def __init__(self, user: str, empresa_id: int, fornecedor: Fornecedor):
        super().__init__()
        self.user = user
        self.empresa_id = empresa_id
        self.fornecedor = fornecedor
        self.setWindowTitle("Informações do Fornecedor")
        self.setGeometry(300, 100, 1000, 700)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QWidget { background-color: #181818; color: #e0e0e0; }
            QScrollArea { border: none; background-color: transparent; }
        """)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        header_layout = QHBoxLayout()
        titulo = QLabel("Informações do Fornecedor")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header_layout.addWidget(titulo, alignment=Qt.AlignCenter)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background-color: transparent;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(25)

        main_card = QFrame()
        main_card.setStyleSheet("""
            QFrame {
                background-color: #212121;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        main_card_layout = QVBoxLayout(main_card)
        main_card_layout.setSpacing(20)

        card_header = QHBoxLayout()
        company_info = QVBoxLayout()
        razao_social = QLabel(self.fornecedor.razao_social)
        razao_social.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        company_info.addWidget(razao_social)
        cnpj_label = QLabel(f"CNPJ: {self.fornecedor.cnpj}")
        cnpj_label.setStyleSheet("font-size: 14px; color: #9e9e9e;")
        company_info.addWidget(cnpj_label)
        card_header.addLayout(company_info)
        card_header.addStretch()

        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)
        status_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        decreto_badge = StatusBadge("ISENTO DE IMPOSTO" if self.fornecedor.isento else "SUJEITO A IMPOSTO", is_positive=self.fornecedor.isento)
        simples_badge = StatusBadge("SIMPLES NACIONAL" if self.fornecedor.simples else "NÃO OPTANTE PELO SIMPLES", is_positive=self.fornecedor.simples)
        status_layout.addWidget(decreto_badge)
        status_layout.addWidget(simples_badge)
        card_header.addLayout(status_layout)
        main_card_layout.addLayout(card_header)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #333333;")
        main_card_layout.addWidget(separator)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(self.create_info_card("CNAE", self.fornecedor.cnae_codigo), 0, 0)
        grid.addWidget(self.create_info_card("UF", self.fornecedor.uf), 0, 1)
        grid.addWidget(self.create_info_card("Decreto", "Sim" if self.fornecedor.isento else "Não"), 0, 2)
        grid.addWidget(self.create_info_card("Simples Nacional", "Sim" if self.fornecedor.simples else "Não"), 1, 0)
        grid.addWidget(self.create_info_card("Alíquota Adicional", "Aplicável" if self.fornecedor.simples else "Não Aplicável"), 1, 1)
        main_card_layout.addLayout(grid)

        tax_section = QFrame()
        tax_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        tax_layout = QVBoxLayout(tax_section)
        tax_title = QLabel("Situação Tributária")
        tax_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        tax_info = QLabel(f"• Decreto: {'ISENTO DE IMPOSTO' if self.fornecedor.isento else 'SUJEITO A IMPOSTO'}\n• Simples Nacional: {'PAGA ALÍQUOTA ADICIONAL' if self.fornecedor.simples else 'NÃO PAGA ALÍQUOTA ADICIONAL'}")
        tax_info.setStyleSheet("color: #e0e0e0; line-height: 1.6;")
        tax_layout.addWidget(tax_title)
        tax_layout.addWidget(tax_info)
        main_card_layout.addWidget(tax_section)

        scroll_layout.addWidget(main_card)

        fonte_label = QLabel("Dados obtidos via API pública do site Minha Receita")
        fonte_label.setStyleSheet("font-size: 11px; color: #888888;")
        fonte_label.setAlignment(Qt.AlignRight)
        scroll_layout.addWidget(fonte_label)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        action_layout = QHBoxLayout()
        btn_voltar = QPushButton("")
        btn_voltar.setCursor(Qt.PointingHandCursor)
        btn_voltar.setIcon(QIcon("images/voltar.png"))
        btn_voltar.setIconSize(QSize(22, 22))
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
        """)
        btn_voltar.clicked.connect(self.voltar_dashboard)
        action_layout.addWidget(btn_voltar)
        action_layout.addStretch()

        
        main_layout.addLayout(action_layout)

    def create_info_card(self, title, value):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9e9e9e; font-size: 12px; background: none;")
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background: none;")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def voltar_dashboard(self):
        from ui.dashboardinicial import DashboardInicial
        self.dashboard = DashboardInicial(self.user, self.empresa_id)
        self.dashboard.showMaximized()
        self.close()
