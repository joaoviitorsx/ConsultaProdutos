import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,QSpacerItem, QSizePolicy, QFrame, QHBoxLayout
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt
from services.produto_service import buscar_produto_por_codigo_service
from models.fornecedor import Fornecedor
from models.produto import Produto
from utils.validacao import validar_codigo
from utils.pdf import PDFGenerator
from utils.mensagem import mensagem_aviso, mensagem_error, mensagem_sucesso
from repository.consulta_repository import registrar_consulta

class ProdutoTela(QWidget):
    def __init__(self, user: str, empresa_id: int, fornecedor: Fornecedor):
        super().__init__()
        self.setWindowTitle("Consulta de Produto")
        self.setGeometry(400, 100, 850, 700)
        self.user = user
        self.empresa_id = empresa_id
        self.fornecedor = fornecedor
        self.produto: Produto | None = None
        self.setup_ui()
        self.aplicar_estilo()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Card principal
        card = QFrame()
        card.setObjectName("cardContainer")
        card.setFixedWidth(650)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignTop)

        # Informações do fornecedor (centralizadas)
        info_container = QFrame()
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignCenter)

        razao = QLabel(f"Razão Social: {self.fornecedor.razao_social}")
        razao.setStyleSheet("font-weight: bold; font-size: 16px; color: white; background: none;")
        info_layout.addWidget(razao)

        dados = QLabel(
            f"CNPJ: {self.fornecedor.cnpj} | "
            f"CNAE: {self.fornecedor.cnae_codigo} | "
            f"UF: {self.fornecedor.uf}"
        )
        dados.setStyleSheet("color: white; background: none;")
        info_layout.addWidget(dados)

        extras = QLabel(
            f"Decreto: {'Sim' if self.fornecedor.isento else 'Não'} | "
            f"Simples: {'Sim' if self.fornecedor.simples else 'Não'}"
        )
        extras.setStyleSheet("color: white; background: none;")
        info_layout.addWidget(extras)

        status_decreto = "ISENTO DE IMPOSTO" if self.fornecedor.isento else "SUJEITO A IMPOSTO"
        status_simples = "PAGA ALÍQUOTA ADICIONAL" if self.fornecedor.simples else "NÃO PAGA ALÍQUOTA ADICIONAL"

        situacao = QLabel(
            f"Situação Tributária:\n- Decreto: {status_decreto}\n- Simples Nacional: {status_simples}"
        )
        situacao.setStyleSheet("color: white; background: none; font-size: 16px; font-weight: bold;")
        info_layout.addWidget(situacao)

        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFrameShadow(QFrame.Sunken)
        info_layout.addWidget(linha)

        card_layout.addWidget(info_container)

        # Título da seção
        titulo = QLabel("Consulta de Produto")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(titulo)

        subtitulo = QLabel("Informe o código do produto para visualizar os dados")
        subtitulo.setObjectName("descricao")
        subtitulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitulo)

        card_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Campo de código
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ex: 12345")
        self.input_codigo.setValidator(QIntValidator())
        self.input_codigo.setObjectName("campoInput")
        self.input_codigo.setAlignment(Qt.AlignCenter)
        self.input_codigo.returnPressed.connect(self.consultar_produto)
        card_layout.addWidget(self.input_codigo)

        # Botão consultar
        self.btn_consultar = QPushButton("Consultar Produto")
        self.btn_consultar.setObjectName("botaoPrincipal")
        self.btn_consultar.setCursor(Qt.PointingHandCursor)
        self.btn_consultar.clicked.connect(self.consultar_produto)
        card_layout.addWidget(self.btn_consultar)

        card_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Painel de resultado
        self.resultado_card = QFrame()
        self.resultado_card.setObjectName("painelResultado")
        resultado_layout = QVBoxLayout(self.resultado_card)
        resultado_layout.setSpacing(8)

        self.titulo_resultado = QLabel("Resumo da Consulta")
        self.titulo_resultado.setStyleSheet("font-size: 18px; font-weight: bold;background: transparent;")
        resultado_layout.addWidget(self.titulo_resultado)

        self.bloco_fornecedor = QLabel()
        self.bloco_fornecedor.setWordWrap(True)
        resultado_layout.addWidget(self.bloco_fornecedor)

        linha_divisoria = QFrame()
        linha_divisoria.setFrameShape(QFrame.HLine)
        linha_divisoria.setFrameShadow(QFrame.Sunken)
        resultado_layout.addWidget(linha_divisoria)

        self.bloco_produto = QLabel()
        self.bloco_produto.setWordWrap(True)
        resultado_layout.addWidget(self.bloco_produto)

        self.resultado_card.hide()
        card_layout.addWidget(self.resultado_card)

        # Botões inferiores
        btn_layout = QHBoxLayout()

        self.btn_pdf = QPushButton("Gerar PDF da Consulta")
        self.btn_pdf.setObjectName("botaoPrincipal")
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.clicked.connect(self.gerar_pdf)
        btn_layout.addWidget(self.btn_pdf)

        self.btn_voltar = QPushButton("Consultar Outro Fornecedor")
        self.btn_voltar.setObjectName("botaoPrincipal")
        self.btn_voltar.setCursor(Qt.PointingHandCursor)
        self.btn_voltar.clicked.connect(self.voltar_para_fornecedor)
        btn_layout.addWidget(self.btn_voltar)

        self.btn_relatorio = QPushButton("Relatório de Consultas")
        self.btn_relatorio.setObjectName("botaoPrincipal")
        self.btn_relatorio.setCursor(Qt.PointingHandCursor)
        self.btn_relatorio.clicked.connect(self.relatorio_tela)
        btn_layout.addWidget(self.btn_relatorio)

        card_layout.addLayout(btn_layout)
        layout.addWidget(card)

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
            }

            #cardContainer {
                background-color: #1f1f1f;
                border-radius: 12px;
                padding: 24px;
            }

            #campoInput {
                background-color: #121212;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #444;
                border-radius: 6px;
            }

            #campoInput:focus {
                border: 1px solid #E53935;
            }

            #botaoPrincipal {
                background-color: #E53935;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            #botaoPrincipal:hover {
                background-color: #C62828;
            }

            #botaoPrincipal:disabled {
                background-color: #444444;
                color: #CCCCCC;
                border: 1px solid #333333;
            }

            #painelResultado {
                background-color:#202020;
                border-radius: 12px;
                padding: 20px;
                color: #1a1a1a;
                font-size: 14px;
                border: 1px solid #ccc;
            }

            #titulo {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }

            #descricao {
                font-size: 13px;
                color: #c0c0c0;
            }
        """)

    def consultar_produto(self):
        codigo = self.input_codigo.text().strip()

        if not validar_codigo(codigo):
            mensagem_aviso("Digite um código de produto válido.")
            return

        produto = buscar_produto_por_codigo_service(codigo, self.empresa_id)

        if not produto:
            mensagem_error("Produto não se encontra na base de dados.")
            self.bloco_fornecedor.setText("")
            self.bloco_produto.setText("")
            self.resultado_card.hide()
            self.btn_pdf.setEnabled(False)
            return

        self.produto = produto
        aliquota_adicional = 3.0 if self.fornecedor.simples else 0.0
        aliquota_total = produto.aliquota + aliquota_adicional
            
        # Dados formatados em HTML
        fornecedor_html = f"""
            <h3 style="margin-bottom: 6px;">Dados do Fornecedor</h3>
            <p><b>Razão Social:</b> {self.fornecedor.razao_social}<br>
            <b>CNPJ:</b> {self.fornecedor.cnpj} |
            <b>CNAE:</b> {self.fornecedor.cnae_codigo} |
            <b>UF:</b> {self.fornecedor.uf}<br>
            <b>Decreto:</b> {"Sim" if self.fornecedor.isento else "Não"} |
            <b>Simples:</b> {"Sim" if self.fornecedor.simples else "Não"}</p>
        """

        produto_html = f"""
            <h3 style="margin-top: 10px; margin-bottom: 6px;">Dados do Produto</h3>
            <p><b>Código:</b> {produto.codigo}<br>
            <b>Produto:</b> {produto.nome}<br>
            <b>NCM:</b> {produto.ncm}<br>
            <b>Alíquota:</b> {produto.aliquota:.2f}%</p>
            <b>Alíquota Adicional (SIMPLES):</b> {aliquota_adicional:.2f}%<br>
            <b>Alíquota Total:</b> {aliquota_total:.2f}%</p>
        """

        registrar_consulta(
            empresa_id=self.empresa_id,
            user=self.user,
            fornecedor=self.fornecedor,
            produto=self.produto
        )

        self.bloco_fornecedor.setTextFormat(Qt.RichText)
        self.bloco_fornecedor.setTextInteractionFlags(Qt.NoTextInteraction)
        self.bloco_fornecedor.setText(fornecedor_html)

        self.bloco_produto.setTextFormat(Qt.RichText)
        self.bloco_produto.setTextInteractionFlags(Qt.NoTextInteraction)
        self.bloco_produto.setText(produto_html)

        self.resultado_card.show()
        self.btn_pdf.setEnabled(True)

    def gerar_pdf(self):
        if not self.produto:
            mensagem_error("Nenhuma informação para gerar PDF.")
            return

        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        nome_arquivo = f"{self.produto.codigo}_{self.fornecedor.razao_social}.pdf"
        caminho_pdf = os.path.join(downloads, nome_arquivo)

        try:
            pdf = PDFGenerator(
                user=self.user,
                razao_social=self.fornecedor.razao_social,
                cnpj=self.fornecedor.cnpj,
                cnae_codigo=self.fornecedor.cnae_codigo,
                uf=self.fornecedor.uf,
                cnae_valido=self.fornecedor.isento,
                simples=self.fornecedor.simples
            )

            pdf.generate_pdf(
                caminho_pdf,
                self.produto.codigo,
                self.produto.nome,
                self.produto.ncm,
                self.produto.aliquota
            )

            mensagem_sucesso(f"PDF gerado com sucesso em:\n{caminho_pdf}")

        except Exception as e:
            mensagem_error(f"Erro ao gerar PDF:\n{e}")

    def voltar_para_fornecedor(self):
        from ui.fornecedor_tela import FornecedorTela
        self.fornecedor_tela = FornecedorTela(self.user, self.empresa_id)
        self.fornecedor_tela.showMaximized()
        self.close()

    def relatorio_tela(self):
        from ui.relatorio_tela import RelatorioTela
        self.relatorio_window = RelatorioTela(
            empresa_id=self.empresa_id,
            razao_social=self.fornecedor.razao_social,
            user=self.user
        )
        self.relatorio_window.showMaximized()
        self.close()