""# -*- coding: utf-8 -*
'''
    Consulta automatizada ao SIAPA
'''

from collections import namedtuple
from getpass import getpass
import os
import sys
import time

from brazilnum.cpf import validate_cpf
import colorama
from colorama import Fore, Style
import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException,
                                        NoSuchFrameException, TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .exceptions import *
from .form_filler import Form


__all__ = ["SPU", "Siapa", "dados_login"]


UF = namedtuple('SPU', ['code', 'name'])

SPU = {"SPUDF": UF("0111", "SPU - DISTRITO FEDERAL"),
       "DF": UF("0110", "DISTRITO FEDERAL"),
       "GO": UF("0120", "GOIAS"),
       "MT": UF("0130", "MATO GROSSO"),
       "MS": UF("0140", "MATO GROSSO DO SUL"),
       "PA": UF("0210", "PARA"),
       "AM": UF("0220", "AMAZONAS"),
       "CE": UF("0310", "CEARA"),
       "MA": UF("0320", "MARANHAO"),
       "PI": UF("0330", "PIAUI"),
       "PE": UF("0410", "PERNAMBUCO"),
       "RN": UF("0420", "RIO GRANDE DO NORTE"),
       "PB": UF("0430", "PARAIBA"),
       "AL": UF("0440", "ALAGOAS"),
       "BA": UF("0510", "BAHIA"),
       "SE": UF("0520", "SERGIPE"),
       "MG": UF("0610", "MINAS GERAIS"),
       "RJ": UF("0710", "RIO DE JANEIRO"),
       "ES": UF("0720", "ESPIRITO SANTO"),
       "SP": UF("0810", "SAO PAULO"),
       "PR": UF("0910", "PARANA"),
       "SC": UF("0920", "SANTA CATARINA"),
       "RS": UF("1010", "RIO GRANDE DO SUL"),
       "AC": UF("0230", "ACRE"),
       "AP": UF("0240", "AMAPA"),
       "RO": UF("0250", "RONDONIA"),
       "RR": UF("0260", "RORAIMA"),
       "TO": UF("0150", "TOCANTINS")}


class Siapa():
    def __init__(self, headless=False):
        colorama.init()
        self.headless = headless

    def entrar(self, numCpf=None, txtSenha=None, modo='producao'):
        if numCpf is None and txtSenha is None:
            numCpf, txtSenha = dados_login()

        self.driver = set_chrome(headless=self.headless)

        #self.driver.implicitly_wait(1.5)
        # Abre o navegador e acessa o site do SIAPA
        url = "https://www.siapa.spu.planejamento.gov.br/"
        urlhom = "http://www.siapahom.serpro.gov.br/"

        # verifica o modo de homologacao
        if modo == 'homologacao':
            self.driver.get(urlhom)
        elif modo == 'producao':
            self.driver.get(url)

        self.driver.switch_to_frame("Principal")

        formulario = self.formulario()
        formulario.fields['TxtNuCpf'].send_keys(numCpf)
        formulario.fields['TxtSenha'].send_keys(txtSenha)
        formulario.submit()

        login_sucess = 'Consultar' in self.driver.page_source
        if login_sucess:
            return

        def verifica_erro_ja_logado():
            try:
                self.driver.find_element(By.XPATH, "//a[text()='Financeiro']")
            except NoSuchElementException:
                return False
            return True

        try:
            error = self.driver.find_element_by_tag_name('li')

            if error.text == 'USUARIO NAO CADASTRADO':
                msg = 'Usuário {numCpf} não cadastrado.'
                raise UsuarioNaoCadastrado(msg)

            if error.text == 'SENHA NAO OK':
                print(Fore.RED + "Senha inválida. Execute o programa novamente "
                      "com a senha correta." + Style.RESET_ALL)
                raise SenhaInvalida
        except TimeoutException:
            pass


        ''' Caso o SIAPA informe que o usuário já está logado,
        retorna e tenta o login novamente'''
        if not verifica_erro_ja_logado():
            self.driver.back()
            self.driver.switch_to_frame("Principal")
            formulario = self.formulario()
            formulario.fields['TxtNuCpf'].send_keys(numCpf)
            formulario.fields['TxtSenha'].send_keys(txtSenha)
            formulario.submit()

            self.driver.implicitly_wait(0)

    def voltar(self, n=1):
        for i in range(0, n):
            self.driver.back()

    def sair(self):
        self.driver.close()

    def navigate_menu(self, option1, option2=None, option3=None):
        def click_menu(xpath):
            TIMEOUT = 5
            wait = WebDriverWait(self.driver, TIMEOUT)
            wait.until(EC.visibility_of_element_located((By.XPATH,
                                                         xpath))).click()

        try:
            self.driver.switch_to_frame("Principal")
        except NoSuchFrameException:
            pass

        menu_options = []

        menu = f"//*[@id='cabec'][{option1}]"
        menu_options.append(menu + "/a")

        if option2 is not None:
            sub_menu1 = f"{menu}/ul/li[{option2}]"
            menu_options.append(sub_menu1 + "/a")

        if option3 is not None:
            sub_menu2 = f"{sub_menu1}/ul/li[{option3}]"
            menu_options.append(sub_menu2 + "/a")

        for option in menu_options:
            click_menu(option)

    def trocar_GRPU(self, sigla_UF):
        codigo_UF = SPU[sigla_UF].code
        self.navigate_menu(12)

        # aguarda o campo
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "CboGRPU")))

        # busca as opções e seleciona
        opcoes = self.driver.find_elements_by_tag_name("option")
        for opt in opcoes:
            if opt.text.strip().startswith(codigo_UF):
                opt.click()

        # clica no botaão selecionar
        self.driver.find_element_by_name("Avancar").click()
        print(f"GRPU alterada para {sigla_UF} com sucesso.")

    def formulario(self):
        try:
            self.driver.switch_to_frame("Principal")
        except NoSuchFrameException:
            pass
        formulario = Form(self.driver)
        return formulario

    def links(self):
        ''' Seleciona apenas o links que não estão vinculados a botões utili-
        zando a presença do atributo onmouseover como filtro '''
        try:
            self.driver.switch_to_frame("Principal")
        except NoSuchFrameException:
            pass
        page_links = self.driver.find_elements_by_tag_name("a")
        links_list = [l for l in page_links if l.get_attribute("onmouseover") is None]
        return links_list

    def tables(self):
        html = self.driver.page_source
        tabs = pd.read_html(html, header=0, decimal=",", thousands=".")
        return tabs


def set_chrome(path=None, headless=False):
    CHROME_DRIVER = path or 'chromedriver.exe'

    # Configura o browser.
    chrome_options = Options()
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--ignore-certificate-errors')

    if headless is True:
        HEADLESS = '--headless'
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(HEADLESS)

    if os.name == 'posix':
        driver = Chrome(chrome_options=chrome_options)
    else:
        driver = Chrome(CHROME_DRIVER, chrome_options=chrome_options,
                        service_args=['--verbose'],service_log_path='driver.log')

    return driver


def dados_login():
    while True:
        cpfServidor = input("Informe o CPF e tecle ENTER: ")
        if validate_cpf(cpfServidor) is True:
            break
        else:
            print(f"{cpfServidor} não é um número de CPF válido.")

    senhaServidor = getpass(prompt="Informe a senha e tecle ENTER: ")
    return cpfServidor, senhaServidor
