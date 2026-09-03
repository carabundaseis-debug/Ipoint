"""
Ipoint — um "banco" de pontos (não dinheiro de verdade).
App Android feito em Kivy. Toda a lógica de dados está em db.py.
"""
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.core.window import Window

import db

# ---------------------------------------------------------------------------
# Paleta de cores — azul escuro + ciano
# ---------------------------------------------------------------------------
COR_FUNDO = (0.039, 0.086, 0.157, 1)        # #0A1628 fundo geral
COR_CARD = (0.063, 0.165, 0.275, 1)          # #102A46 cartões
COR_CARD_CLARO = (0.09, 0.22, 0.35, 1)       # cartões/itens de lista
COR_CIANO = (0.0, 0.851, 1.0, 1)             # #00D9FF destaque
COR_CIANO_ESCURO = (0.0, 0.72, 0.83, 1)      # botões pressionados
COR_TEXTO = (0.92, 0.96, 1.0, 1)
COR_TEXTO_MUTED = (0.60, 0.70, 0.78, 1)
COR_ENTRADA = (0.30, 0.95, 0.75, 1)          # verde-ciano p/ entradas
COR_SAIDA = (1.0, 0.42, 0.42, 1)             # vermelho p/ saídas

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
            radius: [dp(18)]
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
            radius: [dp(12)]

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
            rgba: app.cor_card_claro
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<PBInput@TextInput>:
    background_normal: ""
    background_active: ""
    background_color: app.cor_card_claro
    foreground_color: app.cor_texto
    hint_text_color: app.cor_texto_muted
    cursor_color: app.cor_ciano
    padding: [dp(14), dp(14)]
    size_hint_y: None
    height: dp(48)
    multiline: False

<TopBar@BoxLayout>:
    size_hint_y: None
    height: dp(56)
    spacing: dp(8)
    padding: [dp(4), 0]

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)

        TopBar:
            Label:
                text: "Ipoint"
                color: app.cor_texto
                bold: True
                font_size: "22sp"
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

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(10)
            PBButton:
                text: "Transferir"
                on_release: root.ir_transferir()
            PBButton:
                text: "Extrato"
                on_release: root.ir_extrato()

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(10)
            PBSecondaryButton:
                text: "+ Depositar"
                on_release: root.ir_depositar()
            PBSecondaryButton:
                text: "+ Nova conta"
                on_release: root.ir_nova_conta()

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
            height: dp(230)
            Label:
                text: "De: " + root.nome_origem
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(24)
                halign: "left"
                text_size: self.size
            Label:
                text: "Para"
                color: app.cor_texto_muted
                size_hint_y: None
                height: dp(20)
                halign: "left"
                text_size: self.size
            Spinner:
                id: spinner_destino
                text: root.nome_destino
                values: root.opcoes_destino
                size_hint_y: None
                height: dp(44)
                background_normal: ""
                background_color: app.cor_card_claro
                color: app.cor_texto
                on_text: root.selecionar_destino(self.text)
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
                input_filter: "float"

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
            height: dp(180)
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
                input_filter: "float"
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
                input_filter: "float"
            PBInput:
                id: campo_desc
                hint_text: "Descrição (opcional)"
        PBButton:
            text: "Confirmar depósito"
            on_release: root.confirmar()
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
    box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    box.add_widget(Label(text=mensagem, color=COR_TEXTO))
    btn = Button(text="OK", size_hint_y=None, height=dp(44),
                 background_normal="", background_color=COR_CIANO, color=(0.02, 0.06, 0.10, 1))
    box.add_widget(btn)
    pop = Popup(title="Ops", content=box, size_hint=(0.8, 0.35),
                background_color=COR_CARD, separator_color=COR_CIANO)
    btn.bind(on_release=pop.dismiss)
    pop.open()


