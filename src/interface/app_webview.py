import webview
import os
import pyperclip
import traceback
from src.extrator_banco import iniciar_navegador, verificar_login_por_qrcode, extrair_investimentos

def _transformar_para_tabela(dados_brutos):
    tabela = []
    for item in dados_brutos:
        if item.get("grauRisco") not in (1, 2, 3): continue
        if item.get("tipo", {}).get("descricao") not in ("LCI", "LCA", "CDB"): continue

        aplicacao_minima = item.get("aplicacaoMinima", 0)
        try:
            inv_minimo = f"R$ {float(aplicacao_minima):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
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

class Api:
    def __init__(self):
        self.investimentos = []

    def obter_investimentos(self):
        return self.investimentos
        
    def iniciar_extracao(self):
        print("Iniciando extração do banco via robô...")
        try:
            driver, wait = iniciar_navegador()
            verificar_login_por_qrcode(wait)
            dados_brutos = extrair_investimentos(driver)
            driver.quit()
            
            self.investimentos = _transformar_para_tabela(dados_brutos)
            return self.investimentos
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Falha na extração: {str(e)}")

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
            texto = "\\n".join([f"{d['produto']} | {d['rendimento']} | {d['investimento_minimo']} | {d['vencimento']}" for d in dados_filtrados])
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
        return True

    def copiar_dados(self, dados_filtrados):
        print(f"Copiando {len(dados_filtrados)} produtos...")
        texto = "\\n".join([f"{d['produto']} | {d['rendimento']} | {d['investimento_minimo']} | {d['vencimento']}" for d in dados_filtrados])
        pyperclip.copy(texto)
        return True

def main():
    api = Api()
    caminho_html = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "index.html"))
    janela = webview.create_window(
        title="Painel de Investimentos", 
        url="file://" + caminho_html,
        js_api=api,
        width=1200, 
        height=700,
        background_color="#0f1319"
    )
    webview.start()

if __name__ == "__main__":
    main()
