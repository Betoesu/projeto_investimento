#Gera arquivos com as informações fornecidas

def criar_relatorio_txt(relatorio):
    with open('./data/relatorio.txt', "w", encoding="utf-8") as r:
        for item in relatorio:
            r.write(f"{item['produto']} | Taxa: {item['rendimento']} | Inv.Mínimo: {item['investimento_minimo']} | Isento de Imposto de Renda: {item["isento_ir"]} | Vencimento: {item["vencimento"]}\n")