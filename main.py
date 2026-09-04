"""
Ipoint — um "banco" de pontos (não dinheiro de verdade).
App Android feito em Kivy. Login e dados ficam no Supabase (api.py).
"""
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
import threading

import api as db

# ---------------------------------------------------------------------------
# Paleta de cores — azul escuro + ciano, em vários tons
# ---------------------------------------------------------------------------
COR_FUNDO = (0.039, 0.086, 0.157, 1)        # #0A1628 fundo geral
COR_CARD = (0.063, 0.165, 0.275, 1)          # #102A46 cartões
COR_CARD_CLARO = (0.09, 0.22, 0.35, 1)       # cartões/itens de lista
COR_CIANO = (0.0, 0.851, 1.0, 1)             # #00D9FF destaque (conta Comum)
COR_CIANO_ESCURO = (0.0, 0.72, 0.83, 1)      # botões pressionados
COR_TEXTO = (0.92, 0.96, 1.0, 1)
COR_TEXTO_MUTED = (0.60, 0.70, 0.78, 1)
COR_ENTRADA = (0.30, 0.95, 0.75, 1)          # verde-ciano p/ entradas
COR_SAIDA = (1.0, 0.42, 0.42, 1)             # vermelho p/ saídas

# Um tom de azul por categoria de conta
COR_CAT_COMUM = (0.0, 0.851, 1.0, 1)         # ciano
COR_CAT_INVESTIMENTO = (0.25, 0.55, 1.0, 1)  # azul royal
COR_CAT_PORQUINHO = (0.45, 0.75, 1.0, 1)     # azul claro/celeste
COR_CAT_EMPRESTIMO = (0.35, 0.35, 0.95, 1)   # azul-anil (mais escuro/roxeado)

COR_AZUL_ACO = (0.14, 0.36, 0.62, 1)         # azul aço — botões secundários
COR_AZUL_PROFUNDO = (0.02, 0.10, 0.22, 1)    # azul quase-preto — detalhes de fundo
COR_AZUL_MEDIO = (0.10, 0.30, 0.55, 1)       # azul intermediário — variações de card

Window.clearcolor = COR_FUNDO

