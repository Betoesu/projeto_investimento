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

# Quais colunas têm o comportamento de seta (exclusividade mútua)
_COLS_SETA   = {"investimento_minimo", "vencimento"}
                                                                       # caso queira mexer com redimento _COLS_SETA   = {"rendimento", "investimento_minimo", "vencimento"}
# A coluna toggle de fundo
_COL_TOGGLE  = "isento_ir"
# A coluna de reset
_COL_RESET   = "produto"

# Ícones de ordenação
_SETA_CIMA   = " ↑"
_SETA_BAIXO  = " ↓"

# Cores do cabeçalho interativo
_COR_NORMAL        = tema.TEXTO_MUTED
_COR_HOVER         = tema.TEXTO_SECUNDARIO
_COR_ATIVO         = tema.ACCENT          # verde quando ativo (seta)
_COR_RESET_HOVER   = tema.TEXTO_SECUNDARIO
_BG_NORMAL         = tema.CARD_BG
_BG_HOVER          = tema.CARD_BG_HOVER
_BG_SETA_ATIVO     = tema.ACCENT_BG      # fundo sutil verde nas colunas com seta ativa
_BG_TOGGLE_ATIVO   = tema.ACCENT_BG
_COR_TOGGLE_ATIVO  = tema.ACCENT



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

# ──────────────────────────────────────────────────────────────────────────────
# Widget de célula de cabeçalho
# ──────────────────────────────────────────────────────────────────────────────

class _CelulaCabecalho(tk.Frame):
    """Célula interativa do cabeçalho da tabela.

    Três modos de comportamento, selecionados por `modo`:
      "reset"   – Produto: clique invisível que reseta todos os outros.
      "seta"    – Rendimento / Inv. Mínimo / Vencimento: hover de botão +
                  seta que alterna ↑ / ↓ com exclusividade mútua.
      "toggle"  – Isento IR: hover normal + fundo verde quando ativo.
    """

    def __init__(self, master, rotulo: str, modo: str,
                 on_click=None, **kwargs):
        super().__init__(master, bg=_BG_NORMAL,
                         highlightthickness=0, bd=0, **kwargs)
        self._rotulo  = rotulo
        self._modo    = modo           # "reset" | "seta" | "toggle"
        self.on_click = on_click       # callable sem argumentos

        # Estado interno
        self._seta_estado = None       # None | "cima" | "baixo"  (modo seta)
        self._toggle_ativo = False     # (modo toggle)

        # Label principal
        self._label = tk.Label(
            self,
            text=rotulo,
            font=tema.FONTE_TABELA_H,
            fg=_COR_NORMAL,
            bg=_BG_NORMAL,
            anchor="w",
            cursor="hand2",
        )
        self._label.pack(fill="both", expand=True, padx=0, pady=0)

        # Bind de eventos em ambos frame + label para não haver "buracos"
        for widget in (self, self._label):
            widget.bind("<Enter>",  self._ao_entrar)
            widget.bind("<Leave>",  self._ao_sair)
            widget.bind("<Button-1>", self._ao_clicar)

    # ── Eventos ──────────────────────────────────────────────────────────────

    def _ao_entrar(self, _e=None):
        if self._modo == "reset":
            # Produto: hover sutil — só clareia o texto, sem mudar o fundo
            self._label.configure(fg=_COR_RESET_HOVER)
            return
        if self._modo == "toggle" and self._toggle_ativo:
            return  # já tem fundo verde; não altera hover

        bg_h = _BG_HOVER
        if self._modo == "seta" and self._seta_estado is not None:
            # ativo: mantém o bg verde e clareia ainda mais o texto no hover
            bg_h = _BG_SETA_ATIVO
            cor_h = tema.TEXTO_PRIMARIO
        else:
            cor_h = _COR_HOVER
        self.configure(bg=bg_h)
        self._label.configure(bg=bg_h, fg=cor_h)

    def _ao_sair(self, _e=None):
        if self._modo == "reset":
            self._label.configure(fg=_COR_NORMAL)
            return
        self._restaurar_visual()

    def _ao_clicar(self, _e=None):
        if self.on_click:
            self.on_click()

    # ── API pública (chamada pelo TelaResultados) ─────────────────────────────

    def ativar_seta(self):
        """Modo seta: avança o estado None → ↑ → ↓ → ↑ → …"""
        if self._seta_estado is None or self._seta_estado == "baixo":
            self._seta_estado = "cima"
        else:
            self._seta_estado = "baixo"
        icone = _SETA_CIMA if self._seta_estado == "cima" else _SETA_BAIXO
        self._label.configure(
            text=self._rotulo + icone,
            fg=_COR_ATIVO,          # verde
            bg=_BG_SETA_ATIVO,      # fundo verde sutil
        )
        self.configure(bg=_BG_SETA_ATIVO)

    def limpar_seta(self):
        """Modo seta: remove a seta e volta ao estilo neutro."""
        self._seta_estado = None
        self._label.configure(text=self._rotulo, fg=_COR_NORMAL, bg=_BG_NORMAL)
        self.configure(bg=_BG_NORMAL)

    def alternar_toggle(self):
        """Modo toggle: inverte o estado de fundo."""
        self._toggle_ativo = not self._toggle_ativo
        self._restaurar_visual()

    def resetar(self):
        """Volta a célula ao estado neutro (seta ou toggle)."""
        if self._modo == "seta":
            self.limpar_seta()
        elif self._modo == "toggle":
            self._toggle_ativo = False
            self._restaurar_visual()

    # ── Helpers internos ─────────────────────────────────────────────────────

    def _restaurar_visual(self):
        """Aplica o visual correto para o estado atual (fora do hover)."""
        if self._modo == "toggle" and self._toggle_ativo:
            bg  = _BG_TOGGLE_ATIVO
            cor = _COR_TOGGLE_ATIVO
        elif self._modo == "seta" and self._seta_estado is not None:
            bg  = _BG_SETA_ATIVO    # fundo verde sutil mantido no estado ativo
            cor = _COR_ATIVO        # texto verde
        else:
            bg  = _BG_NORMAL
            cor = _COR_NORMAL

        self.configure(bg=bg)
        self._label.configure(bg=bg, fg=cor)