class HomeScreen(Screen):
    nome_conta_atual = StringProperty("Minha Conta")
    saldo_formatado = StringProperty("0,00")

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        contas = db.listar_contas()
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

    def _linha_conta(self, conta):
        app = App.get_running_app()
        linha = Button(
            size_hint_y=None,
            height=dp(56),
            background_normal="",
            background_color=(0, 0, 0, 0),
            halign="left",
        )
        box = BoxLayout(padding=[dp(14), 0], size_hint_y=None, height=dp(56))
        from kivy.graphics import Color, RoundedRectangle

        def redraw(*_):
            box.canvas.before.clear()
            with box.canvas.before:
                is_atual = conta["id"] == app.conta_atual_id
                Color(*(COR_CARD_CLARO if is_atual else COR_CARD))
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(14)])

        box.bind(pos=redraw, size=redraw)
        nome_lbl = Label(text=conta["nome"], color=COR_TEXTO, halign="left",
                          valign="middle", bold=(conta["id"] == app.conta_atual_id))
        nome_lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        saldo_lbl = Label(text=fmt(conta["saldo"]) + " pts", color=COR_CIANO,
                           halign="right", valign="middle")
        saldo_lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        box.add_widget(nome_lbl)
        box.add_widget(saldo_lbl)

        def selecionar(*_):
            app.conta_atual_id = conta["id"]
            self.refresh()

        wrapper = Button(size_hint_y=None, height=dp(56), background_normal="",
                          background_color=(0, 0, 0, 0))
        wrapper.add_widget(box)
        wrapper.bind(on_release=selecionar)
        return wrapper

    def ir_transferir(self):
        self.manager.current = "transferir"

    def ir_extrato(self):
        self.manager.current = "extrato"

    def ir_nova_conta(self):
        self.manager.current = "nova_conta"

    def ir_depositar(self):
        self.manager.current = "depositar"


class TransferirScreen(Screen):
    nome_origem = StringProperty("")
    nome_destino = StringProperty("")
    opcoes_destino = ObjectProperty([])
    destino_id = NumericProperty(0)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        contas = db.listar_contas()
        origem = next(c for c in contas if c["id"] == app.conta_atual_id)
        self.nome_origem = origem["nome"]
        outras = [c for c in contas if c["id"] != app.conta_atual_id]
        self._mapa = {c["nome"]: c["id"] for c in outras}
        self.opcoes_destino = list(self._mapa.keys())
        if outras:
            self.nome_destino = outras[0]["nome"]
            self.destino_id = outras[0]["id"]
        else:
            self.nome_destino = "Crie outra conta primeiro"
            self.destino_id = 0

    def selecionar_destino(self, nome):
        if nome in self._mapa:
            self.destino_id = self._mapa[nome]

    def confirmar(self):
        app = App.get_running_app()
        campo = self.ids.campo_valor
        if not self.destino_id:
            popup_erro("Crie outra conta antes de transferir.")
            return
        try:
            valor = parse_valor(campo.text)
        except ValueError:
            popup_erro("Digite um valor válido.")
            return
        try:
            db.transferir(app.conta_atual_id, self.destino_id, valor)
        except ValueError as e:
            popup_erro(str(e))
            return
        campo.text = ""
        self.manager.current = "home"

    def voltar(self):
        self.manager.current = "home"


class ExtratoScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        transacoes = db.extrato(app.conta_atual_id)
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
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(12)])

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
        novo_id = db.criar_conta(nome, saldo)
        App.get_running_app().conta_atual_id = novo_id
        self.ids.campo_nome.text = ""
        self.ids.campo_saldo.text = ""
        self.manager.current = "home"

    def voltar(self):
        self.manager.current = "home"


class DepositarScreen(Screen):
    nome_conta_atual = StringProperty("")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        conta = db.obter_conta(app.conta_atual_id)
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
        except ValueError as e:
            popup_erro(str(e))
            return
        self.ids.campo_valor.text = ""
        self.ids.campo_desc.text = ""
        self.manager.current = "home"

    def voltar(self):
        self.manager.current = "home"


class PontosBankApp(App):
    cor_fundo = ObjectProperty(COR_FUNDO)
    cor_card = ObjectProperty(COR_CARD)
    cor_card_claro = ObjectProperty(COR_CARD_CLARO)
    cor_ciano = ObjectProperty(COR_CIANO)
    cor_ciano_escuro = ObjectProperty(COR_CIANO_ESCURO)
    cor_texto = ObjectProperty(COR_TEXTO)
    cor_texto_muted = ObjectProperty(COR_TEXTO_MUTED)
    conta_atual_id = NumericProperty(allownone=True)

    def build(self):
        self.title = "Ipoint"
        self.conta_atual_id = None
        Builder.load_string(KV)
        db.init_db()

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(TransferirScreen(name="transferir"))
        sm.add_widget(ExtratoScreen(name="extrato"))
        sm.add_widget(NovaContaScreen(name="nova_conta"))
        sm.add_widget(DepositarScreen(name="depositar"))
        return sm


if __name__ == "__main__":
    PontosBankApp().run()