KV = """
#:import dp kivy.metrics.dp

<CardBox@BoxLayout>:
    canvas.before:
        Color:
            rgba: app.cor_card
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(26)]
    padding: dp(16)
    spacing: dp(8)

<PBButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: app.cor_ciano
    color: (0.02, 0.06, 0.10, 1)
    bold: True
    font_size: "16sp"
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: app.cor_ciano_escuro if self.state == "down" else app.cor_ciano
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(24)]

<PBSecondaryButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: (0,0,0,0)
    color: app.cor_ciano
    bold: True
    font_size: "15sp"
    size_hint_y: None
    height: dp(44)
    canvas.before:
        Color:
            rgba: app.cor_azul_aco if self.state == "normal" else app.cor_azul_medio
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(22)]

<PBTile@Button>:
    background_normal: ""
    background_down: ""
    background_color: (0,0,0,0)
    color: app.cor_texto
    bold: True
    font_size: "13sp"
    halign: "center"
    valign: "middle"
    text_size: self.size
    padding: [dp(4), dp(4)]
    canvas.before:
        Color:
            rgba: app.cor_card_claro if self.state == "normal" else app.cor_azul_medio
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18)]

<PBInput@TextInput>:
    background_color: app.cor_card_claro
    foreground_color: app.cor_texto
    hint_text_color: app.cor_texto_muted
    cursor_color: app.cor_ciano
    padding: [dp(16), dp(14)]
    size_hint_y: None
    height: dp(48)
    multiline: False

<TopBar@BoxLayout>:
    size_hint_y: None
    height: dp(56)
    spacing: dp(8)
    padding: [dp(4), 0]

<Spinner>:
    color: app.cor_texto
    background_normal: ""
    background_down: ""
    background_color: app.cor_card_claro
    canvas.before:
        Color:
            rgba: app.cor_card_claro
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]

<SpinnerOption>:
    color: app.cor_texto
    background_normal: ""
    background_down: ""
    background_color: app.cor_azul_aco

<SpinnerCarregando>:
    source: "spinner.png"
    canvas.before:
        PushMatrix
        Rotate:
            angle: self.angulo
            origin: self.center
    canvas.after:
        PopMatrix

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)

        TopBar:
            Button:
                text: "="
                size_hint_x: None
                width: dp(44)
                background_normal: ""
                background_color: (0,0,0,0)
                color: app.cor_ciano
                bold: True
                font_size: "22sp"
                on_release: root.ir_menu()
            Image:
                source: "icon.png"
                size_hint_x: None
                width: dp(40)
                allow_stretch: True
                keep_ratio: True
            Label:
                text: "Ipoint"
                bold: True
                font_size: "24sp"
                italic: True
                markup: True
                color: app.cor_ciano
                halign: "left"
                valign: "middle"
                text_size: self.size

        CardBox:
            orientation: "vertical"
            size_hint_y: None
            height: dp(140)
            Label:
                text: root.nome_conta_atual
                color: app.cor_texto_muted
                font_size: "14sp"
                halign: "left"
                text_size: self.size
                size_hint_y: None
                height: dp(20)
            Label:
                text: root.saldo_formatado
                color: app.cor_ciano
                bold: True
                font_size: "34sp"
                halign: "left"
                text_size: self.size
            Label:
                text: "pontos disponíveis"
                color: app.cor_texto_muted
                font_size: "12sp"
                halign: "left"
                text_size: self.size
                size_hint_y: None
                height: dp(16)

        GridLayout:
            cols: 3
            size_hint_y: None
            height: dp(158)
            spacing: dp(10)
            PBTile:
                text: "Transferir"
                on_release: root.ir_transferir()
            PBTile:
                text: "Extrato"
                on_release: root.ir_extrato()
            PBTile:
                text: "Depositar"
                on_release: root.ir_depositar()
            PBTile:
                text: "Nova conta"
                on_release: root.ir_nova_conta()
            PBTile:
                text: "Bônus diário"
                on_release: root.resgatar_bonus()
            PBTile:
                text: "Minha Chave"
                on_release: root.ir_chave()

        Label:
            text: "Minhas contas"
            color: app.cor_texto_muted
            bold: True
            size_hint_y: None
            height: dp(24)
            halign: "left"
            text_size: self.size

        ScrollView:
            BoxLayout:
                id: lista_contas
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)

<TransferirScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Transferir"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        CardBox:
            orientation: "vertical"
            size_hint_y: None
            height: dp(200)
            Label:
                text: "De: " + root.nome_origem
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(24)
                halign: "left"
                text_size: self.size
            Label:
                text: "E-mail ou chave de quem vai receber"
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            PBInput:
                id: campo_email_destino
                hint_text: "email@exemplo.com ou IPT-XXXXXXXX"
            Label:
                text: "Valor (pontos)"
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            PBInput:
                id: campo_valor
                hint_text: "ex: 1,50"

        PBButton:
            text: "Confirmar transferência"
            on_release: root.confirmar()

<ExtratoScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Extrato"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size
        ScrollView:
            BoxLayout:
                id: lista_extrato
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(6)

<NovaContaScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Nova conta"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size
        CardBox:
            orientation: "vertical"
            size_hint_y: None
            height: dp(290)
            Label:
                text: "Nome da conta"
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            PBInput:
                id: campo_nome
                hint_text: "ex: Poupança, Filho, Time X..."
            Label:
                text: "Saldo inicial (opcional)"
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            PBInput:
                id: campo_saldo
                hint_text: "0,00"
            Label:
                text: "Categoria"
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            Spinner:
                id: spinner_categoria
                text: "Comum"
                values: ["Comum", "Investimento", "Porquinho", "Empréstimo"]
                size_hint_y: None
                height: dp(44)
                background_normal: ""
                background_color: app.cor_card_claro
                color: app.cor_texto
        PBButton:
            text: "Criar conta"
            on_release: root.criar()

<DepositarScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Depositar"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size
        CardBox:
            orientation: "vertical"
            size_hint_y: None
            height: dp(180)
            Label:
                text: "Depositando em: " + root.nome_conta_atual
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            PBInput:
                id: campo_valor
                hint_text: "Valor (ex: 1,50)"
            PBInput:
                id: campo_desc
                hint_text: "Descrição (opcional)"
        PBButton:
            text: "Confirmar depósito"
            on_release: root.confirmar()

<MenuScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Menu"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        CardBox:
            orientation: "vertical"
            size_hint_y: None
            height: dp(80)
            Label:
                text: "Usuário"
                color: app.cor_texto_muted
                font_size: "13sp"
                size_hint_y: None
                height: dp(18)
                halign: "left"
                text_size: self.size
            Label:
                text: root.nome_usuario
                color: app.cor_texto
                bold: True
                font_size: "18sp"
                halign: "left"
                text_size: self.size

        PBSecondaryButton:
            text: "Termos de Uso"
            on_release: root.ir_termos()

        PBSecondaryButton:
            text: "Minha Chave"
            on_release: root.ir_chave()

        PBSecondaryButton:
            text: "Configurar PIN"
            on_release: root.ir_criar_pin()

        PBSecondaryButton:
            text: "Avisos"
            on_release: root.ir_avisos()

        PBSecondaryButton:
            text: "Trocar senha"
            on_release: root.ir_trocar_senha()

        PBSecondaryButton:
            text: "Sair"
            on_release: root.sair()

<TermosScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Termos de Uso"
                color: app.cor_texto
                bold: True
                font_size: "18sp"
                halign: "left"
                valign: "middle"
                text_size: self.size
        ScrollView:
            Label:
                text: root.texto_termos
                color: app.cor_texto
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: "left"
                valign: "top"
                font_size: "14sp"

<ChaveScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Minha Chave"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        Label:
            text: "Mostre esse QR code ou compartilhe a chave pra alguém te mandar pontos"
            color: app.cor_texto_muted
            size_hint_y: None
            height: dp(50)
            halign: "center"
            text_size: self.width, None

        Widget:
            id: qr_container
            size_hint_y: None
            height: dp(260)

        CardBox:
            orientation: "vertical"
            size_hint_y: None
            height: dp(70)
            Label:
                text: root.texto_chave
                color: app.cor_ciano
                bold: True
                font_size: "18sp"
                halign: "center"
                valign: "middle"
                text_size: self.size

        Widget:

<BootScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: app.cor_fundo
            Rectangle:
                pos: self.pos
                size: self.size
        SpinnerCarregando:
            id: spinner_boot
            size_hint: None, None
            size: dp(140), dp(140)
            pos_hint: {"center_x": 0.5, "center_y": 0.55}
        Label:
            text: "Ipoint"
            color: app.cor_ciano
            bold: True
            font_size: "22sp"
            size_hint: None, None
            size: dp(200), dp(40)
            pos_hint: {"center_x": 0.5, "center_y": 0.30}

<PinScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)

        Widget:
            size_hint_y: None
            height: dp(60)

        Label:
            text: "Ipoint"
            color: app.cor_ciano
            bold: True
            font_size: "30sp"
            size_hint_y: None
            height: dp(44)

        Label:
            text: "Digite seu PIN"
            color: app.cor_texto_muted
            size_hint_y: None
            height: dp(24)

        Widget:
            size_hint_y: None
            height: dp(10)

        PBInput:
            id: campo_pin
            hint_text: "PIN"
            password: True
            input_filter: "int"
            halign: "center"

        PBButton:
            text: "Entrar"
            on_release: root.entrar()

        PBSecondaryButton:
            text: "Usar e-mail e senha"
            on_release: root.usar_login()

        Widget:

<CriarPinScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Configurar PIN"
                color: app.cor_texto
                bold: True
                font_size: "18sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        Label:
            text: "Crie um PIN de pelo menos 4 números pra entrar mais rápido da próxima vez, sem digitar e-mail e senha."
            color: app.cor_texto_muted
            size_hint_y: None
            height: dp(60)
            halign: "left"
            text_size: self.width, None

        PBInput:
            id: campo_pin
            hint_text: "Novo PIN"
            password: True
            input_filter: "int"

        PBInput:
            id: campo_pin_confirma
            hint_text: "Confirme o PIN"
            password: True
            input_filter: "int"

        PBButton:
            text: "Salvar PIN"
            on_release: root.salvar()

        Widget:

<AvisosScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Avisos"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        PBButton:
            id: botao_novo_aviso
            text: "+ Novo aviso"
            size_hint_y: None
            height: dp(0)
            opacity: 0
            disabled: True
            on_release: root.ir_novo_aviso()

        ScrollView:
            BoxLayout:
                id: lista_avisos
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)

<NovoAvisoScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Novo aviso"
                color: app.cor_texto
                bold: True
                font_size: "18sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        PBInput:
            id: campo_titulo
            hint_text: "Título"

        PBInput:
            id: campo_mensagem
            hint_text: "Mensagem"
            size_hint_y: None
            height: dp(120)
            multiline: True

        PBButton:
            text: "Publicar"
            on_release: root.publicar()

<TrocarSenhaScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Trocar senha"
                color: app.cor_texto
                bold: True
                font_size: "18sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        PBInput:
            id: campo_senha
            hint_text: "Nova senha (mínimo 6 caracteres)"
            password: True

        PBInput:
            id: campo_senha_confirma
            hint_text: "Confirme a nova senha"
            password: True

        PBButton:
            text: "Salvar nova senha"
            on_release: root.salvar()

        Widget:

<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)

        Widget:
            size_hint_y: None
            height: dp(40)

        Label:
            text: "Ipoint"
            color: app.cor_ciano
            bold: True
            font_size: "30sp"
            size_hint_y: None
            height: dp(44)

        Label:
            text: "Entre com sua conta"
            color: app.cor_texto_muted
            size_hint_y: None
            height: dp(24)

        Widget:
            size_hint_y: None
            height: dp(10)

        PBInput:
            id: campo_email
            hint_text: "E-mail"
            input_type: "mail"

        PBInput:
            id: campo_senha
            hint_text: "Senha"
            password: True

        PBButton:
            text: "Entrar"
            on_release: root.entrar()

        PBSecondaryButton:
            text: "Criar conta nova"
            on_release: root.ir_registro()

        PBSecondaryButton:
            text: "Esqueci minha senha"
            on_release: root.esqueci_senha()

        Widget:

<RegisterScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)

        TopBar:
            PBSecondaryButton:
                text: "< Voltar"
                size_hint_x: None
                width: dp(90)
                on_release: root.voltar()
            Label:
                text: "Criar conta"
                color: app.cor_texto
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
                text_size: self.size

        PBInput:
            id: campo_email
            hint_text: "E-mail"
            input_type: "mail"

        PBInput:
            id: campo_senha
            hint_text: "Senha (mínimo 6 caracteres)"
            password: True

        PBInput:
            id: campo_senha_confirma
            hint_text: "Confirme a senha"
            password: True

        PBButton:
            text: "Registrar"
            on_release: root.registrar()

        Widget:
"""


