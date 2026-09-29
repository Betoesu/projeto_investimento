"""Tela de resultados: tabela de produtos + exportar TXT + copiar."""

import datetime
import os
import tkinter as tk

import customtkinter as ctk

from . import tema

CAMPOS = [
    ("produto",            "Produto",       5),
    ("rendimento",         "Rendimento",    3),
    ("investimento_minimo","Inv. Mínimo",   3),
    ("isento_ir",          "Isento IR",     3),
    ("vencimento",         "Vencimento",    4),
]

# Quais colunas têm o comportamento de seta (exclusividade mútua)
_COLS_SETA  = {"investimento_minimo", "vencimento", "rendimento"}
# A coluna toggle de fundo
_COL_TOGGLE = "isento_ir"
# A coluna de reset
_COL_RESET  = "produto"

# Ícones de ordenação
_SETA_CIMA  = " ↑"
_SETA_BAIXO = " ↓"

# Cores do cabeçalho interativo
_COR_NORMAL       = tema.TEXTO_MUTED
_COR_HOVER        = tema.TEXTO_SECUNDARIO
_COR_ATIVO        = tema.ACCENT
_COR_RESET_HOVER  = tema.TEXTO_SECUNDARIO
_BG_NORMAL        = tema.CARD_BG
_BG_HOVER         = tema.CARD_BG_HOVER
_BG_SETA_ATIVO    = tema.ACCENT_BG
_BG_TOGGLE_ATIVO  = tema.ACCENT_BG
_COR_TOGGLE_ATIVO = tema.ACCENT


# ── Helpers de módulo ─────────────────────────────────────────────────────────

def _formatar_txt(investimentos):
    """Gera o texto no mesmo estilo que o main.py já exporta."""
    linhas = []
    agora  = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
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


def _padronizar_rendimentos(tabela: list) -> list:
    """Adiciona 'rendimento_padronizado' (float, % a.a.) em cada item.

    Regras (em ordem de prioridade):
      'Rende até … X% do CDI'  → calcular_cdi_anual(X)
      'IPCA + X%'              → calcular_ipca_anual(X)
      'X% a.a.'                → X   (já em % a.a.)
      'X% do CDI'              → calcular_cdi_anual(X)

    Retorna a mesma lista (mutada in-place) para facilitar encadeamento.
    Um try/except por item garante que um formato inesperado não derruba a tela.
    """
    try:
        from ..taxas import calcular_cdi_anual, calcular_ipca_anual
    except ImportError:
        # fallback: sem as funções auxiliares, usa o número bruto
        def calcular_cdi_anual(x):  return x
        def calcular_ipca_anual(x): return x

    for inv in tabela:
        taxa = inv.get("rendimento", "")
        try:
            if "Rende até" in taxa and "+" not in taxa:
                try:
                    valor = float(taxa.split()[-3].replace("%", "").replace(",", "."))
                    padronizado = calcular_cdi_anual(valor)
                except (IndexError, ValueError):
                    padronizado = float(taxa.split()[-2].replace("%", "").replace(",", "."))
            elif "IPCA" in taxa:
                valor = float(taxa.split()[-2].replace("%", "").replace(",", "."))
                padronizado = calcular_ipca_anual(valor)
            elif "a.a" in taxa:
                padronizado = float(taxa.split()[0].replace("%", "").replace(",", "."))
            else:
                valor = float(taxa.split()[0].replace("%", "").replace(",", "."))
                padronizado = calcular_cdi_anual(valor)
        except Exception:
            padronizado = 0.0   # mantém o item sem quebrar a ordenação

        inv["rendimento_padronizado"] = padronizado

    return tabela


# ──────────────────────────────────────────────────────────────────────────────
# Widget de célula de cabeçalho
# ──────────────────────────────────────────────────────────────────────────────

