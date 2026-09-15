from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json


#TEMPORARIO 
import sys
import os
# Volta uma pasta (..) e adiciona a raiz do projeto ao radar do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.extrator_banco import navegar_para_renda_fixa

URL_RENDA_FIXA = "rendas-fixas/produtos"
ARQUIVO_SAIDA = "resultado_renda_fixa.json"


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

driver.get("https://contadigital.inter.co/home")

try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Saldo')]")))

except TimeoutException:
    print("Tempo esgotado ou elemento não encontrado. O login não foi concluído.")
    driver.quit()
    exit()


print("Login detectado com sucesso! Indo para renda fixa...")

driver.requests.clear() # limpa o histórico pra não pegar lixo de antes
navegar_para_renda_fixa(wait)

print("\nCapturando tokens...")
try:
    req = driver.wait_for_request(URL_RENDA_FIXA, timeout=20)
except TimeoutException:
    print("Não encontrei a chamada de rendas-fixas/produtos a tempo.")
    driver.quit()
    exit()

auth_header = req.headers.get("authorization")
mag_id = req.headers.get("mag-identifier")

if not auth_header or not mag_id:
    print("A requisição apareceu, mas sem os headers esperados.")
    driver.quit()
    exit()

print("Headers capturados com sucesso!")

js_code = """
const [url, token, magId, done] = arguments;
fetch(url, {
    method: 'GET',
    headers: {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': token,
        'mag-identifier': magId
    }
})
.then(async response => {
    if (!response.ok) {
        const text = await response.text();
        done({ success: false, status: response.status, error: text });
    } else {
        done({ success: true, status: response.status, data: await response.json() });
    }
})
.catch(err => done({ success: false, error: err.toString() }));
"""

url_api = "https://cd.web.bancointer.com.br/ib-pfj/investimentos/v2/rendas-fixas/produtos"

  
resultado = driver.execute_async_script(js_code, url_api, auth_header, mag_id)
data = resultado["data", {}]

if resultado.get("success"):
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo:
        json.dump(data, arquivo, ensure_ascii=False, indent=4)
    print("Sucesso! Dados salvos.")

    for investimento in data: 
        if data["grauRisco"] == 1 or 2 or 3 and data["indexador"]["descricacao"] == "DI" or "LCI" or "LCA":
            nome = data.get("nome", "")
            taxa = data.get("taxa", 0)
            inv_min = data.get("aplicacaoMinima", 0)
            isento_ir = data.get("isentoImpostos", None)
            vencimento = "/".join(data.get("dataResgate", "").split("-")[::-1])

    

else:
    print("Erro:", resultado.get("error"))