def fmt(valor):
    """Formata número no padrão brasileiro: 1.234,56"""
    s = f"{valor:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def parse_valor(texto):
    """Converte texto digitado (aceita vírgula ou ponto) em float."""
    texto = (texto or "").strip().replace(".", "").replace(",", ".")
    if texto.count(".") > 1:
        # se sobrou mais de um ponto (ex: usuário digitou 1.234.56 estranho), pega só o último
        partes = texto.split(".")
        texto = "".join(partes[:-1]) + "." + partes[-1]
    return float(texto)


def popup_erro(mensagem):
    from kivy.graphics import Color, RoundedRectangle
    box = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(14))

    def redraw(*_):
        box.canvas.before.clear()
        with box.canvas.before:
            Color(*COR_CARD)
            RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(20)])

    box.bind(pos=redraw, size=redraw)
    lbl = Label(text=mensagem, color=COR_TEXTO, halign="center", valign="middle")
    lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    box.add_widget(lbl)
    btn = Button(text="OK", size_hint_y=None, height=dp(46),
                 background_normal="", background_color=(0, 0, 0, 0),
                 color=(0.02, 0.06, 0.10, 1), bold=True)

    def redraw_btn(*_):
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*COR_CIANO)
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(20)])

    btn.bind(pos=redraw_btn, size=redraw_btn)
    box.add_widget(btn)
    pop = Popup(title="", content=box, size_hint=(0.82, 0.36),
                separator_height=0, background="", background_color=(0, 0, 0, 0))
    btn.bind(on_release=pop.dismiss)
    pop.open()


