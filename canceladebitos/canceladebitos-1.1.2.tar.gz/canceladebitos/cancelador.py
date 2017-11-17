'''
    Busca os débitos parcelados no banco de dados do SPUnet e faz o
    cancelamento no SIAPA.
'''

from collections import namedtuple
import logging
import os
import sys

import pandas as pd
import psycopg2
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm
from siapa_robo import Siapa

from .bancodedados import Parcelamento
from .dadossiapa import busca_debitos_cancelados, busca_uf_rip


__all__ = ['ClasseDebito', 'busca_uf_rip', 'marca_uf_debitos',
           'busca_debitos_para_baixa', 'Cancelador', 'exclui_debitos_baixados']


ERROS_SIAPA = {'5045': '5045 - SITUACAO DO DEBITO NAO PERMITE CANCELAMENTO',
               '5022': '5022 - DEBITO INFORMADO TEM RECEITA ORDINARIA'}


class ClasseDebito():
    ORDINARIO = 'Ordinário'
    EXTRAORDINARIO = 'Extraordinário'

    def __init__(self):
        pass

    @property
    def classes(self):
        '''
            Classes de receita do SIAPA.
        '''
        nomes_classes = [self.ORDINARIO, self.EXTRAORDINARIO]
        classes_debitos = namedtuple('classes_debitos', nomes_classes)
        return classes_debitos(('2073', '2090'), ('2081', '9136'))

    def classifica(self, co_receita):
        ''' Classifica um código de receita como extraordinário ou
            ordinário.
        '''
        for codigos, classe_debito in zip(self.classes, self.classes._fields):
            if co_receita in codigos:
                classificacao = classe_debito
                break
        else:
            raise ValueError('Código desconhecido {}'.format(co_receita))

        return classificacao


def seleciona_menu(siapa, classe_debito):
    #menu = {ClasseReceita.ordinaria: 3, ClasseReceita.extraordinaria: 6}
    menu = {ClasseDebito.ORDINARIO: 3, ClasseDebito.EXTRAORDINARIO: 6}
    siapa.navigate_menu(8, 1, menu[classe_debito])
    titulo = siapa.driver.find_element_by_tag_name('p').text
    assert classe_debito in titulo
    return None


def marca_uf_debitos(dataframe_debitos):
    df = dataframe_debitos.copy()
    df['nu_rip'] = df['nu_rip'].map(lambda x: x[:11])
    uf_rip = busca_uf_rip()
    marcados = df.merge(uf_rip, how='left', on='nu_rip')
    assert not marcados['uf_rip'].isnull().any()
    return marcados


def busca_debitos_para_baixa():
    '''
    Retorna dataframe contendo os débitos referentes às operações de
    parcelamento já deferidas.
    '''
    p = Parcelamento()
    deferidos = p.filtra_parcelamentos(situacao='Deferido')
    qtd_deferidos = len(deferidos)
    #print(f'Encontrados {qtd_deferidos} parcelamentos deferidos.')

    debitos_deferidos = p.tb_debitos_parcelados.merge(
            deferidos, how='inner', on='id_parcelamento')
    #print(f'Encontrados {len(debitos_deferidos)} débitos referentes a parcelamentos deferidos.')


    lista_final = marca_uf_debitos(debitos_deferidos)

    lista_final['classe_receita'] = lista_final['id_tiporeceita'].map(ClasseDebito().classifica)

    cols = ['nu_debito', 'nu_rip', 'uf_rip', 'classe_receita', 'id_parcelamento']
    lista_final = lista_final[cols].sort_values(by=['uf_rip', 'id_parcelamento'])
    return lista_final


def exclui_debitos_baixados(df):
    '''
    Exclui da tabela de débitos para baixa os débitos que já estão cancelados
    na base Siapa.
    '''
    cancelados = busca_debitos_cancelados()
    nao_baixados = df[~df['nu_debito'].isin(cancelados)]
    return nao_baixados


def cancela_debito(siapa, nu_debito):
    try:
        form = siapa.formulario()
    except TimeoutException:
        logging.error('Não foi possível carregar o formulário. Saindo do '
                      'programa.')
        raise TimeoutException

    campos = form.fields
    campos['TextDeb'].clear()
    campos['TextDeb'].send_keys(nu_debito)

    campos['TextMot'].options[7].click()

    campos['TextProc'].clear()
    nu_processo_sei = '04905002144201714'
    campos['TextProc'].send_keys(nu_processo_sei)

    form.submit()

    #verifica se houve erro. Informa o erro e passa para o próximo débito.
    try:
        erro_siapa = siapa.driver.find_element_by_tag_name('li')
        if erro_siapa:
            msg_erro = erro_siapa.text
            botao_voltar = 'Voltar'
            siapa.driver.find_element_by_name(botao_voltar).click()
            return msg_erro[:4]
    except:
        BOTAO_CONFIRMAR = 'Desistir'  # botão possui o nome errado no Siapa
        siapa.driver.find_element_by_name(BOTAO_CONFIRMAR).click()

        botao_voltar = 'Retorna'
        siapa.driver.find_element_by_name(botao_voltar).click()

        return True


