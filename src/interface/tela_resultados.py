"""Tela de resultados: tabela de produtos + exportar TXT + copiar."""

import datetime
import os
import tkinter as tk

import customtkinter as ctk

from . import tema

CAMPOS = [
    # Aumentamos o peso do produto e demos mais espaço para as colunas finais
    ("produto",            "Produto",       5), 
    ("rendimento",         "Rendimento",    3),
    ("investimento_minimo","Inv. Mínimo",   3),
    ("isento_ir",          "Isento IR",     3), 
    ("vencimento",         "Vencimento",    4), 
]


def _formatar_txt(investimentos):
    """Gera o texto no mesmo estilo que o main.py já exporta."""
    linhas = []
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linhas.append("=" * 68)
    linhas.append(f"  PAINEL DE INVESTIMENTOS — Renda Fixa · {agora}")
    linhas.append("=" * 68)
    for item in investimentos:
        isento = "Sim" if str(item.get("isento_ir", "")).strip().lower() in (
            "sim", "true", "isento") else "Não"
        linhas.append(
            f"  {item.get('produto', '-'):<30} "
            f"Taxa: {item.get('rendimento', '-'):<16} "
            f"Mín: {item.get('investimento_minimo', '-'):<12} "
            f"IR: {isento:<4} "
            f"Venc: {item.get('vencimento', '-')}"
        )
    linhas.append("=" * 68)
    return "\n".join(linhas)


