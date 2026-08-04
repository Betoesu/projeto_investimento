"""Tela de carregamento com barra de progresso e checklist de etapas."""

import tkinter as tk
import customtkinter as ctk
from . import tema

class TelaCarregamento(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=tema.BG, corner_radius=0, **kwargs)
        self.labels_etapas = []
        self._montar()

    def _montar(self):
        # Container centralizado para não parecer vazio
        meio = ctk.CTkFrame(self, fg_color="transparent")
        meio.pack(expand=True, fill="both", padx=80, pady=80)

        ctk.CTkLabel(
            meio, text="Sincronizando Dados", font=("Segoe UI", 24, "bold"), text_color=tema.TEXTO_PRIMARIO
        ).pack(anchor="w")

        ctk.CTkLabel(
            meio, text="O robô está trabalhando nos bastidores. Acompanhe o progresso.", 
            font=tema.FONTE_CORPO, text_color=tema.TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(4, 28))

        # Barra de Progresso
        self.barra = ctk.CTkProgressBar(
            meio, height=12, corner_radius=6, fg_color=tema.BORDA, progress_color=tema.ACCENT
        )
        self.barra.pack(fill="x", pady=(0, 24))
        self.barra.set(0) # Inicia vazia (0.0 até 1.0)

        # Cartão para agrupar o Checklist
        cartao_etapas = ctk.CTkFrame(
            meio, fg_color=tema.CARD_BG, corner_radius=12, border_width=1, border_color=tema.BORDA
        )
        cartao_etapas.pack(fill="x")

        # Lista de passos
        etapas = [
            "1. Acessando painel de Renda Fixa",
            "2. Aplicando filtros de investimento",
            "3. Extraindo e processando dados",
        ]

        for i, texto in enumerate(etapas):
            # Cria a linha da etapa
            linha = ctk.CTkFrame(cartao_etapas, fg_color="transparent")
            linha.pack(fill="x", padx=20, pady=16)
            
            lbl = ctk.CTkLabel(
                linha, text=texto, font=tema.FONTE_CORPO, text_color=tema.TEXTO_MUTED
            )
            lbl.pack(side="left")
            self.labels_etapas.append(lbl)

            # Adiciona divisória entre as etapas (exceto na última)
            if i < len(etapas) - 1:
                tk.Frame(cartao_etapas, bg=tema.BORDA, height=1).pack(fill="x", padx=20)

    def atualizar_etapa(self, indice_etapa, porcentagem):
        """Atualiza a barra de progresso e pinta a etapa atual de verde."""
        self.barra.set(porcentagem)

        for i, lbl in enumerate(self.labels_etapas):
            if i < indice_etapa:
                # Etapas já concluídas
                lbl.configure(text_color=tema.TEXTO_PRIMARIO, font=("Segoe UI", 13))
            elif i == indice_etapa:
                # Etapa atual em destaque
                lbl.configure(text_color=tema.ACCENT, font=("Segoe UI", 13, "bold"))
            else:
                # Etapas futuras
                lbl.configure(text_color=tema.TEXTO_MUTED, font=("Segoe UI", 13))