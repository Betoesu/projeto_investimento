from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
import requests

URL_RENDA_FIXA = "rendas-fixas/produtos"
ARQUIVO_SAIDA = "resultado_renda_fixa.json"

def iniciar_navegador():
    """Configura e abre o navegador, retornando as instâncias necessárias."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    driver.get("https://contadigital.inter.co/investimento/renda-fixa")

    return driver, wait

def verificar_login_por_qrcode(wait):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Renda')]")))
    except TimeoutException as e:
        raise TimeoutException(f"Tempo esgotado. O login não foi concluído. Rode esta célula novamente após logar. Erro: {e}")

def extrair_investimentos(driver):
    """Extrai os dados e retorna uma lista de dicionários."""
    driver.requests.clear()  # limpa o histórico pra não pegar lixo de antes

    try:
        req = driver.wait_for_request(URL_RENDA_FIXA, timeout=10)
    except TimeoutException as e:
        raise TimeoutException(f"Não foi encontrado a chamada de rendas-fixas/produtos a tempo. Erro: {e}")

    auth_header = req.headers.get("authorization")
    mag_id = req.headers.get("mag-identifier")

    if not auth_header or not mag_id:
        raise RuntimeError("Headers não encontrados")

    url_api = "https://cd.web.bancointer.com.br/ib-pfj/investimentos/v2/rendas-fixas/produtos"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "authorization": auth_header,
        "mag-identifier": mag_id
    }

    resultado = requests.get(url=url_api, headers=headers)
    resultado.raise_for_status

    data = resultado.json()

    return data

def gerar_relatorio(data):
    # Salva JSON completo
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo:
        json.dump(data, arquivo, ensure_ascii=False, indent=4)
    print(f"JSON salvo em {ARQUIVO_SAIDA}")

    # Salva TXT filtrado
    count = 0
    with open("investimentos.txt", "w", encoding="utf-8") as arquivo:
        for investimento in data:
            if investimento.get("grauRisco") in [1, 2, 3] and investimento.get("tipo", {}).get("descricao") in [ "LCI", "LCA", "CDB"]:
                nome = investimento.get("nome", "")
                taxa = investimento.get("taxa", 0)
                inv_min = investimento.get("aplicacaoMinima", 0)
                isento_ir = investimento.get("isentoImpostos", None)
                vencimento = "/".join(investimento.get("dataResgate", "").split("-")[::-1])

                arquivo.write(f"{nome} | Taxa: {taxa} | Inv.Mínimo: {inv_min} | Isento de Imposto de Renda: {isento_ir} | Vencimento: {vencimento}\n")
                count += 1