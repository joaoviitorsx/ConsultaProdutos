import asyncio
import traceback
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,QFrame, QScrollArea, QGridLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QMetaObject, Slot, Signal, QSize
from PySide6.QtGui import QFont, QCursor, QIntValidator, QIcon
from utils.mensagem import mensagem_error
from utils.cnpj import remover_caracteres_nao_numericos, buscar_informacoes_api_segura
from PySide6.QtCore import QThread
from services.fornecedor_service import consultar_dados_fornecedor
from services.imposto_service import calcular_impostos_detalhados
from PySide6.QtGui import QDoubleValidator
from repository.consulta_repository import registrar_consulta
from models.fornecedor import Fornecedor
from models.produto import Produto

buscar_informacoes = buscar_informacoes_api_segura

class AsyncHelper(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._coro = None
        self._callback = None

    def run_coroutine(self, coro, callback=None):
        self._coro = coro
        self._callback = callback
        self.start()

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._coro)
            self.finished.emit(result)
            if self._callback:
                self._callback(result)
        except Exception as e:
            traceback.print_exc()  # exibe a stack completa no terminal
            self.error.emit(f"Erro em thread assíncrona: {str(e)}")

    def stop(self):
        if self.isRunning():
            self.quit()
            self.wait()

class CardFornecedor(QFrame):
    def __init__(self, numero, on_processar_callback, async_helper, on_remover_callback=None):
        super().__init__()
        self.numero = numero
        self.on_processar_callback = on_processar_callback
        self.async_helper = async_helper
        self.on_remover_callback = on_remover_callback

        self.setStyleSheet("""
            QFrame {
                background-color: #212121;
                border-radius: 12px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #E53935;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Cabeçalho do card com badge de número e botão de remover
        header = QHBoxLayout()
        
        numero_badge = QLabel(f"#{self.numero}")
        numero_badge.setStyleSheet("""
            background-color: #E53935;
            color: white;
            font-weight: bold;
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 12px;
        """)
        
        titulo = QLabel(f"Fornecedor {self.numero}")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        
        header.addWidget(numero_badge)
        header.addSpacing(10)
        header.addWidget(titulo)
        header.addStretch()
        
        # Botão de remover (X)
        if self.on_remover_callback and self.numero > 1:
            btn_remover = QPushButton("✕")
            btn_remover.setCursor(Qt.PointingHandCursor)
            btn_remover.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 4px 8px;
                    min-width: 24px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #E53935;
                }
            """)
            btn_remover.clicked.connect(lambda: self.on_remover_callback(self))
            header.addWidget(btn_remover)
        
        layout.addLayout(header)

        # Campo CNPJ
        cnpj_label = QLabel("CNPJ do Fornecedor")
        cnpj_label.setStyleSheet("font-size: 13px; color: #ffffff; margin-top: 5px;")
        layout.addWidget(cnpj_label)
        
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("00.000.000/0000-00")
        self.input_cnpj.setInputMask("00.000.000/0000-00")
        self.input_cnpj.setMinimumHeight(40)
        layout.addWidget(self.input_cnpj)

        # Campo Código do Produto
        codigo_label = QLabel("Código do Produto")
        codigo_label.setStyleSheet("font-size: 13px; color: #ffffff; margin-top: 5px;")
        layout.addWidget(codigo_label)

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ex: 12345")
        self.input_codigo.setMinimumHeight(40)
        self.input_codigo.setValidator(QIntValidator())
        layout.addWidget(self.input_codigo)

        # Campo Valor
        valor_label = QLabel("Valor do Produto")
        valor_label.setStyleSheet("font-size: 13px; color: #ffffff; margin-top: 5px;")
        layout.addWidget(valor_label)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Ex: 1249.99")
        self.input_valor.setMinimumHeight(40)

        # Aplicar validador numérico com 2 casas decimais
        validador = QDoubleValidator(0.0, 9999999.99, 2)
        validador.setNotation(QDoubleValidator.StandardNotation)
        self.input_valor.setValidator(validador)

        layout.addWidget(self.input_valor)

        # Espaçador para empurrar o botão para baixo
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Botão de processar
        self.btn_processar = QPushButton("Processar")
        self.btn_processar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_processar.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
            QPushButton:pressed {
                background-color: #C63828;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.btn_processar.setMinimumHeight(45)
        self.btn_processar.clicked.connect(self.processar)
        layout.addWidget(self.btn_processar)

        if not self.on_processar_callback or not callable(self.on_processar_callback):
            self.btn_processar.setEnabled(False)

    def get_codigo_produto(self):
        return self.input_codigo.text().strip()

    def processar(self):
        cnpj = self.input_cnpj.text()
        valor = self.input_valor.text()
        codigo = self.input_codigo.text().strip()
        if not codigo:
            mensagem_error("Informe o código do produto.")
            return

        # Validação básica
        cnpj_limpo = remover_caracteres_nao_numericos(cnpj)
        if not cnpj or len(cnpj_limpo) != 14:
            mensagem_error("CNPJ inválido. Por favor, verifique.")
            return

        if not valor.strip():
            mensagem_error("Informe um valor para o produto.")
            return

        # Desabilita o botão
        self.btn_processar.setEnabled(False)
        self.btn_processar.setText("Processando...")

        print(f"[DEBUG] Botão 'Processar' clicado | CNPJ: {cnpj} | Valor: {valor}")
        print("[DEBUG] Chamando on_processar_callback (coroutine)...")

        def resultado_callback(result):
            print(f"[DEBUG] → Resultado recebido no callback: {result}")
            
            parent = self._encontrar_pai_com_atributo("registrar_resultado")
            if parent:
                parent.resultado_processado.emit(result)
            else:
                print("[ERRO] → Não foi possível encontrar o parent com atributo 'registrar_resultado'.")

        try:
            self.async_helper.run_coroutine(
                self.on_processar_callback(cnpj, valor, codigo, self.numero),
                callback=resultado_callback
            )
        except Exception as e:
            print(f"[ERRO ao iniciar run_coroutine] {str(e)}")
            mensagem_error("Erro inesperado ao iniciar o processamento.")
            self._processar_concluido(None)

    def _encontrar_pai_com_atributo(self, atributo: str):
        parent = self.parent()
        while parent:
            if hasattr(parent, atributo):
                return parent
            parent = parent.parent()
        return None

    def _processar_concluido(self, result):
        # Reabilitar o botão após o processamento
        self.btn_processar.setEnabled(True)
        self.btn_processar.setText("Processar")
        
        # Feedback visual de sucesso/erro
        if result is None:
            self.setStyleSheet("""
                QFrame {
                    background-color: #212121;
                    border-radius: 12px;
                    border: 1px solid #b91c1c;
                }
            """)
            QTimer.singleShot(2000, lambda: self.setStyleSheet("""
                QFrame {
                    background-color: #212121;
                    border-radius: 12px;
                    border: 1px solid #333333;
                }
                QFrame:hover {
                    border: 1px solid #444444;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #444444;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 1px solid #0f766e;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """))
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #212121;
                    border-radius: 12px;
                    border: 1px solid #0f766e;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #444444;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """)
            QTimer.singleShot(2000, lambda: self.setStyleSheet("""
                QFrame {
                    background-color: #212121;
                    border-radius: 12px;
                    border: 1px solid #333333;
                }
                QFrame:hover {
                    border: 1px solid #444444;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #444444;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 1px solid #0f766e;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """))

class ResultadoCard(QFrame):
    def __init__(self, resultado, is_melhor=False, parent=None):
        super().__init__(parent)
        self.resultado = resultado
        self.is_melhor = is_melhor

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumWidth(800)
        self.setMinimumHeight(220)

        border_color = "#14b8a6" if is_melhor else "#E53935"

        self.setObjectName("resultadoCard")
        self.setStyleSheet(f"""
            QFrame#resultadoCard {{
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: #e0e0e0;
                font-size: 14px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # ───── Cabeçalho ─────
        header = QHBoxLayout()

        if is_melhor:
            melhor_badge = QLabel("MELHOR OPÇÃO")
            melhor_badge.setStyleSheet("""
                background-color: #14b8a6;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
            """)
            header.addWidget(melhor_badge)
            header.addSpacing(10)

        numero_label = QLabel(f"Fornecedor #{self.resultado['index']}")
        numero_label.setStyleSheet("color: white; font-weight: bold; font-size: 15px;")
        header.addWidget(numero_label)
        header.addStretch()

        regime_badge = QLabel(self.resultado['regime'])
        regime_badge.setAlignment(Qt.AlignCenter)
        regime_badge.setMinimumWidth(120)
        regime_badge.setStyleSheet("""
            background-color: #2c2c2c;
            color: #e0e0e0;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
        """)
        header.addWidget(regime_badge)

        layout.addLayout(header)

        # ───── Informações principais ─────
        def info_label(titulo, valor):
            lbl = QLabel(f"{titulo}: <b>{valor}</b>")
            lbl.setStyleSheet("font-size: 14px; color: #e0e0e0;")
            return lbl

        layout.addWidget(info_label("CNPJ", self.resultado["cnpj"]))
        layout.addWidget(info_label("Razão Social", self.resultado["razao_social"]))
        layout.addWidget(info_label("Produto", self.resultado.get("nome_produto", "Desconhecido")))

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #333; height: 1px;")
        layout.addWidget(separator)

        # ───── Valores ─────
        valores_grid = QGridLayout()
        valores_grid.setSpacing(5)

        # Valor base
        lbl_base_title = QLabel("Valor Base:")
        lbl_base_title.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        valores_grid.addWidget(lbl_base_title, 0, 0)

        lbl_base = QLabel(f"R$ {self.resultado['valor_base']:.2f}")
        lbl_base.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        valores_grid.addWidget(lbl_base, 0, 1)

        # Cabeçalho de impostos
        lbl_impostos = QLabel("Impostos:")
        lbl_impostos.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        valores_grid.addWidget(lbl_impostos, 1, 0)

        # Layout de cada linha de imposto
        impostos_layout = QVBoxLayout()
        impostos_layout.setContentsMargins(0, 0, 0, 0)
        impostos_layout.setSpacing(4)

        for nome, valor in self.resultado['impostos'].items():
            cor = "#eab308"
            texto = f"{nome}: {valor}"
            if isinstance(valor, (float, int)):
                cor = "#f87171"
                texto = f"{nome}: R$ {valor:.2f}"
            elif str(valor).lower() == "não paga":
                cor = "#4ade80"

            imposto_label = QLabel(texto)
            imposto_label.setStyleSheet(f"color: {cor}; font-size: 13px; font-weight: bold;")
            impostos_layout.addWidget(imposto_label)

        impostos_widget = QWidget()
        impostos_widget.setLayout(impostos_layout)
        valores_grid.addWidget(impostos_widget, 1, 1, Qt.AlignTop)

        # Valor total
        lbl_total_title = QLabel("Valor Total:")
        lbl_total_title.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        valores_grid.addWidget(lbl_total_title, 2, 0)

        total_label = QLabel(f"R$ {self.resultado['valor_total']:.2f}")
        total_color = "#4ade80" if is_melhor else "white"
        total_label.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {total_color};")
        valores_grid.addWidget(total_label, 2, 1)

        layout.addLayout(valores_grid)

        # ───── Isenção (baseada no resultado real dos impostos) ─────
        icms = self.resultado["impostos"].get("ICMS", "Não paga")
        simples = self.resultado["impostos"].get("Simples", "Não paga")

        nenhum_imposto = all(str(v).lower() == "não paga" for v in [icms, simples])

        if nenhum_imposto:
            isento_info = QLabel("✓ Produto isento de impostos (nenhum imposto aplicado)")
            isento_info.setStyleSheet("color: #4ade80; font-size: 13px;")
        else:
            isento_info = QLabel("✗ Impostos foram aplicados neste produto")
            isento_info.setStyleSheet("color: #f87171; font-size: 13px;")

        layout.addWidget(isento_info)

class ConsultaProdutoTela(QWidget):
    resultado_processado = Signal(dict)

    def __init__(self, user: str, empresa_id: int):
        super().__init__()
        self.buscar_informacoes = consultar_dados_fornecedor

        self.user = user
        self.empresa_id = empresa_id
        self.max_fornecedores = 4
        self.contador = 0 
        self.cards = []
        self.resultados = []

        self.resultado_processado.connect(self.registrar_resultado_seguro)
        self.async_helper = AsyncHelper()
        self.async_helper.error.connect(self.mostrar_erro)

        self.setWindowTitle("Consulta de Produtos")
        self.setGeometry(300, 100, 1200, 800)
        self.setStyleSheet("""
            QWidget { background-color: #181818; color: #e0e0e0; }
            QScrollArea { border: none; background-color: transparent; }
        """)

        self.init_ui()
        self.adicionar_card()  # inicia com 1 card

    def mostrar_erro(self, mensagem):
        print(f"[ERRO FATAL] → {mensagem}")
        mensagem_error(mensagem)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #121212; border-bottom: 1px solid #2c2c2c;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

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

        titulo = QLabel("Consulta de Produtos")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        titulo.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(btn_voltar)
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        main_layout.addWidget(header)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container = QWidget()
        self.cards_container.setLayout(self.cards_layout)
        self.cards_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #E53935;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #ff6f61;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }

            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.cards_scroll.setWidget(self.cards_container)

        btn_container = QWidget()
        btn_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_adicionar = QPushButton("+ Adicionar Fornecedor")
        self.btn_adicionar.setCursor(Qt.PointingHandCursor)
        self.btn_adicionar.setMinimumHeight(50)
        self.btn_adicionar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #0f766e;
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0d9488;
            }
            QPushButton:pressed {
                background-color: #0f766e;
            }
            QPushButton:disabled {
                background-color: #2e2e2e;
                color: #888888;
            }
        """)
        self.btn_adicionar.clicked.connect(self.adicionar_card)

        btn_layout.addWidget(self.btn_adicionar)
        self.cards_layout.addWidget(btn_container)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        titulo_fornecedores = QLabel("Comparação de Fornecedores")
        titulo_fornecedores.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        left_panel.addWidget(titulo_fornecedores)

        subtitulo = QLabel("Adicione até 4 fornecedores para comparar impostos e valores")
        subtitulo.setStyleSheet("font-size: 13px; color: #aaaaaa; margin-bottom: 5px;")
        left_panel.addWidget(subtitulo)

        left_panel.addWidget(self.cards_scroll)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setStyleSheet("background-color: #1a1a1a; border-radius: 8px; padding: 10px;")


        self.resultados_layout = QVBoxLayout()
        self.resultados_layout.setAlignment(Qt.AlignTop)

        self.resultados_container = QWidget()
        self.resultados_container.setLayout(self.resultados_layout)

        self.resultados_scroll = QScrollArea()
        self.resultados_scroll.setWidgetResizable(True)
        self.resultados_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #E53935;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #ff6f61;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.resultados_scroll.setWidget(self.resultados_container)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        titulo_resultados = QLabel("Resultado da Análise")
        titulo_resultados.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        right_panel.addWidget(titulo_resultados)

        right_panel.addWidget(self.resultados_scroll)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setStyleSheet("background-color: #1a1a1a; border-radius: 8px; padding: 10px;")
        content_layout.addWidget(left_widget, 4)
        content_layout.addWidget(right_widget, 6)

        main_layout.addWidget(content)
 
    def adicionar_card(self):
        if len(self.cards) >= self.max_fornecedores:
            self.btn_adicionar.setEnabled(False)
            return

        usados = set(card.numero for card in self.cards)

        numero_disponivel = 1
        while numero_disponivel in usados:
            numero_disponivel += 1

        card = CardFornecedor(
            numero_disponivel,
            self.processar_fornecedor,
            self.async_helper,
            on_remover_callback=self.remover_card
        )

        self.cards.append(card)
        self.cards_layout.insertWidget(self.cards_layout.count() - 2, card)

        if len(self.cards) >= self.max_fornecedores:
            self.btn_adicionar.setEnabled(False)

    def remover_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            card.setParent(None)
            card.deleteLater()

            self.resultados = [r for r in self.resultados if r['index'] != card.numero]
            self.atualizar_resultado()

            # Reativa botão de adicionar se abaixo do limite
            if len(self.cards) < self.max_fornecedores:
                self.btn_adicionar.setEnabled(True)

    async def processar_fornecedor(self, cnpj: str, valor_str: str, codigo: str, index: int):
        try:
            valor_str = valor_str.replace(",", ".")
            valor_float = float(valor_str)
        except ValueError:
            mensagem_error("Valor inválido.")
            return

        cnpj_limpo = remover_caracteres_nao_numericos(cnpj)

        card = next((c for c in self.cards if c.numero == index), None)
        if not card:
            mensagem_error("Erro interno: Card não encontrado.")
            return

        codigo_produto = card.get_codigo_produto()
        if not codigo_produto:
            mensagem_error("Informe o código do produto.")
            return

        try:
            from services.imposto_service import calcular_impostos_detalhados
            resultado = await asyncio.to_thread(
                calcular_impostos_detalhados,
                cnpj_limpo,
                codigo_produto,
                valor_float,
                self.empresa_id
            )

            print("[DEBUG] Conteúdo de resultado:", resultado)

            resultado["index"] = index

            fornecedor_model = Fornecedor(
                cnpj=cnpj_limpo,
                razao_social=resultado["razao_social"],
                simples=(resultado["regime"] == "Simples Nacional"),
                cnae_codigo=resultado.get("cnae", ""),  # ou "0000000" como padrão
                isento=resultado.get("isento", False),
                uf=resultado.get("uf", "")
            )

            produto_model = Produto(
                codigo=codigo_produto,
                nome=resultado["nome_produto"],
                aliquota=resultado["aliquota"],
                ncm=resultado.get("ncm", ""),
                valor_base=resultado.get("valor_base", 0.0),
                valor_total=resultado.get("valor_total", 0.0)
            )

            registrar_consulta(
                empresa_id=self.empresa_id,
                user=self.user,
                fornecedor=fornecedor_model,
                produto=produto_model
            )
            self.resultado_processado.emit(resultado)
            return resultado

        except Exception as e:
            import traceback
            traceback.print_exc()
            mensagem_error(f"Erro ao processar fornecedor: {e}")
            return None

    @Slot()
    def atualizar_resultado(self):
        self.resultados_container.setUpdatesEnabled(False)
        self.resultados_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        for i in reversed(range(self.resultados_layout.count())):
            widget = self.resultados_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        if not self.resultados:
            msg = QLabel("Nenhum produto processado ainda.")
            msg.setStyleSheet("color: #aaa; font-size: 14px; padding: 20px;")
            msg.setAlignment(Qt.AlignCenter)
            self.resultados_layout.addWidget(msg)
        else:
            menor = min(self.resultados, key=lambda r: r["valor_total"])
            for resultado in sorted(self.resultados, key=lambda r: r["valor_total"]):
                is_melhor = resultado == menor
                card = ResultadoCard(resultado, is_melhor, parent=self.resultados_container)
                self.resultados_layout.addWidget(card)

        self.resultados_container.setUpdatesEnabled(True)
        self.resultados_container.update()

    def voltar_dashboard(self):
        self.async_helper.stop()
        from ui.dashboardinicial import DashboardInicial
        self.dashboard = DashboardInicial(self.user, self.empresa_id)
        self.dashboard.showMaximized()
        self.close()
    
    def closeEvent(self, event):
        self.async_helper.stop()
        self.resultados.clear()
        super().closeEvent(event)

    @Slot(dict)
    def registrar_resultado_seguro(self, result: dict):
        if result is None:
            return
        for card in self.cards:
            if result and "index" in result and card.numero == result["index"]:
                card._resultado_temporario = result
                break
        self.registrar_resultado(result)

    def registrar_resultado(self, result: dict):
        if any(r["cnpj"] == result["cnpj"] and r["index"] != result["index"] for r in self.resultados):
            mensagem_error(f"O CNPJ {result['cnpj']} já foi processado em outro fornecedor.")
            return

        self.resultados = [r for r in self.resultados if r["index"] != result["index"]]
        self.resultados.append(result)
        self.atualizar_resultado()