class LinhaClicavel(ButtonBehavior, BoxLayout):
    """BoxLayout que também dispara on_release, tipo um botão — usado nas listas."""
    pass


class SpinnerCarregando(Image):
    angulo = NumericProperty(0)


class BootScreen(Screen):
    def on_enter(self, *args):
        spinner = self.ids.spinner_boot
        anim = Animation(angulo=360, duration=1.1)
        anim.repeat = True
        anim.start(spinner)
        self._anim = anim
        Clock.schedule_once(self._seguir, 1.3)

    def _seguir(self, *args):
        if hasattr(self, "_anim"):
            self._anim.cancel(self.ids.spinner_boot)
        self.manager.current = "pin" if db.tem_pin_configurado() else "login"


def _popup_carregando():
    box = BoxLayout(padding=dp(24))
    spinner = SpinnerCarregando(size_hint=(None, None), size=(dp(90), dp(90)),
                                 pos_hint={"center_x": 0.5, "center_y": 0.5})
    box.add_widget(spinner)
    pop = Popup(title="", content=box, size_hint=(0.5, 0.28), separator_height=0,
                background="", background_color=(0, 0, 0, 0), auto_dismiss=False)
    anim = Animation(angulo=360, duration=1.1)
    anim.repeat = True
    anim.start(spinner)
    pop._anim = anim
    pop._spinner = spinner
    pop.open()
    return pop


def _fechar_carregando(pop):
    pop._anim.cancel(pop._spinner)
    pop.dismiss()


def _rodar_em_segundo_plano(tarefa, ao_terminar):
    """Roda `tarefa` (sem argumentos) numa thread separada, mostrando o spinner,
    e chama `ao_terminar(erro)` na thread principal quando acabar (erro=None se deu certo)."""
    pop = _popup_carregando()

    def trabalhar():
        erro = None
        try:
            tarefa()
        except db.ApiError as e:
            erro = str(e)
        except Exception as e:
            erro = f"Erro inesperado: {e}"

        def finalizar(*_):
            _fechar_carregando(pop)
            ao_terminar(erro)

        Clock.schedule_once(finalizar, 0)

    threading.Thread(target=trabalhar, daemon=True).start()


