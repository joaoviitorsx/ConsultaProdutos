from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from repository.atividade_repository import obter_atividades_por_dia
from repository.produto_admin_repository import listar_ultimos_produtos, contar_produtos, contar_produtos_mes_atual
from repository.usuario_repository import listar_ultimos_usuarios, contar_usuarios, contar_usuarios_mes_atual
from repository.fornecedor_repository import listar_ultimos_fornecedores, contar_fornecedores, contar_fornecedores_mes_atual


class DashboardCard(QFrame):
    def __init__(self, titulo, valor, subtitulo, icone_path, cor_valor="#FFFFFF", cor_extra="#00D26A"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1F2536;
                border-radius: 12px;
                padding: 5px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(8)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(icone_path).pixmap(32, 32))
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.icon_label)

        self.title_label = QLabel(titulo)
        self.title_label.setStyleSheet("color: #B0B0B0; font-size: 10pt;")
        self.layout.addWidget(self.title_label)

        self.value_label = QLabel(str(valor))
        self.value_label.setStyleSheet(f"font-size: 22pt; font-weight: bold; color: {cor_valor};")
        self.layout.addWidget(self.value_label)

        self.extra_label = QLabel(subtitulo)
        self.extra_label.setStyleSheet(f"color: {cor_extra}; font-size: 9pt;")
        self.layout.addWidget(self.extra_label)

        self.layout.addStretch()

    def set_valor(self, novo_valor: str):
        self.value_label.setText(str(novo_valor))

    def set_extra(self, novo_texto: str):
        self.extra_label.setText(novo_texto)


class DashboardAdminTela(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1A1F2C;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(15)

        self.card_fornecedores = DashboardCard("Fornecedores", "...", "Carregando...", "images/fornecedor1.png")
        self.card_produtos = DashboardCard("Produtos", "...", "Carregando...", "images/produto1.png")
        self.card_usuarios = DashboardCard("Usuários", "...", "Carregando...", "images/usuario1.png")

        self.cards_layout.addWidget(self.card_fornecedores)
        self.cards_layout.addWidget(self.card_produtos)
        self.cards_layout.addWidget(self.card_usuarios)

        layout.addLayout(self.cards_layout)

        grafico_frame = QFrame()
        grafico_frame.setStyleSheet("""
            QFrame {
                background-color: #1F2536;
                border-radius: 12px;
                padding: 20px;
            }
            QLabel {
                color: #888;
                font-size: 11pt;
            }
        """)
        self.grafico_layout = QVBoxLayout(grafico_frame)
        self.grafico_layout.addWidget(QLabel("Relatório de Atividades"))
        layout.addWidget(grafico_frame)

        transacoes_frame = QFrame()
        transacoes_frame.setStyleSheet("""
            QFrame {
                background-color: #1F2536;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        self.transacoes_layout = QVBoxLayout(transacoes_frame)
        self.transacoes_layout.addWidget(QLabel("Últimos Produtos", styleSheet="color: white; font-weight: bold; font-size: 12pt;"))
        layout.addWidget(transacoes_frame)

        usuarios_frame, self.usuarios_layout = self.criar_bloco_listagem("Últimos Usuários")
        layout.addWidget(usuarios_frame)

        fornecedores_frame, self.fornecedores_layout = self.criar_bloco_listagem("Últimos Fornecedores")
        layout.addWidget(fornecedores_frame)

        self.carregar_dados()

    def criar_bloco_listagem(self, titulo):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1F2536;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(frame)
        label = QLabel(titulo)
        label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
        layout.addWidget(label)
        return frame, layout

    def carregar_dados(self):
        try:
            self.card_fornecedores.set_valor(contar_fornecedores())
            self.card_produtos.set_valor(contar_produtos())
            self.card_usuarios.set_valor(contar_usuarios())

            self.card_fornecedores.set_extra(f"+{contar_fornecedores_mes_atual()} este mês")
            self.card_produtos.set_extra(f"+{contar_produtos_mes_atual()} este mês")

            novos_usuarios = contar_usuarios_mes_atual()
            subtitulo_usuarios = "Nenhum novo" if novos_usuarios == 0 else f"+{novos_usuarios} este mês"
            self.card_usuarios.set_extra(subtitulo_usuarios)

            self.gerar_grafico_atividades(self.grafico_layout)

            self.atualizar_transacoes()
            self.atualizar_usuarios()
            self.atualizar_fornecedores()

        except Exception as e:
            print("Erro ao carregar dashboard:", e)

    def gerar_grafico_atividades(self, layout_destino):
        dados = obter_atividades_por_dia("tabela_tributacao")
        fig = Figure(figsize=(5, 2.5))
        ax = fig.add_subplot(111)

        dias = list(dados.keys())
        valores = list(dados.values())

        ax.bar(dias, valores, color="#9B87F5")
        ax.set_title("Atividades Recentes")
        ax.set_facecolor("#1F2536")
        fig.patch.set_facecolor('#1F2536')
        ax.tick_params(colors='white')
        ax.title.set_color('white')

        canvas = FigureCanvas(fig)
        layout_destino.addWidget(canvas)

    def atualizar_transacoes(self):
        produtos = listar_ultimos_produtos(limit=4)
        for p in produtos:
            texto = f"🧾 {p['produto']} — {p['codigo']} | Empresa: {p['empresa']} | ID #{p['criado_em']}"
            label = QLabel(texto)
            label.setStyleSheet("color: #DDD; font-size: 10pt; margin-bottom: 5px;")
            self.transacoes_layout.addWidget(label)

    def atualizar_usuarios(self):
        usuarios = listar_ultimos_usuarios(limit=4)
        for u in usuarios:
            texto = f"👤 {u['nome']} — Cadastrado"
            label = QLabel(texto)
            label.setStyleSheet("color: #DDD; font-size: 10pt; margin-bottom: 5px;")
            self.usuarios_layout.addWidget(label)

    def atualizar_fornecedores(self):
        fornecedores = listar_ultimos_fornecedores(limit=4)
        for f in fornecedores:
            texto = f"🏢 {f['razao_social']} — CNPJ: {f['cnpj']} | ID #{f['id']}"
            label = QLabel(texto)
            label.setStyleSheet("color: #DDD; font-size: 10pt; margin-bottom: 5px;")
            self.fornecedores_layout.addWidget(label)