class _CelulaCabecalho(tk.Frame):
    """Célula interativa do cabeçalho da tabela.

    Modos:
      "reset"  – Produto: hover sutil + clique limpa todos os outros.
      "seta"   – Inv. Mínimo / Vencimento: hover de botão,
                 estado ativo em verde + seta ↑/↓, exclusividade mútua.
      "toggle" – Isento IR: hover normal + fundo verde quando ativo.
    """

    def __init__(self, master, rotulo: str, modo: str,
                 on_click=None, **kwargs):
        super().__init__(master, bg=_BG_NORMAL,
                         highlightthickness=0, bd=0, **kwargs)
        self._rotulo       = rotulo
        self._modo         = modo
        self.on_click      = on_click
        self._seta_estado  = None   # None | "cima" | "baixo"
        self._toggle_ativo = False

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

        for widget in (self, self._label):
            widget.bind("<Enter>",    self._ao_entrar)
            widget.bind("<Leave>",    self._ao_sair)
            widget.bind("<Button-1>", self._ao_clicar)

    # ── Eventos ──────────────────────────────────────────────────────────────

    def _ao_entrar(self, _e=None):
        if self._modo == "reset":
            self._label.configure(fg=_COR_RESET_HOVER)
            return
        if self._modo == "toggle" and self._toggle_ativo:
            return

        bg_h = _BG_HOVER
        if self._modo == "seta" and self._seta_estado is not None:
            bg_h  = _BG_SETA_ATIVO
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

    # ── API pública ───────────────────────────────────────────────────────────

    def ativar_seta(self):
        """Avança o estado: None → ↑ → ↓ → ↑ → …"""
        if self._seta_estado is None or self._seta_estado == "baixo":
            self._seta_estado = "cima"
        else:
            self._seta_estado = "baixo"
        icone = _SETA_CIMA if self._seta_estado == "cima" else _SETA_BAIXO
        self._label.configure(
            text=self._rotulo + icone,
            fg=_COR_ATIVO,
            bg=_BG_SETA_ATIVO,
        )
        self.configure(bg=_BG_SETA_ATIVO)

    def limpar_seta(self):
        """Remove a seta e volta ao estilo neutro."""
        self._seta_estado = None
        self._label.configure(text=self._rotulo, fg=_COR_NORMAL, bg=_BG_NORMAL)
        self.configure(bg=_BG_NORMAL)

    def alternar_toggle(self):
        """Inverte o estado de fundo verde."""
        self._toggle_ativo = not self._toggle_ativo
        self._restaurar_visual()

    def resetar(self):
        """Volta ao estado neutro (qualquer modo)."""
        if self._modo == "seta":
            self.limpar_seta()
        elif self._modo == "toggle":
            self._toggle_ativo = False
            self._restaurar_visual()

    # ── Helpers internos ─────────────────────────────────────────────────────

    def _restaurar_visual(self):
        if self._modo == "toggle" and self._toggle_ativo:
            bg, cor = _BG_TOGGLE_ATIVO, _COR_TOGGLE_ATIVO
        elif self._modo == "seta" and self._seta_estado is not None:
            bg, cor = _BG_SETA_ATIVO, _COR_ATIVO
        else:
            bg, cor = _BG_NORMAL, _COR_NORMAL
        self.configure(bg=bg)
        self._label.configure(bg=bg, fg=cor)


# ──────────────────────────────────────────────────────────────────────────────
# Tela principal
# ──────────────────────────────────────────────────────────────────────────────