class HomeScreen(Screen):
    nome_conta_atual = StringProperty("Minha Conta")
    saldo_formatado = StringProperty("0,00")

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        try:
            contas = db.listar_contas()
        except db.ApiError as e:
            popup_erro(str(e))
            return
        if not contas:
            return
        if app.conta_atual_id is None or not any(c["id"] == app.conta_atual_id for c in contas):
            app.conta_atual_id = contas[0]["id"]
        conta_atual = next(c for c in contas if c["id"] == app.conta_atual_id)
        self.nome_conta_atual = conta_atual["nome"]
        self.saldo_formatado = fmt(conta_atual["saldo"])

        lista = self.ids.lista_contas
        lista.clear_widgets()
        for c in contas:
            item = self._linha_conta(c)
            lista.add_widget(item)

    def _rotulo_categoria(self, categoria):
        rotulos = {
            "investimento": "[Investimento] ",
            "porquinho": "[Porquinho] ",
            "emprestimo": "[Empréstimo] ",
        }
        return rotulos.get((categoria or "comum").lower(), "")

    def _cor_categoria(self, categoria):
        cores = {
            "comum": COR_CAT_COMUM,
            "investimento": COR_CAT_INVESTIMENTO,
            "porquinho": COR_CAT_PORQUINHO,
            "emprestimo": COR_CAT_EMPRESTIMO,
        }
        return cores.get((categoria or "comum").lower(), COR_CAT_COMUM)

    def _linha_conta(self, conta):
        app = App.get_running_app()
        box = LinhaClicavel(
            orientation="horizontal",
            padding=[dp(14), 0],
            size_hint_y=None,
            height=dp(56),
        )
        from kivy.graphics import Color, RoundedRectangle

        def redraw(*_):
            box.canvas.before.clear()
            with box.canvas.before:
                is_atual = conta["id"] == app.conta_atual_id
                Color(*(COR_CARD_CLARO if is_atual else COR_CARD))
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(20)])

        box.bind(pos=redraw, size=redraw)
        nome_lbl = Label(text=self._rotulo_categoria(conta["categoria"]) + conta["nome"],
                          color=COR_TEXTO, halign="left",
                          valign="middle", bold=(conta["id"] == app.conta_atual_id),
                          shorten=True, shorten_from="right")
        nome_lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        saldo_lbl = Label(text=fmt(conta["saldo"]) + " pts", color=self._cor_categoria(conta["categoria"]),
                           halign="right", valign="middle", bold=True,
                           size_hint_x=None, width=dp(110))
        saldo_lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        box.add_widget(nome_lbl)
        box.add_widget(saldo_lbl)

        def selecionar(*_):
            app.conta_atual_id = conta["id"]
            self.refresh()

        box.bind(on_release=selecionar)
        return box

    def ir_transferir(self):
        self.manager.current = "transferir"

    def ir_extrato(self):
        self.manager.current = "extrato"

    def ir_nova_conta(self):
        self.manager.current = "nova_conta"

    def ir_depositar(self):
        self.manager.current = "depositar"

    def ir_menu(self):
        self.manager.current = "menu"

    def ir_chave(self):
        self.manager.current = "chave"

    def resgatar_bonus(self):
        try:
            valor = db.resgatar_bonus_diario()
        except db.ApiError as e:
            popup_erro(str(e))
            return
        popup_erro(f"Você ganhou {fmt(valor)} pontos de bônus!")
        self.refresh()


class TransferirScreen(Screen):
    nome_origem = StringProperty("")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        try:
            contas = db.listar_contas()
            origem = next(c for c in contas if c["id"] == app.conta_atual_id)
            self.nome_origem = origem["nome"]
        except Exception:
            self.nome_origem = ""

    def confirmar(self):
        email_destino = self.ids.campo_email_destino.text.strip()
        campo = self.ids.campo_valor
        if not email_destino:
            popup_erro("Digite o e-mail de quem vai receber.")
            return
        try:
            valor = parse_valor(campo.text)
        except ValueError:
            popup_erro("Digite um valor válido.")
            return
        try:
            db.transferir_para_destino(email_destino, valor)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        self.ids.campo_email_destino.text = ""
        campo.text = ""
        self.manager.current = "home"

    def voltar(self):
        self.manager.current = "home"


class ExtratoScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        try:
            transacoes = db.extrato(app.conta_atual_id)
        except db.ApiError as e:
            popup_erro(str(e))
            transacoes = []
        lista = self.ids.lista_extrato
        lista.clear_widgets()
        if not transacoes:
            lbl = Label(text="Nenhuma movimentação ainda.", color=COR_TEXTO_MUTED,
                        size_hint_y=None, height=dp(40))
            lista.add_widget(lbl)
            return
        for t in transacoes:
            lista.add_widget(self._linha(t))

    def _linha(self, t):
        from kivy.graphics import Color, RoundedRectangle
        box = BoxLayout(padding=[dp(14), dp(8)], size_hint_y=None, height=dp(62),
                         orientation="horizontal")

        def redraw(*_):
            box.canvas.before.clear()
            with box.canvas.before:
                Color(*COR_CARD)
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(18)])

        box.bind(pos=redraw, size=redraw)

        info = BoxLayout(orientation="vertical")
        desc = Label(text=t["descricao"] or "Movimentação", color=COR_TEXTO, halign="left",
                     valign="middle", bold=True, font_size="14sp")
        desc.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        data = Label(text=t["data"][:16].replace("T", " "), color=COR_TEXTO_MUTED,
                     halign="left", valign="middle", font_size="11sp")
        data.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        info.add_widget(desc)
        info.add_widget(data)

        sinal = "+" if t["tipo"] == "entrada" else "-"
        cor = COR_ENTRADA if t["tipo"] == "entrada" else COR_SAIDA
        valor_lbl = Label(text=f"{sinal} {fmt(t['valor'])}", color=cor, bold=True,
                           halign="right", valign="middle", size_hint_x=None, width=dp(110))
        valor_lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        box.add_widget(info)
        box.add_widget(valor_lbl)
        return box

    def voltar(self):
        self.manager.current = "home"


