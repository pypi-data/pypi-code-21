import time
import sys
from functools import partial
from multiprocessing import Pool, Process, Value, Manager

import numpy as np
import pandas as pd
from tqdm import tqdm

from selenium.common.exceptions import NoSuchFrameException, TimeoutException
from siapa_robo.siapa import Siapa

from .cancelador import *


def login_siapa(siapa, nu_cpf, senha):
    siapa.entrar(numCpf=nu_cpf, txtSenha=senha)
    return siapa

def acessa_consulta(siapa):
    MENU_CONSULTA_DEBITOS = (8, 6, 1)
    siapa.navigate_menu(*MENU_CONSULTA_DEBITOS)


def carrega_debitos():
    debitos = busca_debitos_para_baixa()
    debitos['nu_debito'] = debitos['nu_debito'].map(lambda x: str(x).zfill(8))
    debitos = debitos[['nu_rip', 'nu_debito']]
    return debitos


def envia_formulario(siapa, nu_rip):
    form = siapa.formulario()
    txt_RIP = form.fields['TextRip']
    txt_RIP.clear()
    txt_RIP.send_keys(nu_rip)
    botao_consultar = siapa.driver.find_element_by_name('Consultar')
    botao_consultar.click()


def clean_nu_debito(nu_debito):
    if pd.isnull(nu_debito):
        return None
    string = str(nu_debito)
    remove_decimal = string.replace('.0', '')
    numero = remove_decimal.zfill(8)
    return numero


def historico_debitos_cancelados(siapa):
    siapa.driver.switch_to_default_content()
    siapa.driver.switch_to_frame('Principal')
    siapa.driver.switch_to_frame('Dados_Principais')
    tabela = siapa.tables()[1]
    tabela['nu_debito'] = tabela['Nro Débito'].apply(clean_nu_debito)
    tabela['nu_debito'] = tabela['nu_debito'].fillna(method='ffill')
    tabela.rename(columns={'Valor na Data Base Calculo': 'situacao'},
                  inplace=True)
    CANCELADOS_PARC_MANUAL = 'CANC.PARC.MAN.'
    hist_cancelados = tabela.query(f'situacao == "{CANCELADOS_PARC_MANUAL}"')
    siapa.driver.switch_to_default_content()
    return hist_cancelados[['nu_debito', 'situacao']]

def valida_debitos():
    dados = tabelas[1]


def valida_rip(siapa, debitos, nu_rip):
    envia_formulario(siapa, nu_rip)
    try:
        historico = historico_debitos_cancelados(siapa)
    except (ValueError, NoSuchFrameException):
        ERRO_6904 = '6904 - RETORNO ANORMAL DO ACESSO AO TS'
        if ERRO_6904 in siapa.driver.page_source:
            siapa.driver.find_element_by_name('Voltar').click()
            envia_formulario(siapa, nu_rip)
            historico = historico_debitos_cancelados(siapa)


    debitos_rip = debitos.query(f'nu_rip == "{nu_rip}"')['nu_debito'].values

    for dbt in debitos_rip:
        if not dbt in historico['nu_debito'].values:
            raise AssertionError(f'RIP: {nu_rip} - Débito: {dbt} não cancelado.')
            sys.exit(1)
    siapa.driver.back()


def crash_recover(siapa, nu_cpf, senha, debitos, nu_rip):
    siapa.driver.quit()
    siapa = login_siapa(siapa, nu_cpf, senha)
    acessa_consulta(siapa)
    valida_rip(siapa, debitos, nu_rip)

def debitos_para_baixar():
    debitos = carrega_debitos()
    debitos = exclui_debitos_baixados(debitos)
    debitos.reset_index(inplace=True)
    return debitos


def fatia_dataframe(df, n):
    ''' Divide o dataframe em n partes e retorna uma lista de n dataframes '''
    tamanho_fatia = len(df) // n
    fatias = [i for g, i in df.groupby(np.arange(len(df)) // tamanho_fatia)]
    print('FATIAS', sum([len(i) for i in fatias]))
    return fatias


def login_siapa_abre_consulta(nu_cpf, senha):
    try:
        siapa = Siapa(headless=False)
        login_siapa(siapa, nu_cpf, senha)
        acessa_consulta(siapa)
    except(TimeoutException) as err:
        siapa.driver.quit()
        siapa = login_siapa_abre_consulta(nu_cpf, senha)
    else:
        return siapa


def processo(nu_cpf, senha, counter, debitos):
    siapa = login_siapa_abre_consulta(nu_cpf, senha)

    rips = debitos['nu_rip'].unique()

    #with tqdm(total=qtd_rips, unit='RIP') as pbar:
    for nu_rip in rips:
        try:
            valida_rip(siapa, debitos, nu_rip)
        except (ValueError, NoSuchFrameException, UnboundLocalError):
            while True:
                try:
                    crash_recover(siapa, nu_cpf, senha, debitos, nu_rip)
                except:
                    pass
                else:
                    break

        with counter.get_lock():
            counter.value += 1

    siapa.driver.quit()
    return


def pbar(total, counter):
    with tqdm(total=total) as barra:
        while counter.value <= total + 1:
            barra.update(counter.value - barra.n)
    return

def main_multprocess(nu_cpf, senha):
    print(' - Iniciando validação do processo de cancelamento dos '
          'débitos parcelados.')
    debitos = debitos_para_baixar()
    N_PROCESSOS = 4
    chunks = fatia_dataframe(debitos, N_PROCESSOS)
    qtd_rips = len(debitos['nu_rip'].unique())
    print(f' - {qtd_rips} imóveis contendo {len(debitos)} débitos selecionados '
          'para validação.')

    counter = Value('i', 0)

    p1 = Process(target=processo, args=(nu_cpf, senha, counter, chunks[0]))
    p2 = Process(target=processo, args=(nu_cpf, senha, counter, chunks[1]))
    p3 = Process(target=processo, args=(nu_cpf, senha, counter, chunks[2]))
    p4 = Process(target=processo, args=(nu_cpf, senha, counter, chunks[3]))
    bar = Process(target=pbar, args=(qtd_rips, counter))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    bar.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    bar.join()

    print(' - Validação realizada com sucesso. Todos os débitos estão cancelados.')
    sys.exit(0)
    return 0


def main(nu_cpf, senha):
    print(' - Iniciando validação do cancelamento dos débitos parcelados.')
    siapa = Siapa(headless=True)
    print(f' - Efetuando login no Siapa como {nu_cpf}.')
    login_siapa(siapa, nu_cpf, senha)
    acessa_consulta(siapa)

    print(f' - Buscando lista de débitos parcelados para validação.')
    debitos = carrega_debitos()
    print(f' - Excluindo os débitos já cancelados na base Siapa.')
    debitos = exclui_debitos_baixados(debitos)

    rips = debitos['nu_rip'].unique()
    print(f' - Processando {len(debitos)} débitos encontrados em {len(rips)} imóveis.')

    with tqdm(total=len(rips), unit='RIP') as pbar:
        for nu_rip in rips:
            try:
                valida_rip(siapa, debitos, nu_rip)
            except (NoSuchFrameException, ValueError) as err:
                print('\n', err, '- Ativando o Crash Recover')
                crash_recover(siapa, nu_cpf, senha, debitos, nu_rip)
            finally:
                pbar.update(1)

    siapa.driver.quit()
    print(' - Validação realizada com sucesso. Todos os débitos estão cancelados.')
    return 0