class TelaResultados(ctk.CTkFrame):
    """Cabeçalho + tabela rolável + barra de ações."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=tema.BG, corner_radius=0, **kwargs)
        self.winfo_toplevel().geometry("1200x700")
        self._dados: list = []          # dados originais (recebidos de fora)
        self._celulas_cab: dict[str, _CelulaCabecalho] = {}
        self._montar()

    # ── Construção da UI ─────────────────────────────────────────────────────

    def _montar(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=28, pady=(24, 0))

        ctk.CTkLabel(
            topo, text="Painel de Investimentos",
            font=tema.FONTE_TITULO, text_color=tema.TEXTO_PRIMARIO,
        ).pack(side="left")

        self._pill = ctk.CTkLabel(
            topo, text="0 Produtos Encontrados",
            font=tema.FONTE_LEGENDA, text_color=tema.ACCENT,
            fg_color=tema.ACCENT_BG, corner_radius=6, padx=10, pady=4,
        )
        self._pill.pack(side="right")

        tk.Frame(self, bg=tema.BORDA, height=1).pack(fill="x", padx=28, pady=(12, 0))

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

            if chave == _COL_RESET:
                modo = "reset"
            elif chave == _COL_TOGGLE:
                modo = "toggle"
            elif chave in _COLS_SETA:
                modo = "seta"
            else:
                modo = "reset"

            celula = _CelulaCabecalho(
                self._cab, rotulo=rotulo, modo=modo,
                on_click=lambda ch=chave: self._ao_clicar_cabecalho(ch),
            )
            celula.grid(row=0, column=i, sticky="nsew", padx=12, pady=(12, 10))
            self._celulas_cab[chave] = celula

        tk.Frame(cartao, bg=tema.BORDA, height=1).grid(
            row=0, column=0, sticky="sew", padx=12, pady=0
        )

        # ── Área de dados ────────────────────────────────────────────────────
        self._tabela = ctk.CTkScrollableFrame(cartao, fg_color="transparent")
        self._tabela.grid(row=1, column=0, sticky="nsew", pady=(4, 8))

        for i, (_, _, peso) in enumerate(CAMPOS):
            self._tabela.grid_columnconfigure(i, weight=peso, uniform="cols")

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


        #--------------------TEMPORÁRIO--------------------

        # Caixas de filtro
        self._input_min = ctk.CTkEntry(barra, placeholder_text="Mín (Ex: 100)", width=100)
        self._input_min.pack(side="left", padx=(0, 8))
        
        self._input_max = ctk.CTkEntry(barra, placeholder_text="Máx (Ex: 5000)", width=100)
        self._input_max.pack(side="left", padx=(0, 12))

        # Opcional: um botão para disparar o filtro manualmente
        self._btn_filtrar = ctk.CTkButton(
            barra, text="Filtrar", width=80, 
            command=self._aplicar_ordenacao
        )
        self._btn_filtrar.pack(side="left", padx=(0, 24))

        #--------------------TEMPORÁRIO--------------------

    # ── Eventos do cabeçalho ─────────────────────────────────────────────────

    def _ao_clicar_cabecalho(self, chave: str):
        """Atualiza o visual dos botões e dispara a ordenação."""
        if chave == _COL_RESET:
            for ch, cel in self._celulas_cab.items():
                if ch != _COL_RESET:
                    cel.resetar()

        elif chave == _COL_TOGGLE:
            self._celulas_cab[chave].alternar_toggle()

        elif chave in _COLS_SETA:
            for ch, cel in self._celulas_cab.items():
                if ch in _COLS_SETA and ch != chave:
                    cel.limpar_seta()
            self._celulas_cab[chave].ativar_seta()

        self._aplicar_ordenacao()

    def _aplicar_ordenacao(self):
        """Filtra e Ordena self._dados respeitando os estados dos botões e redesenha.

        
        MUDAR |
              v
        Cascata de ordenação (da menor para a maior prioridade):
          1. Alfabético por produto (base sempre estável)
          2. Coluna de seta ativa (Inv. Mínimo ou Vencimento ou Rendimento)
          3. Isento IR no topo — prioridade máxima (por ser toggle global)
        """
        # 1. LER OS INPUTS DA TELA
        # Tenta converter o que o usuário digitou. Se estiver vazio ou for letra, assume os limites padrão.
        try:
            val_min = float(self._input_min.get().replace(",", ".")) if self._input_min.get().strip() else 0.0
        except ValueError:
            val_min = 0.0

        try:
            val_max = float(self._input_max.get().replace(",", ".")) if self._input_max.get().strip() else float('inf')
        except ValueError:
            val_max = float('inf')

        # 2. APLICA FILTRO DE VALORES
        try:   
            val_min = 0.0 if val_min == "" else float(val_min)
            val_max = float('inf') if val_max == "" else float(val_max)
             
        except ValueError:
            print("Entrada inválida! Por favor, digite somente números.")
            return []

        tabela_filtrada = []
        for inv in self._dados:
            texto_valor = str(inv.get("investimento_minimo", "0"))
            try:
                # Limpa a string financeira e converte
                texto_limpo = texto_valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
                valor_inv = float(texto_limpo)
            except ValueError:
                valor_inv = 0.0
            
            # Só adiciona na lista se estiver dentro da faixa
            if val_min <= valor_inv <= val_max:
                tabela_filtrada.append(inv)

        # 3. Base alfabética
        tabela = sorted(tabela_filtrada, key=lambda d: str(d.get("produto", "")).lower())

        # 4. Colunas de seta (Inv. Mínimo e Vencimento e Rendimento)
        for chave in _COLS_SETA:
            cel = self._celulas_cab.get(chave)
            if cel is None:
                continue
            estado = cel._seta_estado
            if not estado:
                continue

            decrescente = (estado == "cima")

            if chave == "investimento_minimo":
                def get_minimo(d, _ch=chave):
                    try:
                        return float(
                            str(d.get(_ch, "0"))
                            .replace("R$ ", "").replace(".", "").replace(",", ".")
                        )
                    except Exception:
                        return 0.0
                tabela.sort(key=get_minimo, reverse=decrescente)

            elif chave == "vencimento":
                _sentinela = datetime.datetime.min if not decrescente else datetime.datetime.max
                def get_data(d, _s=_sentinela):
                    v = str(d.get("vencimento", "-")).strip()
                    if v == "-":
                        return _s
                    try:
                        return datetime.datetime.strptime(v, "%d/%m/%Y")
                    except Exception:
                        return _s
                tabela.sort(key=get_data, reverse=decrescente)
                
            elif chave == "rendimento":
                tabela.sort(
                    key=lambda d: float(d.get("rendimento_padronizado", 0)),
                    reverse=decrescente
                )

        # 5. Isento IR sempre por último → fica no topo da cascata
        if self._celulas_cab.get("isento_ir") and self._celulas_cab["isento_ir"]._toggle_ativo:
            def get_isento(d):
                v = d.get("isento_ir", False)
                if isinstance(v, bool):
                    return 1 if v else 0
                return 1 if str(v).strip().lower() in ("sim", "true", "isento", "1") else 0
            tabela.sort(key=get_isento, reverse=True)

        # 6. MANDA DESENHAR A TABELA FILTRADA E ORDENADA
        self._renderizar(tabela)

    # ── Alinhamento dinâmico ──────────────────────────────────────────────────

    def _alinhar_cabecalho(self, _evento=None):
        larg = self._tabela.winfo_width()
        if larg <= 1:
            return
        esq  = max(self._tabela.winfo_rootx() - self._cartao.winfo_rootx(), 0)
        dir_ = max(self._cartao.winfo_width() - esq - larg, 0)
        if self._cab_padx != (esq, dir_):
            self._cab_padx = (esq, dir_)
            self._cab.grid_configure(padx=(esq, dir_))

    # ── Dados ─────────────────────────────────────────────────────────────────

    def atualizar_dados(self, investimentos):
        """Ponto de entrada público. Padroniza rendimentos e dispara a ordenação.

        Separa intencionalmente 'receber dados' de 'renderizar': chamar este
        método de fora nunca bypassa a ordenação nem a padronização.
        """
        self._dados = _padronizar_rendimentos(list(investimentos))
        self._aplicar_ordenacao()

    def _renderizar(self, investimentos):
        """Redesenha a tabela com a lista já ordenada.

        Otimização: se a quantidade de linhas não mudou, apenas atualiza o
        texto e a cor dos CTkLabel existentes (sem recriar widgets).
        """
        qtd = len(investimentos)
        self._pill.configure(
            text=f"{qtd} Produto{'s' if qtd != 1 else ''} Encontrado{'s' if qtd != 1 else ''}"
        )
        self._msg.configure(text="")

        widgets = self._tabela.winfo_children()
        total_necessario = qtd * len(CAMPOS)

        if len(widgets) != total_necessario:
            # Quantidade mudou: destrói e recria do zero
            for w in widgets:
                w.destroy()
            for lin, item in enumerate(investimentos):
                bg = tema.CARD_BG if lin % 2 == 0 else tema.BG
                for col, (chave, _, _) in enumerate(CAMPOS):
                    bruto, cor = self._formatar_celula(item, chave)
                    ctk.CTkLabel(
                        self._tabela,
                        text=str(bruto), font=tema.FONTE_CORPO,
                        text_color=cor, fg_color=bg,
                        anchor="w", width=0,
                    ).grid(row=lin, column=col, sticky="ew", padx=12, pady=6)
        else:
            # Mesma quantidade: atualiza só texto e cor (instantâneo)
            idx = 0
            for lin, item in enumerate(investimentos):
                for col, (chave, _, _) in enumerate(CAMPOS):
                    bruto, cor = self._formatar_celula(item, chave)
                    widgets[idx].configure(text=str(bruto), text_color=cor)
                    idx += 1

        self.after_idle(self._alinhar_cabecalho)

    @staticmethod
    def _formatar_celula(item: dict, chave: str) -> tuple:
        """Retorna (texto, cor) prontos para exibição de uma célula."""
        bruto = item.get(chave, "-")
        cor   = tema.TEXTO_PRIMARIO
        if chave == "isento_ir":
            eh    = str(bruto).strip().lower() in ("sim", "true", "isento")
            bruto = "Sim" if eh else "Não"
            cor   = tema.ACCENT if eh else tema.TEXTO_SECUNDARIO
        return bruto, cor

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _exportar_txt(self):
        if not self._dados:
            self._flash("Nenhum dado para exportar.")
            return
        from tkinter import filedialog
        ts      = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            initialfile=f"investimentos_{ts}.txt",
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
        self.clipboard_clear()
        self.clipboard_append(_formatar_txt(self._dados))
        self._flash("Copiado para a área de transferência ✓")

    def _flash(self, msg, ms=3000):
        self._msg.configure(text=msg)
        self.after(ms, lambda: self._msg.configure(text=""))