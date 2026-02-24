from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time


def buscar_medicamento(nome_medicamento: str) -> pd.DataFrame:
    # ===============================
    # CONFIGURAÇÃO
    # ===============================
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 20)

    try:
        # ===============================
        # ACESSO AO SITE
        # ===============================
        driver.get("https://catalogo.compras.gov.br/cnbs-web/busca")

        # ===============================
        # BUSCA
        # ===============================
        campo = wait.until(
            EC.presence_of_element_located((By.XPATH, "//p-autocomplete//input"))
        )
        campo.clear()
        campo.send_keys(nome_medicamento)
        time.sleep(1)
        campo.send_keys(Keys.ENTER)

        # ===============================
        # FILTRO LATERAL
        # ===============================
        categoria = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//p-listbox//div[normalize-space()='6505-Drogas e medicamentos']"
            ))
        )
        categoria.click()
        time.sleep(2)

    except TimeoutException:
        print(f"Nenhum medicamento encontrado para: {nome_medicamento}")
        driver.quit()
        return pd.DataFrame(columns=["Código", "Nome", "Descrição", "NCM"])

    # ===============================
    # FUNÇÕES AUXILIARES
    # ===============================
    def aplicar_paginacao_se_existir():
        """
        Aplica 100 itens por página SOMENTE se o paginator existir.
        """
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        dropdowns = driver.find_elements(
            By.XPATH,
            "//p-paginator//div[contains(@class,'p-dropdown-trigger')]"
        )

        if not dropdowns:
            print("Paginator não encontrado — seguindo direto.")
            return

        dropdowns[0].click()
        time.sleep(1)

        ultima_opcao = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "(//p-dropdownitem//li[@role='option'])[last()]"
            ))
        )
        ultima_opcao.click()
        time.sleep(3)

    def obter_linhas():
        tabela = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//tbody[contains(@class,'p-datatable-tbody')]")
            )
        )
        return tabela.find_elements(By.XPATH, ".//tr")

    # ===============================
    # APLICA PAGINAÇÃO (SE HOUVER)
    # ===============================
    aplicar_paginacao_se_existir()

    # ===============================
    # LOOP PRINCIPAL
    # ===============================
    dados = []
    indice = 0

    while True:
        linhas = obter_linhas()
        total = len(linhas)

        if indice >= total:
            break

        print(f"Processando item {indice + 1}/{total}")

        linha = linhas[indice]
        botao = linha.find_element(
            By.XPATH, ".//button[normalize-space()='Selecionar']"
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", botao
        )
        time.sleep(1)
        botao.click()

        # ===============================
        # AGUARDA DETALHE
        # ===============================
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='Voltar']")
            )
        )
        time.sleep(2)

        # ===============================
        # RASPAGEM
        # ===============================
        linhas_detalhe = driver.find_elements(
            By.XPATH,
            "//tbody[contains(@class,'p-datatable-tbody')]//tr"
        )

        for l in linhas_detalhe:
            cols = l.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                dados.append({
                    "Código": cols[0].text.strip(),
                    "Nome": cols[1].find_element(By.TAG_NAME, "b").text.strip(),
                    "Descrição": cols[1].text.strip(),
                    "NCM": cols[2].text.strip()
                })

        time.sleep(2)

        # ===============================
        # VOLTAR
        # ===============================
        botao_voltar = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[normalize-space()='Voltar']")
            )
        )
        botao_voltar.click()

        # ===============================
        # AGUARDA TABELA + REAPLICA PAGINAÇÃO
        # ===============================
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//tbody[contains(@class,'p-datatable-tbody')]")
            )
        )
        aplicar_paginacao_se_existir()

        indice += 1

    # ===============================
    # DATAFRAME FINAL
    # ===============================
    df = pd.DataFrame(dados, columns=["Código", "Nome", "Descrição", "NCM"])

    driver.quit()
    return df