def crash_recover(siapa, cpf, senha, UF, tipo_debito):
    ''' Reabre o Siapa e retorna para a tela de alteração de débito '''
    print('\nAtivando o Crash Recover.')
    siapa.driver.close()
    siapa.entrar(numCpf=cpf, txtSenha=senha)
    siapa.trocar_GRPU(UF)
    seleciona_menu(siapa, tipo_debito)


def busca_debitos_UF(sigla_UF, dataframe):
    ''' Busca os débitos ordinário e extraordinarios da UF selecionada '''

    debitos_UF = dataframe.query(f'uf_rip == "{sigla_UF}"')

    query_receita_ord = f'classe_receita == "{ClasseDebito.ORDINARIO}"'
    ordinarios = debitos_UF.query(query_receita_ord)

    query_receita_ext = f'classe_receita == "{ClasseDebito.EXTRAORDINARIO}"'
    extraordinarios = debitos_UF.query(query_receita_ext)
    return ordinarios, extraordinarios


def cancela_lista_debitos(siapa, df, classe_debito, UF, pbar):
    ''' Realiza o cancelamento de todos os débitos de uma determinada classe
    contidos em um dataframe '''
    qtd_debitos = len(df)
    if qtd_debitos > 0:
        msg = f'{UF} - Iniciando a baixa de {qtd_debitos} débitos {classe_debito}.'
        logging.info(msg)

        try:
            seleciona_menu(siapa, classe_debito)
        except TimeoutException:
            crash_recover(siapa, nu_cpf, txt_senha, UF, classe_debito)

        for row in df.iterrows():
            dados = row[1]
            try:
                status = cancela_debito(siapa, dados.nu_debito)
            except (NoSuchElementException, TimeoutException):
                logging.info(f'Erro. Ativado o crash recover')
                crash_recover(siapa, nu_cpf, txt_senha, UF, classe_debito)

                logging.info(f'Efetuando nova tentativa')
                status = cancela_debito(siapa, dados.nu_debito)

            if status in ERROS_SIAPA:
                msg = f'{UF} - {dados.nu_debito} - {ERROS_SIAPA[status]}'
                logging.info(msg)
            elif status is True:
                msg = f'{UF} - {dados.nu_debito} - Transação efetuada com sucesso.'
                logging.info(msg)
            else:
                msg = f'{UF} - {dados.nu_debito} - Status inesperado {status}.'
                logging.error(msg)
                raise EnvironmentError(msg)

            pbar.update(1)

        logging.info(f'{UF} - Todos os débitos ordinários processados com sucesso.')
        botao_menu = 'Voltar'
        try:
            siapa.driver.find_element_by_name(botao_menu).click()
        except NoSuchElementException:
            siapa.entrar(nu_cpf, txt_senha)
            #crash_recover(siapa, nu_cpf, txt_senha, UF, classe_debito)
    else:
        logging.info(f'{UF} - UF não possui débitos {classe_debito} para cancelamento.')
        return


def Cancelador(cpf, senha):
    ''' Função principal da rotina '''
    global nu_cpf
    global txt_senha

    nu_cpf = cpf
    txt_senha = senha

    logging.basicConfig(filename='log.txt', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    debitos = busca_debitos_para_baixa()
    print(' - Excluindo os débitos já cancelados na base Siapa.')
    debitos = exclui_debitos_baixados(debitos)

    qtd_debitos = len(debitos)
    msg_qtd_debitos = f' - Encontrados {qtd_debitos} débitos para cancelamento.'
    print(msg_qtd_debitos)
    logging.info(msg_qtd_debitos)

    spu_com_operacoes = debitos['uf_rip'].unique()

    msg_inicializa = ' - Inicializando o Siapa.'
    logging.info(msg_inicializa)
    print(msg_inicializa)
    siapa = Siapa(headless=False)

    msg_login = f' - Efetuando login no Siapa como {cpf}.'
    logging.info(msg_login)
    print(msg_login)
    siapa.entrar(numCpf=nu_cpf, txtSenha=txt_senha)

    for UF in spu_com_operacoes:
        logging.info(f'{UF} - INICIANDO O PROCESSAMENTO')

        siapa.trocar_GRPU(UF)
        logging.info(f'{UF} - GRPU alterada para com sucesso.')

        ordinarios_UF, extraordinarios_UF = busca_debitos_UF(UF, dataframe=debitos)

        # Remove os débitos já cancelados na base Siapa
        qtd_ordinarios = len(ordinarios_UF)
        qtd_extraordinarios = len(extraordinarios_UF)
        logging.info(f'{UF} - Ordinários: {qtd_ordinarios} Extraordinários: {qtd_extraordinarios}')


        with tqdm(total=qtd_ordinarios + qtd_extraordinarios) as pbar:
            cancela_lista_debitos(
                siapa, ordinarios_UF, ClasseDebito.ORDINARIO, UF, pbar)
            logging.info(f'Retornou ao menu principal.')

            cancela_lista_debitos(
                siapa, extraordinarios_UF, ClasseDebito.EXTRAORDINARIO,
                UF, pbar)
            logging.info(f'Retornou ao menu principal.')

        logging.info(f'{UF} - TODOS DÉBITOS PROCESSADOS.')

    msg_fim = f' - Cancelamento realizado com sucesso. Todas UF processadas.'
    logging.info(msg_fim)
    print(msg_fim)

    return True
