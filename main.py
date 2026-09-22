"""Ponto de entrada principal da aplicação."""

from src.interface.app import App

def main():
    print("Iniciando a Interface do Painel de Investimentos...")
    
    # 1. Instancia a janela principal que criamos
    app = App()
    
    # 2. Inicia o "loop principal" (mantém a janela aberta e escutando cliques)
    app.mainloop()

if __name__ == "__main__":
    main()