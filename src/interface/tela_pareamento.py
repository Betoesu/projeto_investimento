"""Tela inicial: guia passo a passo em texto + botão "Estou Pronto"."""

import tkinter as tk
import customtkinter as ctk
from . import tema

PASSOS = [
    {
        "num": "1",
        "titulo": "Abrir o Perfil",
        "desc": "No aplicativo do Inter, toque no ícone de perfil no canto superior esquerdo da tela inicial.",
    },
    {
        "num": "2",
        "titulo": "Token e Autorização",
        "desc": 'Role até a seção "Central de Segurança" e toque em "Token e Autorização".',
    },
    {
        "num": "3",
        "titulo": "Acessar via QR Code",
        "desc": 'Toque em "Acessar via QR Code", confirme o site e pressione "Ler o QR Code".',
    },
]

class TelaPareamento(ctk.CTkFrame):
    """Tela de pareamento dividida em Topo (fixo), Meio (rolável) e Base (fixo)."""

    def __init__(self, master, on_pronto=None, **kwargs):
        super().__init__(master, fg_color=tema.BG, corner_radius=0, **kwargs)
        self.on_pronto = on_pronto
        self._montar()

    def _montar(self):
        # ── 1. TOPO FIXO ──────────────────────────────────────────────
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(side="top", fill="x", padx=28, pady=(28, 0))

        ctk.CTkLabel(
            topo, text="Painel de Investimentos", font=tema.FONTE_TITULO, text_color=tema.TEXTO_PRIMARIO
        ).pack(side="left")

        self._badge = ctk.CTkLabel(
            topo, text="● Aguardando", font=tema.FONTE_LEGENDA, text_color=tema.TEXTO_MUTED
        )
        self._badge.pack(side="right")

        tk.Frame(self, bg=tema.BORDA, height=1).pack(side="top", fill="x", padx=28, pady=(16, 0))

        header_textos = ctk.CTkFrame(self, fg_color="transparent")
        header_textos.pack(side="top", fill="x", padx=28)
        
        ctk.CTkLabel(
            header_textos, text="Como acessar o QR Code no Inter", font=("Segoe UI", 13, "bold"), text_color=tema.TEXTO_PRIMARIO
        ).pack(anchor="w", pady=(24, 4))
        
        ctk.CTkLabel(
            header_textos, text='Siga os passos abaixo no aplicativo antes de clicar em "Estou Pronto".', font=tema.FONTE_SUBTITULO, text_color=tema.TEXTO_SECUNDARIO, justify="left"
        ).pack(anchor="w", pady=(0, 10))


        # ── 3. BASE FIXA (Ações) ───────────────────────────────────────
        base = ctk.CTkFrame(self, fg_color="transparent")
        base.pack(side="bottom", fill="x", padx=28, pady=(0, 5))

        self._status_label = ctk.CTkLabel(
            base, text="", font=tema.FONTE_LEGENDA, text_color=tema.TEXTO_MUTED
        )
        self._status_label.pack(side="bottom", pady=(8, 0))

        self.botao = ctk.CTkButton(
            base, text="Estou Pronto — Iniciar Leitura", font=("Segoe UI", 13, "bold"),
            fg_color=tema.ACCENT_BG, text_color=tema.ACCENT, hover_color="#1A3D2E",
            corner_radius=8, height=44, command=self._clicar_pronto
        )
        self.botao.pack(side="bottom", fill="x", pady=(16, 0))

        tk.Frame(base, bg=tema.BORDA, height=1).pack(side="bottom", fill="x")


        # ── 2. MEIO ROLÁVEL (Conteúdo Dinâmico) ────────────────────────
        # Ocupa todo o espaço que sobrou entre o Topo e a Base
        self._corpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._corpo.pack(side="top", fill="both", expand=True, padx=14)

        for passo in PASSOS:
            self._cartao_passo(passo)

    def _cartao_passo(self, passo):
        # Cartão com padding externo minúsculo (pady=4)
        cartao = ctk.CTkFrame(
            self._corpo, fg_color=tema.CARD_BG, corner_radius=6, border_width=1, border_color=tema.BORDA
        )
        cartao.pack(fill="x", padx=14, pady=(0, 4)) 

        # Bolinha do Número (Agora inserida direto no cartão, sem o frame "esq")
        num_lbl = ctk.CTkLabel(
            cartao, text=passo["num"], font=("Segoe UI", 12, "bold"),
            text_color=tema.ACCENT, fg_color=tema.ACCENT_BG, 
            corner_radius=12, width=24, height=24
        )
        num_lbl.pack(side="left", padx=(8, 8), pady=4)

        # Divisória mais fina
        tk.Frame(cartao, bg=tema.BORDA, width=1).pack(side="left", fill="y", pady=4)

        # Textos colados na divisória
        dir_ = ctk.CTkFrame(cartao, fg_color="transparent")
        dir_.pack(side="left", fill="both", expand=True, padx=8, pady=4)

        ctk.CTkLabel(
            dir_, text=passo["titulo"], font=("Segoe UI", 12, "bold"), text_color=tema.TEXTO_PRIMARIO, anchor="w"
        ).pack(fill="x")

        # Usando a FONTE_LEGENDA para ocupar menos espaço vertical na descrição
        ctk.CTkLabel(
            dir_, text=passo["desc"], font=tema.FONTE_LEGENDA, text_color=tema.TEXTO_SECUNDARIO,
            anchor="w", justify="left", wraplength=540
        ).pack(fill="x")

    def _clicar_pronto(self):
        self.botao.configure(state="disabled", text="Aguardando leitura do QR Code...")
        self._badge.configure(text="● Conectando", text_color=tema.ACCENT)
        self._status_label.configure(
            text="Mantenha o aplicativo do banco aberto até a confirmação."
        )
        if self.on_pronto:
            self.on_pronto()

    def restaurar(self):
        self.botao.configure(state="normal", text="Estou Pronto — Iniciar Leitura")
        self._badge.configure(text="● Aguardando", text_color=tema.TEXTO_MUTED)
        self._status_label.configure(text="")

    def atualizar_status(self, mensagem):
        """Atualiza a mensagem de texto abaixo do botão."""
        self._status_label.configure(text=mensagem)