class NovaContaScreen(Screen):
    def criar(self):
        nome = self.ids.campo_nome.text.strip()
        if not nome:
            popup_erro("Digite um nome para a conta.")
            return
        saldo_txt = self.ids.campo_saldo.text.strip()
        try:
            saldo = parse_valor(saldo_txt) if saldo_txt else 0.0
        except ValueError:
            popup_erro("Saldo inicial inválido.")
            return
        categoria_map = {"Comum": "comum", "Investimento": "investimento", "Porquinho": "porquinho", "Empréstimo": "emprestimo"}
        categoria = categoria_map.get(self.ids.spinner_categoria.text, "comum")
        try:
            novo_id = db.criar_conta(nome, saldo, categoria)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        App.get_running_app().conta_atual_id = novo_id
        self.ids.campo_nome.text = ""
        self.ids.campo_saldo.text = ""
        self.ids.spinner_categoria.text = "Comum"
        self.manager.current = "home"

    def voltar(self):
        self.manager.current = "home"


class DepositarScreen(Screen):
    nome_conta_atual = StringProperty("")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        try:
            conta = db.obter_conta(app.conta_atual_id)
        except db.ApiError:
            conta = None
        self.nome_conta_atual = conta["nome"] if conta else ""

    def confirmar(self):
        app = App.get_running_app()
        try:
            valor = parse_valor(self.ids.campo_valor.text)
        except ValueError:
            popup_erro("Digite um valor válido.")
            return
        desc = self.ids.campo_desc.text.strip() or "Depósito"
        try:
            db.depositar(app.conta_atual_id, valor, desc)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        self.ids.campo_valor.text = ""
        self.ids.campo_desc.text = ""
        self.manager.current = "home"

    def voltar(self):
        self.manager.current = "home"


class MenuScreen(Screen):
    nome_usuario = StringProperty("")

    def on_pre_enter(self, *args):
        self.nome_usuario = db.usuario_atual() or "Convidado"

    def ir_termos(self):
        self.manager.current = "termos"

    def ir_chave(self):
        self.manager.current = "chave"

    def ir_criar_pin(self):
        self.manager.current = "criar_pin"

    def ir_avisos(self):
        self.manager.current = "avisos"

    def ir_trocar_senha(self):
        self.manager.current = "trocar_senha"

    def sair(self):
        db.logout()
        db.remover_pin()
        App.get_running_app().conta_atual_id = None
        self.manager.current = "login"

    def voltar(self):
        self.manager.current = "home"


class TermosScreen(Screen):
    texto_termos = StringProperty(
        "Termos de Uso do Ipoint\n\n"
        "1. Sobre os pontos\n"
        "Os pontos utilizados neste aplicativo nao possuem qualquer valor "
        "monetario real. Eles servem apenas para uso dentro do proprio "
        "aplicativo, como forma de organizacao pessoal.\n\n"
        "2. Proibicao de troca por dinheiro real\n"
        "E estritamente proibido negociar, vender ou trocar pontos deste "
        "aplicativo por dinheiro real ou qualquer outro item de valor "
        "monetario. Qualquer pessoa que for identificada trocando pontos "
        "por dinheiro real esta sujeita a banimento do aplicativo.\n\n"
        "3. Responsabilidade\n"
        "O usuario e responsavel por manter suas informacoes de acesso em "
        "seguranca. O Ipoint nao se responsabiliza por perdas de saldo "
        "causadas por uso indevido da conta por terceiros.\n\n"
        "4. Alteracoes\n"
        "Estes termos podem ser atualizados a qualquer momento para "
        "melhor atender aos usuarios do aplicativo."
    )

    def voltar(self):
        self.manager.current = "menu"