class TelaResultados(ctk.CTkFrame):
    """Cabeçalho + tabela rolável + barra de ações."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=tema.BG, corner_radius=0, **kwargs)

        self.winfo_toplevel().geometry("1200x700")

        self._dados = []
        self._montar()

    # ── Construção da UI ─────────────────────────────────────────────

    def _montar(self):
        # Cabeçalho
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=28, pady=(24, 0))

        ctk.CTkLabel(
            topo,
            text="Painel de Investimentos",
            font=tema.FONTE_TITULO,
            text_color=tema.TEXTO_PRIMARIO,
        ).pack(side="left")

        self._pill = ctk.CTkLabel(
            topo,
            text="0 Produtos Encontrados",
            font=tema.FONTE_LEGENDA,
            text_color=tema.ACCENT,
            fg_color=tema.ACCENT_BG,
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self._pill.pack(side="right")

        sep = tk.Frame(self, bg=tema.BORDA, height=1)
        sep.pack(fill="x", padx=28, pady=(12, 0))

        # Cartão da tabela
        self._cartao = ctk.CTkFrame(self, fg_color=tema.CARD_BG, corner_radius=12)
        self._cartao.pack(fill="both", expand=True, padx=28, pady=(16, 0))
        cartao = self._cartao

        cartao.grid_columnconfigure(0, weight=1)
        cartao.grid_rowconfigure(1, weight=1)
        cartao.grid_rowconfigure(0, minsize=48)

        # Cabeçalho da tabela.
        # Fica num tk.Frame próprio (padx em pixels reais) e usa as MESMAS colunas
        # (pesos + uniform) das linhas de dados. Assim cada título fica exatamente
        # acima da sua coluna. A faixa horizontal é ajustada em _alinhar_cabecalho.
        self._cab = tk.Frame(cartao, bg=tema.CARD_BG, highlightthickness=0, bd=0)
        self._cab.grid(row=0, column=0, sticky="nsew")

        for i, (_, rotulo, peso) in enumerate(CAMPOS):
            self._cab.grid_columnconfigure(i, weight=peso, uniform="cols")
            ctk.CTkLabel(
                self._cab,
                text=rotulo,
                font=tema.FONTE_TABELA_H,
                text_color=tema.TEXTO_MUTED,
                anchor="w",
                width=0,
            ).grid(row=0, column=i, sticky="ew", padx=12, pady=(16, 14))

        # Linha separadora (South, East, West: cola no fundo da linha 0)
        sep2 = tk.Frame(cartao, bg=tema.BORDA, height=1)
        sep2.grid(row=0, column=0, sticky="sew", padx=12, pady=0)

        self._tabela = ctk.CTkScrollableFrame(cartao, fg_color="transparent")
        self._tabela.grid(row=1, column=0, sticky="nsew", pady=(4, 8))

        # Mesmas colunas do cabeçalho
        for i, (_, _, peso) in enumerate(CAMPOS):
            self._tabela.grid_columnconfigure(i, weight=peso, uniform="cols")

        # Mantém o cabeçalho alinhado quando a janela muda de tamanho
        self._cab_padx = None
        self._tabela.bind("<Configure>", self._alinhar_cabecalho, add="+")
        cartao.bind("<Configure>", self._alinhar_cabecalho, add="+")

       # ── Barra de ações ────────────────────────────────────────────
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=28, pady=(12, 28))

        self._btn_txt = ctk.CTkButton(
            barra, text="⬇  Exportar TXT", font=tema.FONTE_CORPO,
            fg_color="transparent", text_color=tema.TEXTO_PRIMARIO,
            hover_color=tema.CARD_BG_HOVER, border_width=1,
            border_color=tema.BORDA_FORTE, corner_radius=6, height=36,
            command=self._exportar_txt,
        )
        self._btn_txt.pack(side="left", padx=(0, 12))

        self._btn_copy = ctk.CTkButton(
            barra, text="⎘  Copiar para Área de Transferência",
            font=("Segoe UI", 13, "bold"), fg_color=tema.ACCENT_BG,
            text_color=tema.ACCENT, hover_color="#1A3D2E", border_width=0,
            corner_radius=6, height=36, command=self._copiar,
        )
        self._btn_copy.pack(side="left")

        self._msg = ctk.CTkLabel(
            barra, text="", font=tema.FONTE_LEGENDA, text_color=tema.ACCENT
        )
        self._msg.pack(side="right", padx=(8, 0))

    # ── Dados ────────────────────────────────────────────────────────

    def atualizar_dados(self, investimentos):
        """Redesenha a tabela. Chame antes de exibir esta tela."""
        self._dados = investimentos
        for w in self._tabela.winfo_children():
            w.destroy()

        qtd = len(investimentos)
        self._pill.configure(
            text=f"{qtd} Produto{'s' if qtd != 1 else ''} Encontrado{'s' if qtd != 1 else ''}"
        )
        self._msg.configure(text="")

        for lin, item in enumerate(investimentos):
            # fundo alternado
            bg = tema.CARD_BG if lin % 2 == 0 else tema.BG

            for col, (chave, _, _) in enumerate(CAMPOS):
                bruto = item.get(chave, "-")
                cor = tema.TEXTO_PRIMARIO

                if chave == "isento_ir":
                    eh = str(bruto).strip().lower() in ("sim", "true", "isento")
                    bruto = "Sim" if eh else "Não"
                    cor = tema.ACCENT if eh else tema.TEXTO_SECUNDARIO

                ctk.CTkLabel(
                    self._tabela,
                    text=str(bruto),
                    font=tema.FONTE_CORPO,
                    text_color=cor,
                    fg_color=bg,
                    anchor="w",
                    width=0,
                ).grid(row=lin, column=col, sticky="ew", padx=12, pady=6)

        self.after_idle(self._alinhar_cabecalho)

    def _alinhar_cabecalho(self, _evento=None):
        """Faz o cabeçalho ocupar a mesma faixa horizontal das linhas de dados.

        A área rolável tem margem interna à esquerda e a barra de rolagem à direita,
        então ela é mais estreita que o cartão. Medimos essa faixa e aplicamos a
        diferença como padding do cabeçalho.
        """
        larg = self._tabela.winfo_width()
        if larg <= 1:
            return
        esq = max(self._tabela.winfo_rootx() - self._cartao.winfo_rootx(), 0)
        dir_ = max(self._cartao.winfo_width() - esq - larg, 0)
        if self._cab_padx != (esq, dir_):
            self._cab_padx = (esq, dir_)
            self._cab.grid_configure(padx=(esq, dir_))

    # ── Ações ─────────────────────────────────────────────────────────

    def _exportar_txt(self):
        if not self._dados:
            self._flash("Nenhum dado para exportar.")
            return
        from tkinter import filedialog
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        padrao = f"investimentos_{ts}.txt"
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            initialfile=padrao,
            title="Salvar relatório",
        )
        if not caminho:
            return
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(_formatar_txt(self._dados))
        self._flash(f"Salvo em: {os.path.basename(caminho)}")

    def _copiar(self):
        if not self._dados:
            self._flash("Nenhum dado para copiar.")
            return
        texto = _formatar_txt(self._dados)
        self.clipboard_clear()
        self.clipboard_append(texto)
        self._flash("Copiado para a área de transferência ✓")

    def _flash(self, msg, ms=3000):
        self._msg.configure(text=msg)
        self.after(ms, lambda: self._msg.configure(text=""))