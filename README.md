# 📊 Painel de Investimentos (Renda Fixa - Banco Inter)

Aplicação desktop interativa para extração, visualização, filtragem e exportação de produtos de Renda Fixa (**CDB, LCI e LCA**) diretamente da plataforma do Banco Inter.

O sistema automatiza a coleta de dados interceptando a comunicação com a API oficial após a autenticação do usuário via QR Code e apresenta as oportunidades em um painel moderno construído com **PyWebView**.

---

## ✨ Funcionalidades

- **Extração Automatizada**: Abre o navegador controlado via Selenium/Selenium-Wire, aguarda o login seguro por QR Code e captura os dados atualizados diretamente da API do Banco Inter.
- **Filtragem Inteligente**: Filtra automaticamente produtos de Renda Fixa elegíveis (`CDB`, `LCI`, `LCA`) com grau de risco baixo/médio (1 a 3).
- **Interface Gráfica Moderna**: Painel visual responsivo renderizado via WebView integrado ao Python.
- **Cálculo de Taxas (BrasilAPI)**: Integração com a BrasilAPI para consulta das taxas anuais de **CDI** e **IPCA** em tempo real.
- **Exportação Rápida**:
  - Salve os resultados filtrados em arquivos `.txt` organizados com data e hora.
  - Copie os dados diretamente para a área de transferência (Clipboard) com um clique.

---

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
- **Python 3.10+** (Recomendado: Python 3.13)
- **Google Chrome** instalado (utilizado pelo WebDriver para realizar a autenticação no banco)
- Conta ativa no **Banco Inter** com o aplicativo instalado no celular (para leitura do QR Code)

---

## 🚀 Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/Betoesu/projeto_investimento.git
cd projeto_invest
```

### 2. Criar e ativar o ambiente virtual (`.venv`)

No **Windows (PowerShell)**:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No **Windows (CMD)**:
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

No **Linux / macOS**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências
Com o ambiente virtual ativado, instale os pacotes necessários listados no `requirements.txt`:

```bash
pip install -r requirements.txt
```

> **Nota sobre compatibilidade (Python 3.12+):** O `selenium-wire` depende do módulo `setuptools` (que fornece o `pkg_resources`) e de versões específicas de `blinker`, `cryptography` e `pyOpenSSL`, já devidamente fixadas no arquivo `requirements.txt`.

---

## ▶️ Como Rodar o Programa
Confira se está com o venv ativado, caso não esteja rode:

```bash
.\.venv\Scripts\Activate.ps1
```

Para iniciar o painel principal conectado ao extrator do Banco Inter, execute na raiz do projeto:

```bash
python main.py
```

### Passo a passo de uso:
1. Ao abrir a janela do **Painel de Investimentos**, clique no botão para iniciar a extração/busca.
2. Uma janela do **Google Chrome** será aberta automaticamente na página do Banco Inter.
3. Faça o login na sua conta lendo o **QR Code** com o aplicativo do Banco Inter no seu celular.
4. Assim que o login for concluído e a página de Renda Fixa carregar, o robô capturará os produtos automaticamente, fechará o navegador e preencherá a tabela no painel.
5. Utilize os filtros na tela, copie os dados ou clique em **Exportar TXT** para salvar o relatório na sua máquina.

---

## 📁 Estrutura do Projeto

```text
projeto_invest/
├── src/
│   ├── interface/
│   │   ├── web/
│   │   │   └── index.html          # Frontend do painel (HTML/CSS/JS)
│   │   └── app_webview.py          # Ponte Python <-> JS (PyWebView) e ações da UI
│   ├── extrator_banco.py           # Automação Selenium-Wire e requisição à API do Inter
│   └── taxas.py                    # Consulta de taxas CDI e IPCA via BrasilAPI
├── main.py                         # Ponto de entrada principal da aplicação
└── requirements.txt                # Dependências do projeto
```

---

## 🧰 Tecnologias Utilizadas

- **[PyWebView](https://pywebview.flowrl.com/)**: Criação da janela nativa desktop renderizando interface web (HTML/CSS/JS).
- **[Selenium](https://www.selenium.dev/) & [Selenium-Wire](https://github.com/wkeeling/selenium-wire)**: Automação do navegador e interceptação de cabeçalhos de autenticação (`Authorization` e `mag-identifier`).
- **[Requests](https://docs.python-requests.org/)**: Consumo direto das APIs do Banco Inter e da BrasilAPI.
- **[Pyperclip](https://pypi.org/project/pyperclip/)**: Integração com a área de transferência do sistema.