class ChaveScreen(Screen):
    texto_chave = StringProperty("Carregando...")

    def on_pre_enter(self, *args):
        try:
            chave = db.minha_chave()
        except db.ApiError as e:
            popup_erro(str(e))
            chave = None
        self.texto_chave = chave or "Não foi possível carregar a chave."
        self._desenhar_qr(chave)

    def _desenhar_qr(self, chave):
        container = self.ids.qr_container
        container.canvas.before.clear()
        if not chave:
            return
        try:
            import qrcode
        except ImportError:
            return

        from kivy.graphics import Color, Rectangle

        qr = qrcode.QRCode(border=1, box_size=1)
        qr.add_data(chave)
        qr.make(fit=True)
        matriz = qr.get_matrix()
        n = len(matriz)

        def redraw(*_):
            container.canvas.before.clear()
            lado = min(container.width, container.height)
            if lado <= 0 or n == 0:
                return
            tam_celula = lado / n
            offset_x = container.x + (container.width - lado) / 2
            offset_y = container.y + (container.height - lado) / 2
            with container.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(pos=(offset_x, offset_y), size=(lado, lado))
                Color(0.02, 0.06, 0.10, 1)
                for linha_i, linha in enumerate(matriz):
                    for col_i, escuro in enumerate(linha):
                        if escuro:
                            x = offset_x + col_i * tam_celula
                            y = offset_y + (n - 1 - linha_i) * tam_celula
                            Rectangle(pos=(x, y), size=(tam_celula + 0.5, tam_celula + 0.5))

        container.bind(pos=redraw, size=redraw)
        redraw()

    def voltar(self):
        self.manager.current = "menu"


class PinScreen(Screen):
    def entrar(self):
        pin = self.ids.campo_pin.text.strip()
        if not pin:
            popup_erro("Digite seu PIN.")
            return

        def tarefa():
            db.entrar_com_pin(pin)

        def ao_terminar(erro):
            if erro:
                popup_erro(erro)
                return
            self.ids.campo_pin.text = ""
            App.get_running_app().conta_atual_id = None
            self.manager.current = "home"

        _rodar_em_segundo_plano(tarefa, ao_terminar)

    def usar_login(self):
        self.ids.campo_pin.text = ""
        self.manager.current = "login"


class CriarPinScreen(Screen):
    def salvar(self):
        pin = self.ids.campo_pin.text.strip()
        confirma = self.ids.campo_pin_confirma.text.strip()
        if not pin or len(pin) < 4:
            popup_erro("O PIN precisa ter pelo menos 4 números.")
            return
        if pin != confirma:
            popup_erro("Os PINs não são iguais.")
            return
        try:
            db.salvar_pin(pin)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        self.ids.campo_pin.text = ""
        self.ids.campo_pin_confirma.text = ""
        popup_erro("PIN configurado! Da próxima vez você pode entrar só com ele.")
        self.manager.current = "menu"

    def voltar(self):
        self.manager.current = "menu"


class AvisosScreen(Screen):
    def on_pre_enter(self, *args):
        botao = self.ids.botao_novo_aviso
        try:
            admin = db.sou_admin()
        except db.ApiError:
            admin = False
        if admin:
            botao.height = dp(48)
            botao.opacity = 1
            botao.disabled = False
        else:
            botao.height = 0
            botao.opacity = 0
            botao.disabled = True

        try:
            avisos = db.listar_avisos()
        except db.ApiError as e:
            popup_erro(str(e))
            avisos = []

        lista = self.ids.lista_avisos
        lista.clear_widgets()
        if not avisos:
            lista.add_widget(Label(text="Nenhum aviso por enquanto.", color=COR_TEXTO_MUTED,
                                    size_hint_y=None, height=dp(40)))
            return
        for aviso in avisos:
            lista.add_widget(self._linha_aviso(aviso))

    def _linha_aviso(self, aviso):
        from kivy.graphics import Color, RoundedRectangle
        box = BoxLayout(orientation="vertical", padding=[dp(14), dp(10)],
                         size_hint_y=None, spacing=dp(4))
        box.bind(minimum_height=box.setter("height"))

        def redraw(*_):
            box.canvas.before.clear()
            with box.canvas.before:
                Color(*COR_CARD)
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(18)])

        box.bind(pos=redraw, size=redraw)

        titulo = Label(text=aviso.get("titulo", ""), color=COR_CIANO, bold=True,
                        halign="left", valign="middle", font_size="15sp",
                        size_hint_y=None, height=dp(24))
        titulo.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        mensagem = Label(text=aviso.get("mensagem", ""), color=COR_TEXTO,
                          halign="left", valign="top", font_size="13sp",
                          size_hint_y=None, text_size=(Window.width - dp(70), None))
        mensagem.bind(texture_size=lambda w, *_: setattr(w, "height", w.texture_size[1]))

        data = Label(text=(aviso.get("criado_em") or "")[:16].replace("T", " "),
                     color=COR_TEXTO_MUTED, halign="left", valign="middle",
                     font_size="11sp", size_hint_y=None, height=dp(18))
        data.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        box.add_widget(titulo)
        box.add_widget(mensagem)
        box.add_widget(data)
        return box

    def ir_novo_aviso(self):
        self.manager.current = "novo_aviso"

    def voltar(self):
        self.manager.current = "menu"


