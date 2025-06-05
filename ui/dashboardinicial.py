from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QSizePolicy, QScrollArea, QGridLayout
from PySide6.QtWidgets import QScrollBar, QSpacerItem
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtGui import QFont, QPixmap, QCursor, QIcon, QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QRect, QPoint, QTimer, Signal


class RoundedIconButton(QPushButton):
    def __init__(self, icon_path, color="#E53935", hover_color="#C62828", size=36):
        super().__init__()
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(size//2, size//2))
        self.color = QColor(color)
        self.hover_color = QColor(hover_color)
        self.is_hovered = False
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: {size//2}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)


class AnimatedCard(QFrame):
    clicked = Signal()
    
    def __init__(self, icon_path, title, description_list, accent_color="#E53935"):
        super().__init__()
        self.setFixedSize(380, 280)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.accent_color = accent_color
        self.is_hovered = False
        
        self.setStyleSheet(f"""
            AnimatedCard {{
                background-color: #212121;
                border: 1px solid #2e2e2e;
                border-radius: 12px;
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 22, 25, 22)
        self.layout.setSpacing(15)
        
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_container = QFrame()
        self.icon_container.setFixedSize(80, 80)
        self.icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: #454343;
                border-radius: 40px;
            }}
        """)
        icon_layout = QVBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        
        self.desc_label = QLabel()
        desc_text = "<ul style='margin: 0; padding-left: 18px;'>"
        for item in description_list:
            desc_text += f"<li style='margin-bottom: 6px; color: #bbbbbb;'>{item}</li>"
        desc_text += "</ul>"
        self.desc_label.setText(desc_text)
        self.desc_label.setStyleSheet("font-size: 13px;")
        self.desc_label.setTextFormat(Qt.RichText)
        self.desc_label.setWordWrap(True)
        
        self.button = QPushButton("Acessar")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(accent_color)};
            }}
        """)
        self.button.clicked.connect(self.clicked.emit)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.icon_container)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.desc_label)
        self.layout.addStretch()
        self.layout.addWidget(self.button)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(600)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def _darken_color(self, color_hex):
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        color.setHsv(h, s, max(0, v - 20), a)
        return color.name()
    
    def enterEvent(self, event):
        self.is_hovered = True
        self.setStyleSheet(f"""
            AnimatedCard {{
                background-color: #212121;
                border: 1px solid {self.accent_color};
                border-radius: 12px;
            }}
        """)
        
        rect = self.geometry()
        self.hover_animation.setStartValue(rect)
        self.hover_animation.setEndValue(QRect(rect.x(), rect.y() - 5, rect.width(), rect.height()))
        self.hover_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.is_hovered = False
        self.setStyleSheet(f"""
            AnimatedCard {{
                background-color: #212121;
                border: 1px solid #2e2e2e;
                border-radius: 12px;
            }}
        """)
        
        rect = self.geometry()
        self.hover_animation.setStartValue(rect)
        self.hover_animation.setEndValue(QRect(rect.x(), rect.y() + 5, rect.width(), rect.height()))
        self.hover_animation.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class DashboardInicial(QWidget):
    def __init__(self, user: str, empresa_id: int):
        super().__init__()
        self.setWindowTitle("Assertivus Contábil - Dashboard")
        self.setGeometry(300, 100, 1200, 700)
        
        self.font = QFont("Segoe UI", 10)
        self.setFont(self.font)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #181818;
                color: #e0e0e0;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.user = user
        self.empresa_id = empresa_id
        self.animations = [] 
        self.init_ui()
        
        QTimer.singleShot(100, self.start_animations)
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background-color: #121212;
                border-bottom: 1px solid #2c2c2c;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setSpacing(15)

        logo_container = QHBoxLayout()
        logo_container.setSpacing(12)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/icone.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignVCenter)

        titulo = QLabel("Assertivus Contábil")
        titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        logo_container.addWidget(logo_label)
        logo_container.addWidget(titulo)
        
        user_container = QHBoxLayout()
        user_container.setSpacing(20)
        
    
        saudacao = QLabel(f"Olá, <b>{self.user}</b>")
        saudacao.setStyleSheet("color: white; font-size: 16px;")
        
        btn_logout = RoundedIconButton("images/sair2.png", "#E53935", "#C62828", 40)
        btn_logout.clicked.connect(self.logout)
        
        user_container.addWidget(saudacao)
        user_container.addWidget(btn_logout)
        
        header_layout.addLayout(logo_container)
        header_layout.addStretch()
        header_layout.addLayout(user_container)
        
        main_layout.addWidget(header)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        welcome_section = QVBoxLayout()
        welcome_section.setSpacing(8)
        
        bem_vindo = QLabel(f"Bem-vindo, {self.user.capitalize()}")
        bem_vindo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        bem_vindo.setStyleSheet("color: white; font-size: 32px;")
        
        subtitulo = QLabel("O que você deseja fazer hoje?")
        subtitulo.setStyleSheet("color: #CCCCCC; font-size: 16px;")
        
        welcome_section.addWidget(bem_vindo)
        welcome_section.addWidget(subtitulo)
        
        content_layout.addLayout(welcome_section)
        
        cards_section = QVBoxLayout()
        cards_section.setSpacing(15)
        
        section_title = QLabel("Ações Disponíveis")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 30px; margin-bottom: 20px;")
        cards_section.addWidget(section_title)
        
        cards_grid = QGridLayout()
        cards_grid.setSpacing(15)
        
        card1 = AnimatedCard(
            "images/fornecedor1.png", 
            "Consultar Fornecedor",
            [
                "Dados cadastrais", 
                "Situação fiscal", 
                "Status de isenção", 
                "Regime tributário"
            ],
            "#2196F3"
        )
        card1.clicked.connect(self.abrir_consulta_fornecedor)
        self.animations.append(card1.animation)
        
        card2 = AnimatedCard(
            "images/produto1.png", 
            "Consultar Produtos",
            [
                "Cálculo de impostos", 
                "Preços finais", 
                "Comparação entre fornecedores", 
                "Melhor custo-benefício"
            ],
            "#E53935"
        )
        card2.clicked.connect(self.abrir_tela_consultar_produtos)
        self.animations.append(card2.animation)
        
        card3 = AnimatedCard(
            "images/relatorio1.png", 
            "Relatórios Mensais",
            [
                "Histórico de consultas", 
                "Exportação em PDF", 
                "Filtros por período", 
                "Visão geral da empresa"
            ],
            "#10B981"
        )
        card3.clicked.connect(self.abrir_tela_gerar_relatorios)
        self.animations.append(card3.animation)

        cards_grid.addWidget(card1, 0, 0)
        cards_grid.addWidget(card2, 0, 2)
        cards_grid.addWidget(card3, 0, 1)

        cards_section.addLayout(cards_grid)
        content_layout.addLayout(cards_section)
        
        footer = QFrame()
        footer.setStyleSheet("background-color: transparent;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 20, 0, 10)
        
        copyright = QLabel("© 2025 Assertivus Contábil. Todos os direitos reservados.")
        copyright.setStyleSheet("color: #ffffff; font-size: 12px;")
        
        footer_layout.addStretch()
        footer_layout.addWidget(copyright)
        footer_layout.addStretch()
        
        content_layout.addStretch()
        content_layout.addWidget(footer)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def start_animations(self):
        for i, animation in enumerate(self.animations):
            QTimer.singleShot(i * 150, animation.start)
    
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

    def abrir_tela_gerar_relatorios(self):
        from ui.relatorio_tela import RelatorioTela
        self.relatorio_tela = RelatorioTela(self.user, self.empresa_id)
        self.relatorio_tela.showMaximized()
        self.close()

    def logout(self):
        from ui.login_tela import LoginTela
        self.login_tela = LoginTela()
        self.login_tela.showMaximized()
        self.close()

