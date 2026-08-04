"""Janela principal — alterna entre pareamento e resultados, com footer."""

import customtkinter as ctk
import tkinter as tk

from . import tema
from .tela_pareamento import TelaPareamento
from .tela_resultados import TelaResultados
from .tela_carregamento import TelaCarregamento

import threading
from src.extrator_banco import (
    iniciar_navegador, realizar_login_por_qrcode,
    navegar_para_renda_fixa, aplicar_filtros, extrair_investimentos
)
from src.gerador_relatorio import criar_relatorio_txt


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title("Painel de Investimentos")
        self.geometry("800x680")
        self.minsize(720, 560)
        self.configure(fg_color=tema.BG)

        self._montar()

    def _montar(self):
        # Área de conteúdo (cresce)
        self._area = ctk.CTkFrame(self, fg_color="transparent")
        self._area.pack(fill="both", expand=True)

        # Footer fixo na base
        self._footer()

        # Telas
        self.tela_pareamento = TelaPareamento(self._area, on_pronto=self._iniciar_automacao )
        self.tela_carregamento = TelaCarregamento(self._area)
        self.tela_resultados = TelaResultados(self._area)


        self._mostrar(self.tela_pareamento)

    def _footer(self):
        rodape = ctk.CTkFrame(
            self,
            fg_color=tema.CARD_BG,
            corner_radius=0,
            height=36,
        )
        rodape.pack(fill="x", side="bottom")
        rodape.pack_propagate(False)

        tk.Frame(rodape, bg=tema.BORDA, height=1).pack(fill="x", side="top")

        ctk.CTkLabel(
            rodape,
            text=f"Painel de Investimentos  ·  v{tema.VERSAO}",
            font=tema.FONTE_LEGENDA,
            text_color=tema.TEXTO_MUTED,
        ).pack(side="left", padx=20)

        self._footer_status = ctk.CTkLabel(
            rodape,
            text="Banco Inter · Renda Fixa",
            font=tema.FONTE_LEGENDA,
            text_color=tema.TEXTO_MUTED,
        )
        self._footer_status.pack(side="right", padx=20)

    # ── Navegação ────────────────────────────────────────────────────

    def _mostrar(self, tela):
        for filho in self._area.winfo_children():
            filho.pack_forget()
        tela.pack(fill="both", expand=True)

    def _trazer_para_frente(self):
        """Força a janela do aplicativo a sobrepor o Chrome."""
        self.attributes('-topmost', True) # Joga no topo de tudo
        self.update()                     # Atualiza a tela
        self.attributes('-topmost', False)# Tira o bloqueio para você poder usar outros apps
        self.lift()
        self.focus_force()

    def _iniciar_automacao(self):
        """Inicia o robô do Selenium em uma thread separada para não travar a UI."""
        self._footer_status.configure(text="Aguardando conexão com o celular...")
        
        def rodar_robo():
            try:
                driver, wait = iniciar_navegador()
                
                # 1. Login Automático
                realizar_login_por_qrcode(driver)

                # GATILHO
                self.after(0, self._trazer_para_frente)
                self.after(0, lambda: self._mostrar(self.tela_carregamento))
                self.after(0, lambda: self._footer_status.configure(text="Sincronizando dados..."))
            
                # Passo 0: Navegação (33% na barra)
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(0, 0.33))
                navegar_para_renda_fixa(wait)
                
                # Passo 1: Filtros (66% na barra)
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(1, 0.66))
                aplicar_filtros(wait)
                
                # Passo 2: Extração (90% na barra)
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(2, 0.90))
                dados = extrair_investimentos(driver, wait)
                
                # Concluído! Enche a barra, fecha o Chrome e exibe os resultados
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(2, 1.0))
                driver.quit() 
                
                self.after(1000, lambda: self.exibir_resultados(dados))
                
            except Exception as e:
                # Se der erro, garante que o Chrome não fique aberto fantasma
                try: driver.quit() 
                except: pass
                self.after(0, self._trazer_para_frente) # Puxa pra frente pra avisar do erro
                self.after(0, lambda: self._erro(f"Falha na automação: {str(e)}"))

        # Dispara o trabalhador invisível (Thread)
        threading.Thread(target=rodar_robo, daemon=True).start()

    def exibir_resultados(self, investimentos):
        """Chame via self.after(0, ...) ao fim da extração."""
        self.tela_resultados.atualizar_dados(investimentos)
        self._footer_status.configure(
            text=f"Banco Inter · {len(investimentos)} produto(s) encontrado(s)"
        )
        self._mostrar(self.tela_resultados)

    def _erro(self, mensagem):
        self.tela_pareamento.restaurar()
        self._mostrar(self.tela_pareamento)
        # Aqui você pode abrir um CTkMessagebox se quiser um popup de erro
        print(f"[ERRO] {mensagem}")