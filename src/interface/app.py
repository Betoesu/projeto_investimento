"""Janela principal — alterna entre pareamento e resultados, com footer."""
 
import customtkinter as ctk
import tkinter as tk
 
from . import tema
from .tela_pareamento import TelaPareamento
from .tela_resultados import TelaResultados
from .tela_carregamento import TelaCarregamento
 
import threading
import traceback
from src.extrator_banco import (
    iniciar_navegador, verificar_login_por_qrcode,
    extrair_investimentos
)
 
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
                verificar_login_por_qrcode(wait)
 
                # GATILHO
                self.after(0, self._trazer_para_frente)
                self.after(0, lambda: self._mostrar(self.tela_carregamento))
                self.after(0, lambda: self._footer_status.configure(text="Sincronizando dados..."))
            
                # Passo 0: Navegação (33% na barra)
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(0, 0.33))
                
                # Passo 1: Filtros (66% na barra)
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(1, 0.66))
                
                # Passo 2: Extração (90% na barra)
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(2, 0.90))
                dados_brutos = extrair_investimentos(driver)
 
                # Concluído! Enche a barra, fecha o Chrome e exibe os resultados
                self.after(0, lambda: self.tela_carregamento.atualizar_etapa(2, 1.0))
                driver.quit()
 
                dados = self._transformar_para_tabela(dados_brutos)
 
                self.after(1000, lambda: self.exibir_resultados(dados))
                
            except Exception as e:
                # Se der erro, garante que o Chrome não fique aberto fantasma
                try: driver.quit() 
                except: pass
 
                # O Python apaga a variável "e" assim que o bloco "except" termina.
                # Como o lambda abaixo só roda depois (agendado via self.after),
                # ele tentava ler um "e" que já não existia mais -> NameError.
                # Por isso capturamos a mensagem numa variável comum antes de agendar.
                mensagem_erro = f"Falha na automação: {e}"
                traceback.print_exc()  # mostra o erro real no console para depuração
 
                self.after(0, self._trazer_para_frente) # Puxa pra frente pra avisar do erro
                self.after(0, lambda: self._erro(mensagem_erro))
 
        # Dispara o trabalhador invisível (Thread)
        threading.Thread(target=rodar_robo, daemon=True).start()
 
    def _transformar_para_tabela(self, dados_api):
        """Converte o JSON bruto da API (Lógica Nova) para o formato de linhas
        que TelaResultados já sabe exibir (produto/rendimento/investimento_minimo/
        isento_ir/vencimento). Usa o mesmo filtro de risco/tipo do gerar_relatorio,
        para que a tabela na tela e o .txt exportado fiquem consistentes."""
        tabela = []
        for item in dados_api:
            if item.get("grauRisco") not in (1, 2, 3):
                continue
            if item.get("tipo", {}).get("descricao") not in ("LCI", "LCA", "CDB"):
                continue
 
            aplicacao_minima = item.get("aplicacaoMinima", 0)
            try:
                inv_minimo = f"R$ {float(aplicacao_minima):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (TypeError, ValueError):
                inv_minimo = str(aplicacao_minima)
 
            data_resgate = item.get("dataResgate") or ""
            vencimento = "/".join(data_resgate.split("-")[::-1]) if data_resgate else "-"
 
            tabela.append({
                "produto": item.get("nome", "-"),
                "rendimento": str(item.get("taxa", "-")),
                "investimento_minimo": inv_minimo,
                "isento_ir": bool(item.get("isentoImpostos", False)),
                "vencimento": vencimento,
            })
        return tabela
 
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
 