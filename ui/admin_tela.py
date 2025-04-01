from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,QStackedWidget, QListWidget, QListWidgetItem, QMessageBox,QFrame, QSizePolicy, QScrollArea
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QIcon
from ui.dashboard_admin_tela import DashboardAdminTela
from ui.fornecedor_admin_tela import FornecedorAdminTela
from ui.produto_admin_tela import ProdutoAdminTela
from ui.usuario_admin_tela import UsuarioAdminTela
from ui.log_visualizacao import LogVisualizacaoTela
from ui.cadastro_empresa_admin import CadastroEmpresaTela


class AdminTela(QWidget):
    def __init__(self, user: str):
        super().__init__()
        self.user = user
        self.setWindowTitle("Painel do Administrador")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(self.estilo())
        self.setup_ui()

    def estilo(self):
        return """
            QWidget {
                background-color: #1A1F2C;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }

            QFrame#header {
                background-color: #151A26;
                border-bottom: 1px solid #2E3445;
            }

            QPushButton#toggleSidebar {
                background-color: transparent;
                border: none;
                padding: 6px;
            }

            QPushButton#toggleSidebar:hover {
                background-color: #2E3445;
                border-radius: 6px;
            }

            QLabel#headerTitle {
                font-size: 14pt;
                font-weight: bold;
                color: #FFFFFF;
            }

            QLabel#labelTela {
                font-size: 13pt;
                color: #D32F2F;
                font-weight: bold;
            }

            QLabel#headerUser {
                background-color: #2E3445;
                border-radius: 15px;
                padding: 5px 15px;
            }

            QListWidget#sidebarMenu {
                background-color: #1A1F2C;
                border: none;
                border-right: 1px solid #2E3445;
                font-size: 11pt;
                padding-top: 10px;
            }

            QListWidget#sidebarMenu::item {
                height: 48px;
                padding-left: 10px;
                border-radius: 5px;
                margin: 2px 5px;
            }

            QListWidget#sidebarMenu::item:selected {
                background-color: #D32F2F;
                color: white;
            }

            QListWidget#sidebarMenu::item:hover:!selected {
                background-color: #2E3445;
            }

            QScrollArea {
                border: none;
            }

            QPushButton {
                background-color: #D32F2F;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
            }

            QPushButton:hover {
                background-color: #5c1414;
            }
        """

    def setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # HEADER
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.btn_toggle_menu = QPushButton()
        self.btn_toggle_menu.setIcon(QIcon("images/sidebarfechar.png"))
        self.btn_toggle_menu.setIconSize(QSize(24, 24))
        self.btn_toggle_menu.setObjectName("toggleSidebar")
        self.btn_toggle_menu.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_menu.setFixedSize(40, 40)
        self.btn_toggle_menu.clicked.connect(self.toggle_sidebar)

        logo_label = QLabel("Painel do Administrador")
        logo_label.setObjectName("headerTitle")

        self.label_tela = QLabel("Dashboard")
        self.label_tela.setObjectName("labelTela")

        self.label_user = QLabel(f"{self.user}")
        self.label_user.setObjectName("headerUser")
        self.label_user.setFixedHeight(30)

        header_layout.addWidget(self.btn_toggle_menu)
        header_layout.addSpacing(10)
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.label_tela)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.label_user)

        layout_principal.addWidget(header)

        # CONTEÚDO PRINCIPAL
        conteudo = QHBoxLayout()
        conteudo.setContentsMargins(0, 0, 0, 0)

        # SIDEBAR
        self.sidebar_scroll = QScrollArea()
        self.sidebar_scroll.setFixedWidth(260)
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_scroll.setFrameShape(QFrame.NoFrame)

        sidebar_inner = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_inner)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        sidebar_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebarMenu")
        self.sidebar.setSpacing(6)
        self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sidebar.setMouseTracking(True)
        self.sidebar.viewport().installEventFilter(self)


        menu_items = [
            {"texto": "Dashboard", "icone": "images/dashboard1.png"},
            {"texto": "Fornecedores", "icone": "images/fornecedor1.png"},
            {"texto": "Produtos", "icone": "images/produto1.png"},
            {"texto": "Usuários", "icone": "images/usuario1.png"},
            {"texto": "Relatórios", "icone": "images/relatorio1.png"},
            {"texto": "Cadastrar Empresa", "icone": "images/cadastro1.png"},
        ]

        for item in menu_items:
            self.adicionar_menu(item["texto"], item["icone"])


        self.sidebar.currentRowChanged.connect(self.navegar)

        sidebar_layout.addWidget(self.sidebar, stretch=1)

        # Criar botão de sair e container antes de adicionar ao layout
        self.btn_sair = QPushButton("  Sair")
        self.btn_sair.setIcon(QIcon("images/sair1.png"))
        self.btn_sair.setCursor(Qt.PointingHandCursor)
        self.btn_sair.setFixedHeight(40)
        self.btn_sair.setMinimumWidth(150)
        self.btn_sair.clicked.connect(lambda: self.navegar(6))
        
        sair_container = QWidget()
        sair_layout = QHBoxLayout(sair_container)
        sair_layout.setContentsMargins(0, 0, 0, 0)
        sair_layout.setAlignment(Qt.AlignCenter)
        sair_layout.addWidget(self.btn_sair)

        sidebar_layout.addWidget(sair_container, alignment=Qt.AlignBottom)

        sidebar_layout.addWidget(sair_container)
        self.sidebar_scroll.setWidget(sidebar_inner)

        # CONTEÚDO CENTRAL
        self.stack = QStackedWidget()
        self.tela_dashboard = DashboardAdminTela()
        self.tela_fornecedor = FornecedorAdminTela()
        self.tela_produto = ProdutoAdminTela()
        self.tela_usuarios = UsuarioAdminTela()
        self.tela_logs = LogVisualizacaoTela()
        self.tela_cadastro = CadastroEmpresaTela()
        self.tela_cadastro.empresa_cadastrada.connect(self.atualizar_empresas_nas_telas)

        self.stack.addWidget(self.tela_dashboard)
        self.stack.addWidget(self.tela_fornecedor)
        self.stack.addWidget(self.tela_produto)
        self.stack.addWidget(self.tela_usuarios)
        self.stack.addWidget(self.tela_logs)
        self.stack.addWidget(self.tela_cadastro)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.stack)

        conteudo.addWidget(self.sidebar_scroll)
        conteudo.addWidget(scroll_area)

        layout_principal.addLayout(conteudo)
        self.setLayout(layout_principal)
        self.sidebar.setCurrentRow(0)

    def adicionar_menu(self, texto, icone_path):
        item = QListWidgetItem(QIcon(icone_path), "  " + texto)
        item.setSizeHint(QSize(200, 40))
        self.sidebar.addItem(item)

        # Aplica o cursor de mão ao item da lista após inserção
        index = self.sidebar.count() - 1
        item_widget = self.sidebar.item(index)
        self.sidebar.item(index).setData(Qt.UserRole, Qt.PointingHandCursor)
        

    def toggle_sidebar(self):
        largura_atual = self.sidebar_scroll.width()
        sidebar_aberta = largura_atual > 0
        nova_largura = 0 if sidebar_aberta else 260

        # Atualiza ícone do botão
        novo_icone = QIcon("images/sidebarfechar.png") if not sidebar_aberta else QIcon("images/sidebarabrir.png")
        self.btn_toggle_menu.setIcon(novo_icone)

        # Animações de abertura/fechamento
        anim1 = QPropertyAnimation(self.sidebar_scroll, b"minimumWidth")
        anim2 = QPropertyAnimation(self.sidebar_scroll, b"maximumWidth")

        for anim in (anim1, anim2):
            anim.setDuration(300)
            anim.setStartValue(largura_atual)
            anim.setEndValue(nova_largura)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            anim.start()

        self.anim_sidebar_1 = anim1
        self.anim_sidebar_2 = anim2

    def navegar(self, index):
        telas = [
            self.tela_dashboard,
            self.tela_fornecedor,
            self.tela_produto,
            self.tela_usuarios,
            self.tela_logs,
            self.tela_cadastro
        ]
        nomes = [
            "Dashboard", "Fornecedores", "Produtos", "Usuários", "Relatórios", "Cadastro"
        ]
        if index < len(telas):
            self.stack.setCurrentWidget(telas[index])
            self.label_tela.setText(nomes[index])
        elif index == 6:
            confirm = QMessageBox.question(
                self, "Sair", "Deseja realmente voltar a tela de Login?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.voltar_para_login()

    def voltar_para_login(self):
        from ui.login_tela import LoginTela
        self.close()
        self.login = LoginTela()
        self.login.showMaximized()

    def atualizar_empresas_nas_telas(self):
        QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
        self.tela_produto.atualizar_empresas()
        self.tela_usuarios.carregar_todos_usuarios()

    def eventFilter(self, source, event):
        if hasattr(self, "sidebar") and source == self.sidebar.viewport():
            if event.type() == QEvent.MouseMove:
                item = self.sidebar.itemAt(event.pos())
                if item:
                    self.sidebar.setCursor(Qt.PointingHandCursor)
                else:
                    self.sidebar.setCursor(Qt.ArrowCursor)
        return super().eventFilter(source, event)