class NovoAvisoScreen(Screen):
    def publicar(self):
        titulo = self.ids.campo_titulo.text.strip()
        mensagem = self.ids.campo_mensagem.text.strip()
        if not titulo or not mensagem:
            popup_erro("Preencha o título e a mensagem.")
            return
        try:
            db.criar_aviso(titulo, mensagem)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        self.ids.campo_titulo.text = ""
        self.ids.campo_mensagem.text = ""
        self.manager.current = "avisos"

    def voltar(self):
        self.manager.current = "avisos"


class TrocarSenhaScreen(Screen):
    def salvar(self):
        senha = self.ids.campo_senha.text
        confirma = self.ids.campo_senha_confirma.text
        if len(senha) < 6:
            popup_erro("A senha precisa ter pelo menos 6 caracteres.")
            return
        if senha != confirma:
            popup_erro("As senhas não são iguais.")
            return
        try:
            db.trocar_senha(senha)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        self.ids.campo_senha.text = ""
        self.ids.campo_senha_confirma.text = ""
        popup_erro("Senha alterada com sucesso!")
        self.manager.current = "menu"

    def voltar(self):
        self.manager.current = "menu"


class LoginScreen(Screen):
    def entrar(self):
        email = self.ids.campo_email.text.strip()
        senha = self.ids.campo_senha.text
        if not email or not senha:
            popup_erro("Preencha e-mail e senha.")
            return

        def tarefa():
            db.login(email, senha)

        def ao_terminar(erro):
            if erro:
                popup_erro(erro)
                return
            self.ids.campo_senha.text = ""
            App.get_running_app().conta_atual_id = None
            self.manager.current = "home"

        _rodar_em_segundo_plano(tarefa, ao_terminar)

    def ir_registro(self):
        self.manager.current = "registro"

    def esqueci_senha(self):
        if db.tem_pin_configurado():
            popup_erro("Entre com seu PIN nesse aparelho e troque a senha pelo Menu.")
            self.manager.current = "pin"
        else:
            popup_erro(
                "Ainda não temos recuperação por e-mail configurada. "
                "Se você tiver um PIN salvo nesse aparelho, use-o pra entrar. "
                "Sem PIN salvo, por enquanto não dá pra recuperar sozinho — "
                "me avisa que a gente configura a recuperação por e-mail."
            )


class RegisterScreen(Screen):
    def registrar(self):
        email = self.ids.campo_email.text.strip()
        senha = self.ids.campo_senha.text
        senha_confirma = self.ids.campo_senha_confirma.text
        if not email or not senha:
            popup_erro("Preencha e-mail e senha.")
            return
        if len(senha) < 6:
            popup_erro("A senha precisa ter pelo menos 6 caracteres.")
            return
        if senha != senha_confirma:
            popup_erro("As senhas não são iguais.")
            return
        try:
            logado = db.registrar(email, senha)
        except db.ApiError as e:
            popup_erro(str(e))
            return
        self.ids.campo_senha.text = ""
        self.ids.campo_senha_confirma.text = ""
        if logado:
            App.get_running_app().conta_atual_id = None
            self.manager.current = "home"
        else:
            popup_erro("Conta criada! Confirme seu e-mail antes de entrar (verifique também o spam).")
            self.manager.current = "login"

    def voltar(self):
        self.manager.current = "login"


class PontosBankApp(App):
    cor_fundo = ObjectProperty(COR_FUNDO)
    cor_card = ObjectProperty(COR_CARD)
    cor_card_claro = ObjectProperty(COR_CARD_CLARO)
    cor_ciano = ObjectProperty(COR_CIANO)
    cor_ciano_escuro = ObjectProperty(COR_CIANO_ESCURO)
    cor_texto = ObjectProperty(COR_TEXTO)
    cor_texto_muted = ObjectProperty(COR_TEXTO_MUTED)
    cor_azul_aco = ObjectProperty(COR_AZUL_ACO)
    cor_azul_profundo = ObjectProperty(COR_AZUL_PROFUNDO)
    cor_azul_medio = ObjectProperty(COR_AZUL_MEDIO)
    conta_atual_id = NumericProperty(allownone=True)

    def build(self):
        self.title = "Ipoint"
        self.conta_atual_id = None
        Builder.load_string(KV)

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(BootScreen(name="boot"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="registro"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(TransferirScreen(name="transferir"))
        sm.add_widget(ExtratoScreen(name="extrato"))
        sm.add_widget(NovaContaScreen(name="nova_conta"))
        sm.add_widget(DepositarScreen(name="depositar"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(TermosScreen(name="termos"))
        sm.add_widget(ChaveScreen(name="chave"))
        sm.add_widget(PinScreen(name="pin"))
        sm.add_widget(CriarPinScreen(name="criar_pin"))
        sm.add_widget(AvisosScreen(name="avisos"))
        sm.add_widget(NovoAvisoScreen(name="novo_aviso"))
        sm.add_widget(TrocarSenhaScreen(name="trocar_senha"))
        sm.current = "boot"
        return sm


if __name__ == "__main__":
    PontosBankApp().run()
