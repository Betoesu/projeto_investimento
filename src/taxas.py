import requests

# Começam como None para sabermos que ainda não foram buscadas
TAXA_ANUAL_CDI = None
TAXA_ANUAL_IPCA = None

def _garantir_taxas():
    """Bate na API apenas se for a primeira vez. Depois, usa a memória."""
    global TAXA_ANUAL_CDI, TAXA_ANUAL_IPCA
    
    # Se já tem os dados salvos, encerra a função instantaneamente
    if TAXA_ANUAL_CDI is not None and TAXA_ANUAL_IPCA is not None:
        return

    try:
        response = requests.get("https://brasilapi.com.br/api/taxas/v1", timeout=5)
        response.raise_for_status()
        dados_api = response.json()
        
        for item in dados_api:
            if item.get("nome") == "CDI":
                TAXA_ANUAL_CDI = float(item.get("valor"))
            elif item.get("nome") == "IPCA":
                TAXA_ANUAL_IPCA = float(item.get("valor"))
                
    except Exception:
        # Se estiver sem internet, zera as taxas para a ordenação não quebrar (dar erro)
        TAXA_ANUAL_CDI = 0.0
        TAXA_ANUAL_IPCA = 0.0

def calcular_cdi_anual(porcentagem):
    """Calcula o rendimento de % do CDI."""
    _garantir_taxas() # Garante que temos a taxa antes de calcular
    return round((porcentagem / 100) * TAXA_ANUAL_CDI, 2)

def calcular_ipca_anual(porcentagem_ipca):
    """Calcula o rendimento de IPCA + %."""
    _garantir_taxas() # Garante que temos a taxa antes de calcular
    
    porc_taxa_ipca = (TAXA_ANUAL_IPCA / 100) + 1
    porcentagem_ipca_f = (porcentagem_ipca / 100) + 1

    return round(((porcentagem_ipca_f * porc_taxa_ipca) - 1) * 100, 2)