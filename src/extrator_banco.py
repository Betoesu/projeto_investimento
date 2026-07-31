# Lida apenas com a conexão/login e busca de dados
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def iniciar_navegador():
    """Configura e abre o navegador, retornando as instâncias necessárias."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    return driver, wait

def realizar_login_por_qrcode(driver):
    driver.get("https://contadigital.inter.co/home")
    resposta = input("Digite 'continuar' ao terminar de scanear o QR CODE: ").lower().strip()

    while resposta != "continuar":
        resposta = input("Digite exatamente 'continuar: '").lower().strip()

def navegar_para_renda_fixa(wait):
    botao_investir = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='header-ib']/div/div[2]/div/div/nav[5]/ul/li/a")))
    botao_investir.click()
    try:
        botao_renda_fixa = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div[1]/div[3]/div[1]/div/div[2]/div/div/div[1]/section/button")))
        botao_renda_fixa.click()
    except:

        #Caso o botao de fechar troque de lugar
        try:
            botao_fechar_dados_cadastrais = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div[1]/button")))
            botao_fechar_dados_cadastrais.click()
        except:
            botao_fechar_dados_cadastrais = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[1]/button")))
            botao_fechar_dados_cadastrais.click()

        botao_inicio = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='header-ib']/div/div[2]/div/div/nav[1]/ul/li/a/span[2]")))
        botao_inicio.click()

        botao_investir = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='header-ib']/div/div[2]/div/div/nav[5]/ul/li/a")))
        botao_investir.click()
        try:
            botao_renda_fixa = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div[1]/div[3]/div[1]/div/div[2]/div/div/div[1]/section/button")))
            botao_renda_fixa.click()
        except:
            botao_investimento = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='header-ib']/div/div[2]/div/div/nav[5]/ul/li/div/div/div/ul/li[1]/button")))
            botao_investimento.click()

            botao_renda_fixa = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div[1]/div[3]/div[1]/div/div[2]/div/div/div[1]/section/button")))
            botao_renda_fixa.click()

def aplicar_filtros(wait):
        
    botao_filtro = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/button")))
    botao_filtro.click()

    botao_filtro_cdb = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[1]/ul/li[1]/span")))
    botao_filtro_cdb.click()

    botao_filtro_lci = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[1]/ul/li[2]/span/span")))
    botao_filtro_lci.click()

    botao_filtro_risco_muito_baixo = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[5]/ul/li[1]/span/span')))
    botao_filtro_risco_muito_baixo.click()

    botao_filtro_risco_baixo = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[5]/ul/li[2]/span/span')))
    botao_filtro_risco_baixo.click()

    botao_filtro_risco_medio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[5]/ul/li[3]/span/span')))
    botao_filtro_risco_medio.click()

    #Fechar aba Filtro
    botao_produto_renda_fixa = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/span')))
    botao_produto_renda_fixa.click()

def extrair_investimentos(driver,wait):
    """Extrai os dados e retorna uma lista de dicionários."""

    #Aguarda site renderizar lista de investimentos
    time.sleep(3)

    lista_investimentos = driver.find_elements(By.XPATH, '//div[@class="sc-kcGwyx lfvmlZ"]/div[@class="sc-edcLgS kUdxgb"]')
    quantidade_investimentos = len(lista_investimentos)

    dados_extraidos = []

    for i in range(1, quantidade_investimentos + 1):
        try:
            xpath_card_atual = f'(//div[@class="sc-kcGwyx lfvmlZ"]/div[@class="sc-edcLgS kUdxgb"])[{i}]'

            investimento = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_card_atual)))
           
            texto = investimento.find_element(By.XPATH, './/span[@class="sc-kLeMFj cNbGSK"]').text

            rendimento = investimento.find_element(By.XPATH, './/span[@class="sc-cBULEp cFVmFq"]').text

            inv_minimo = investimento.find_element(By.XPATH, './/section[@class="sc-ipiWPc UJOeJ"]//span[contains(text(), "R$")]').text.replace("\xa0", " ")

            selo_isencao = investimento.find_elements(By.XPATH, './/span[contains(text(), "Isento de Impostos")]')
            if len(selo_isencao) > 0:
                isento_ir = True   #selo_isencao[0].text se quiser o texto
            else:
                isento_ir = False

            vencimento = investimento.find_element(By.XPATH, './/section[@class="sc-ipiWPc UJOeJ"]//span[contains(text(), "/")]').text
            
            
            dados_extraidos.append({
                "produto": texto,
                "rendimento": rendimento,
                "investimento_minimo": inv_minimo,
                "isento_ir":isento_ir,
                "vencimento":vencimento,
            })
            
            
        except Exception:
            continue

    return dados_extraidos