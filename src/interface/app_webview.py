import webview
import os
import pyperclip
import traceback

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

    def obter_investimentos(self):
        return self.investimentos
        
    def iniciar_extracao(self):
        print("Iniciando extração do banco via robô...")
        # Import tardio (lazy import) para não atrasar a abertura da janela inicial em ~2s
        from src.extrator_banco import iniciar_navegador, verificar_login_por_qrcode, extrair_investimentos
        driver = None
        try:
            driver, wait = iniciar_navegador()
            verificar_login_por_qrcode(wait)
            dados_brutos = extrair_investimentos(driver)
            
            self.investimentos = _transformar_para_tabela(dados_brutos)
            return self.investimentos
        except Exception as e:
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