class TelaResultados(ctk.CTkFrame):
    """Cabeçalho + tabela rolável + barra de ações."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=tema.BG, corner_radius=0, **kwargs)

        self.winfo_toplevel().geometry("1200x700")

        self._dados = []
        self._celulas_cab: dict[str, _CelulaCabecalho] = {}
        self._montar()

    # ── Construção da UI ─────────────────────────────────────────────

    def _montar(self):
        # Título + pílula de contagem
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

        tk.Frame(self, bg=tema.BORDA, height=1).pack(fill="x", padx=28, pady=(12, 0))

        # Cartão da tabela
        self._cartao = ctk.CTkFrame(self, fg_color=tema.CARD_BG, corner_radius=12)
        self._cartao.pack(fill="both", expand=True, padx=28, pady=(16, 0))
        cartao = self._cartao

        cartao.grid_columnconfigure(0, weight=1)
        cartao.grid_rowconfigure(0, minsize=48)
        cartao.grid_rowconfigure(1, weight=1)

        # ── Faixa de cabeçalho ───────────────────────────────────────────────
        self._cab = tk.Frame(cartao, bg=_BG_NORMAL, highlightthickness=0, bd=0)
        self._cab.grid(row=0, column=0, sticky="nsew")

        for i, (chave, rotulo, peso) in enumerate(CAMPOS):
            self._cab.grid_columnconfigure(i, weight=peso, uniform="cols")

            # === ADICIONE ESTE BLOCO AQUI === Caso queria que rendimento seja alteravel apague esse if abaixo
            if chave == "rendimento":
                # Desenha apenas um texto fixo, sem botão ou interações
                tk.Label(
                    self._cab, text=rotulo, font=tema.FONTE_TABELA_H,
                    fg=_COR_NORMAL, bg=_BG_NORMAL, anchor="w"
                ).grid(row=0, column=i, sticky="nsew", padx=12, pady=(12, 10))
                continue  # Pula para a próxima coluna sem ler o código de baixo
            
            if chave == _COL_RESET:
                modo = "reset"
            elif chave == _COL_TOGGLE:
                modo = "toggle"
            elif chave in _COLS_SETA:
                modo = "seta"
            else:
                modo = "reset"  # fallback seguro

            celula = _CelulaCabecalho(
                self._cab,
                rotulo=rotulo,
                modo=modo,
                on_click=lambda ch=chave: self._ao_clicar_cabecalho(ch),
            )
            celula.grid(row=0, column=i, sticky="nsew", padx=12, pady=(12, 10))
            self._celulas_cab[chave] = celula

        # Linha separadora colada no fundo do cabeçalho
        tk.Frame(cartao, bg=tema.BORDA, height=1).grid(
            row=0, column=0, sticky="sew", padx=12, pady=0
        )

        # ── Área de dados ────────────────────────────────────────────────────
        self._tabela = ctk.CTkScrollableFrame(cartao, fg_color="transparent")
        self._tabela.grid(row=1, column=0, sticky="nsew", pady=(4, 8))

        for i, (_, _, peso) in enumerate(CAMPOS):
            self._tabela.grid_columnconfigure(i, weight=peso, uniform="cols")

        # Alinhamento dinâmico do cabeçalho com a área de dados
        self._cab_padx = None
        self._tabela.bind("<Configure>", self._alinhar_cabecalho, add="+")
        cartao.bind("<Configure>",       self._alinhar_cabecalho, add="+")

        # ── Barra de ações ───────────────────────────────────────────────────
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

    # ── Eventos do cabeçalho ─────────────────────────────────────────────────

    def _ao_clicar_cabecalho(self, chave: str):
        """Despacha o clique de acordo com o modo de cada coluna e reordena."""
        
        # 1. ATUALIZA O VISUAL DOS BOTÕES
        if chave == _COL_RESET:
            # Produto: reseta todos os outros cabeçalhos
            for ch, cel in self._celulas_cab.items():
                if ch != _COL_RESET:
                    cel.resetar()

        elif chave == _COL_TOGGLE:
            # Isento IR: toggle de fundo, independente das setas
            self._celulas_cab[chave].alternar_toggle()

        elif chave in _COLS_SETA:
            # Rendimento / Inv. Mínimo / Vencimento: exclusividade de setas
            for ch, cel in self._celulas_cab.items():
                if ch in _COLS_SETA and ch != chave:
                    cel.limpar_seta()
            self._celulas_cab[chave].ativar_seta()

        # 2. CHAMA A CENTRAL DE ORDENAÇÃO
        # Ela vai olhar para o estado visual dos botões, ordenar em cascata 
        # (garantindo o Isento no topo) e chamar o atualizar_dados() sozinha.
        self._aplicar_ordenacao()


    def _aplicar_ordenacao(self):
        # 1. Ordem base (Produto alfabético)
        tabela = sorted(self._dados, key=lambda d: str(d.get('produto', '')).lower())

        # 2. AQUI ESTÃO OS SEUS IFs DE VENCIMENTO E INVESTIMENTO MÍNIMO
        for chave in _COLS_SETA:
            estado = self._celulas_cab[chave]._seta_estado
            if estado:
                if chave == "investimento_minimo":
                    def get_minimo(d):
                        try:
                            return float(str(d.get('investimento_minimo', '0')).replace("R$ ","").replace('.','').replace(',','.'))
                        except Exception:
                            return 0.0
                            
                    tabela.sort(key=get_minimo, reverse=(estado == "baixo"))

                elif chave == "vencimento":
                    def get_data(d):
                        v = str(d.get('vencimento', '-')).strip()
                        if v == "-":
                            return datetime.datetime.min if estado == "baixo" else datetime.datetime.max
                        try:
                            return datetime.datetime.strptime(v, "%d/%m/%Y")
                        except Exception:
                            return datetime.datetime.min if estado == "baixo" else datetime.datetime.max
                            
                    tabela.sort(key=get_data, reverse=(estado == "baixo"))

        # 3. AQUI ESTÁ O SEU IF DO ISENTO IR (Por último, para ser o mestre da tabela)
        if self._celulas_cab["isento_ir"]._toggle_ativo:
            def get_isento(d):
                v = d.get('isento_ir', False)
                if isinstance(v, bool): 
                    return 1 if v else 0
                return 1 if str(v).strip().lower() in ("sim", "true", "isento", "1") else 0
                
            tabela.sort(key=get_isento, reverse=True)

        # 4. Finalmente, envia a tabela ordenada para ser desenhada
        self.atualizar_dados(tabela)
        
    # ── Alinhamento dinâmico ──────────────────────────────────────────────────

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


    # ── Dados ────────────────────────────────────────────────────────

    def atualizar_dados(self, investimentos):
        """Redesenha a tabela ou apenas atualiza os valores se a quantidade for a mesma (Muito mais rápido)."""
        self._dados = investimentos

        qtd = len(investimentos)
        self._pill.configure(
            text=f"{qtd} Produto{'s' if qtd != 1 else ''} Encontrado{'s' if qtd != 1 else ''}"
        )
        self._msg.configure(text="")

        widgets_existentes = self._tabela.winfo_children()
        total_labels_necessarios = qtd * len(CAMPOS)

        # Se a quantidade mudou, destrói tudo e recria do zero (Lento, mas necessário)
        if len(widgets_existentes) != total_labels_necessarios:
            for w in widgets_existentes:
                w.destroy()

            for lin, item in enumerate(investimentos):
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

        # MÁGICA AQUI: Se a quantidade é a mesma, só troca os textos e as cores (Instantâneo)
        else:
            idx = 0
            for lin, item in enumerate(investimentos):
                for col, (chave, _, _) in enumerate(CAMPOS):
                    bruto = item.get(chave, "-")
                    cor = tema.TEXTO_PRIMARIO

                    if chave == "isento_ir":
                        eh = str(bruto).strip().lower() in ("sim", "true", "isento")
                        bruto = "Sim" if eh else "Não"
                        cor = tema.ACCENT if eh else tema.TEXTO_SECUNDARIO

                    # Acessa a label que já está na tela e apenas altera seus valores
                    widgets_existentes[idx].configure(text=str(bruto), text_color=cor)
                    idx += 1

        self.after_idle(self._alinhar_cabecalho)

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