# Lida apenas com a conexão/login e busca de dados
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def _clicar_elemento(wait, xpath):
    """Função auxiliar que aguarda elemento ficar clicável e o clica"""
    elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elemento.click()

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
    # Criamos um "wait" exclusivo de 120 segundos para dar tempo do usuário pegar o celular e ler o QRCODE
    wait_login = WebDriverWait(driver, 120) 

    wait_login.until(EC.presence_of_element_located((By.XPATH, "//*[@id='header-ib']/div/div[2]/div/div/nav[5]/ul/li/a")))

    time.sleep(3)

def navegar_para_renda_fixa(wait):

    #Clica no botão investir
    _clicar_elemento(wait,'//span[contains(text(), "Investir")]' )  

    #Caso apareça o erro de dados não cadastrados. Ele vai simplesmente fechar a aba, ir para o início e tentar novamente
    try:
        #Clica no botão que leva para renda fixa
       _clicar_elemento(wait, '//span[contains(text(), "Renda Fixa")]')

    except:

        #Caso o botao de fechar troque de lugar
        try:
            #Botão de fechar aba de dados cadastrais
            _clicar_elemento(wait,'/html/body/div[3]/div/div[1]/button')

        except:
            #Outro possível caminho para botão de fechar aba de dados cadastrais
            _clicar_elemento(wait,'/html/body/div[2]/div/div[1]/button')

        #Clica no botão de voltar para o início
        _clicar_elemento(wait,'//span[text()="Início"]')

        #Clica no botão investir
        _clicar_elemento(wait,'//span[contains(text(), "Investir")]' )

        #Caso ainda assim o erro de dados não cadastrados continue ele tenta fazer o processo de ir para o inicio e voltar novamente
        try:
            #Clica no botão que leva para renda fixa
            _clicar_elemento(wait, '//span[contains(text(), "Renda Fixa")]')

        except:
            #Clica no botão de investimento
            _clicar_elemento(wait, '//button[text()="Investimentos"]')

            #Clica no botão que leva para renda fixa
            _clicar_elemento(wait, '//span[contains(text(), "Renda Fixa")]')

def aplicar_filtros(wait):

    #Botão Filtro
    #_clicar_elemento(wait, '//*[@id="root"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/button')
    _clicar_elemento(wait, '//button[contains(text(), "Filtros")]')

    #Botão filtro CDB
    #_clicar_elemento(wait, '//*[@id="root"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[1]/ul/li[1]/span')
    _clicar_elemento(wait, '//span[contains(text(), "CDB")]')

    #Botão filtro LCI
    #_clicar_elemento(wait, '//*[@id="root"]/div[1]/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/div/div[1]/ul/li[2]/span/span')
    _clicar_elemento(wait, '//span[contains(text(), "LCI")]')

    #Botão Filtro Risco muito Baixo
    _clicar_elemento(wait, '//span[text()="Muito Baixo"]')

    #Botão Filtro Risco Baixo
    _clicar_elemento(wait, '//span[text()="Baixo"]')

    #Botão Filtro Risco Médio
    _clicar_elemento(wait, '//span[text()="Médio"]')

    #Fechar aba Filtro
    #_clicar_elemento(wait, '//*[@id="root"]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/span')
    _clicar_elemento(wait, '//span[text()="Produtos de Renda Fixa"]')

def extrair_investimentos(driver,wait):

    """Extrai os dados e retorna uma lista de dicionários."""

    # 1. ESPERA INTELIGENTE: O robô aguarda até o 1º cartão de investimento aparecer na tela
    try:
        xpath_primeiro_card = '(//div[@class="sc-kcGwyx lfvmlZ"]/div[@class="sc-edcLgS kUdxgb"])[1]'
        wait.until(EC.presence_of_element_located((By.XPATH, xpath_primeiro_card)))
    except Exception:
        # Se passar o tempo limite e não achar nada, ele segue e retorna vazio (0 produtos)
        pass

    time.sleep(1.5)
    
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
