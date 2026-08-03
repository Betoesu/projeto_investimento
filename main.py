from src.extrator_banco import (
    iniciar_navegador, 
    realizar_login_por_qrcode, 
    navegar_para_renda_fixa, 
    aplicar_filtros, 
    extrair_investimentos
)
from src.gerador_relatorio import criar_relatorio_txt

def executar_automacao():
    print("Iniciando robô de invetimentos...")
    
    # 1. Setup
    driver, wait = iniciar_navegador()

    # 2. Navegação
    realizar_login_por_qrcode(driver)
    navegar_para_renda_fixa(wait)
    aplicar_filtros(wait)

    # 3. Extração de dados
    print("Extraindo dados...")
    dados_investimentos = extrair_investimentos(driver,wait)

    # 4. Resultado
    print(f"\nForam encontrados {len(dados_investimentos)} investimentos!\n")
    for item in dados_investimentos:
        print(f"-> {item['produto']} | Taxa: {item['rendimento']} | Inv.Mínimo: {item['investimento_minimo']} | Isento de Imposto de Renda: {item['isento_ir']} | Vencimento: {item['vencimento']}")

    criar_relatorio_txt(dados_investimentos)

if __name__ == "__main__":
    executar_automacao()   