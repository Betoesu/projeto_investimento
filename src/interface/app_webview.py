import webview
import os
import pyperclip
import traceback
import threading

def _transformar_para_tabela(dados_brutos):
    tabela = []
    for item in dados_brutos:
        if item.get("grauRisco") not in (1, 2, 3): continue
        if item.get("tipo", {}).get("descricao") not in ("LCI", "LCA", "CDB"): continue

        aplicacao_minima = item.get("aplicacaoMinima", 0)
        try:
            inv_minimo = f"R$ {float(aplicacao_minima):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            inv_minimo = str(aplicacao_minima)

        data_resgate = item.get("dataResgate") or ""
        vencimento = "/".join(data_resgate.split("-")[::-1]) if data_resgate else "-"

        tabela.append({
            "produto": item.get("nome", "-"),
            "rendimento": str(item.get("taxa", "-")),
            "investimento_minimo": inv_minimo,
            "isento_ir": bool(item.get("isentoImpostos", False)),
            "vencimento": vencimento,
            "tipo_investimento": item.get("tipo", {}).get("descricao")
        })
    return tabela

def _formatar_linhas_relatorio(dados_filtrados):
    return "\n".join(
        f"{d['produto']} | {d['rendimento']} | {d['investimento_minimo']} | {d['vencimento']}"
        for d in dados_filtrados
    )

class Api:
    def __init__(self):
        self.investimentos = []
        self.status_extracao = {
            "etapa": "idle",
            "progresso": 0,
            "titulo": "Sincronizando com o Banco",
            "mensagem": "Preparando conexão...",
            "subtitulo": "Iniciando processo..."
        }
        # Pré-carrega os módulos pesados (seleniumwire/selenium) em segundo plano
        # enquanto o usuário está nas telas de instruções, para que ao clicar
        # em "Próximo" na última etapa o navegador do Inter abra imediatamente.
        threading.Thread(target=self._precarregar_extrator, daemon=True).start()

    def _precarregar_extrator(self):
        try:
            import src.extrator_banco  # noqa: F401
        except Exception:
            pass

    def _atualizar_status(self, etapa, progresso, titulo, mensagem, subtitulo):
        self.status_extracao = {
            "etapa": etapa,
            "progresso": progresso,
            "titulo": titulo,
            "mensagem": mensagem,
            "subtitulo": subtitulo
        }

    def obter_status_extracao(self):
        return self.status_extracao

    def obter_investimentos(self):
        return self.investimentos
        
    def iniciar_extracao(self):
        print("Iniciando extração do banco via robô...")
        self._atualizar_status(
            etapa="abrindo_navegador",
            progresso=8,
            titulo="Abrindo o Banco Inter",
            mensagem="Iniciando o navegador e carregando a página de acesso do Inter...",
            subtitulo="Aguarde a abertura da janela do Chrome"
        )
        from src.extrator_banco import iniciar_navegador, verificar_login_por_qrcode, extrair_investimentos
        driver = None
        try:
            driver, wait = iniciar_navegador()

            self._atualizar_status(
                etapa="aguardando_qrcode",
                progresso=35,
                titulo="Aguardando Leitura do QR Code",
                mensagem="Navegador aberto! Escaneie o QR Code exibido na tela do Inter com seu celular...",
                subtitulo="Acompanhe e autentique pelo navegador Chrome aberto"
            )
            verificar_login_por_qrcode(wait)

            self._atualizar_status(
                etapa="extraindo_dados",
                progresso=75,
                titulo="Extraindo Investimentos",
                mensagem="Login confirmado! Capturando os produtos de Renda Fixa disponíveis...",
                subtitulo="Sincronizando catálogo de investimentos"
            )
            dados_brutos = extrair_investimentos(driver)
            
            self._atualizar_status(
                etapa="processando",
                progresso=95,
                titulo="Processando Dados",
                mensagem="Formatando e organizando a tabela de investimentos...",
                subtitulo="Quase pronto"
            )
            self.investimentos = _transformar_para_tabela(dados_brutos)

            self._atualizar_status(
                etapa="concluido",
                progresso=100,
                titulo="Sincronização Concluída",
                mensagem="Investimentos carregados com sucesso!",
                subtitulo="Concluído"
            )
            return self.investimentos
        except Exception as e:
            self._atualizar_status(
                etapa="erro",
                progresso=0,
                titulo="Falha na Sincronização",
                mensagem=str(e),
                subtitulo="Tente novamente"
            )
            traceback.print_exc()
            raise Exception(f"Falha na extração: {str(e)}")
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass

    def exportar_txt(self, dados_filtrados):
        print(f"Exportando {len(dados_filtrados)} produtos para TXT...")
        from tkinter import filedialog
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            initialfile=f"investimentos_{ts}.txt",
            title="Salvar relatório",
        )
        if caminho:
            texto = _formatar_linhas_relatorio(dados_filtrados)
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
        return True

    def copiar_dados(self, dados_filtrados):
        print(f"Copiando {len(dados_filtrados)} produtos...")
        texto = _formatar_linhas_relatorio(dados_filtrados)
        pyperclip.copy(texto)
        return True

def main():
    api = Api()
    caminho_html = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "index.html"))
    janela = webview.create_window(
        title="ZENO - Painel de Investimentos", 
        url="file://" + caminho_html,
        js_api=api,
        width=1380, 
        height=840,
        background_color="#0b0e11"
    )
    webview.start()

if __name__ == "__main__":
    main()
