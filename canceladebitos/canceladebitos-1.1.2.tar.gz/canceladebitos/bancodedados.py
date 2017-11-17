'''
    Acessa o banco de dados do SPUNET e busca as informações das operações
    de parcelamento.
'''

import pandas as pd
import psycopg2

from .config import config_spunet


class Parcelamento():
    '''
    Acessa os dados das operações de parcelamento no SPUNET.
    '''
    def __init__(self):
        con_args = {'host': '10.209.9.199',
                    'dbname': 'receitas',
                    'user': config_spunet['user'],
                    'password': config_spunet['password']}

        self.con = psycopg2.connect(**con_args)

    def get_table(self, schema_table):
        '''
        Retorna uma dataframe contendo uma tabela do banco de dados

        Parâmetros:
          schema_table(str): Caminho para a tabela. Ex: "siapa.tb_debitos"
        '''

        sql = "SELECT * FROM {};".format(schema_table)
        table = pd.read_sql_query(sql, con=self.con)
        return table

    @property
    def tb_parcelamento(self):
        ''' Retorna a tabela com as operações de parcelamento '''

        parc = self.get_table('siapa.tb_novo_parcelamento')
        parc = parc.merge(self.tb_situacao, how='left', left_on='id_situacao',
                          right_on='id_situacao_parcelamento')
        del parc['id_situacao_parcelamento']
        return parc

    @property
    def qtd_parcelamentos(self):
        ''' Quantidade total de parcelamentos '''
        return len(self.tb_parcelamento)

    @property
    def tb_debitos_parcelados(self):
        ''' Retorna a tabela de débitos parcelados '''
        debitos = self.get_table('siapa.tb_debito_parcelado')
        return debitos

    @property
    def qtd_debitos(self):
        ''' Quantidade total de débitos parcelados '''
        return len(self.tb_debitos_parcelados)

    @property
    def tb_situacao(self):
        ''' Tabela de domínio com as situações possível para operações
        de parcelamento '''
        return self.get_table('siapa.tb_situacao_parcelamento')

    @property
    def resumo_por_situacao(self):
        '''
            Resumo das operações de parcelamento consolidado por situação.
        '''
        resumo = self.tb_parcelamento.groupby('ds_situacao_parcelamento').count()['id_parcelamento']
        resumo = resumo.reset_index().rename(columns={'id_parcelamento': 'Quantidade'})
        return resumo

    @property
    def resumo_por_uf(self):
        ''' Operações de parcelamento consolidadas por UF '''

        cols = ['sg_uf', 'ds_situacao_parcelamento']
        resumo = self.tb_parcelamento.groupby(cols)['id_parcelamento'].count()
        resumo = resumo.reset_index().rename(columns={'id_parcelamento': 'Quantidade'})
        resumo = resumo.sort_values(by=['sg_uf', 'Quantidade'])
        return resumo

    def filtra_parcelamentos(self, situacao=None, sigla_uf=None):
        ''' Retorna as operações de parcelamento com a situação selecionada '''

        filtro_situacao = f'ds_situacao_parcelamento == "{situacao}"'
        filtro_uf = f'sg_uf == "{sigla_uf}"'
        params = filter(lambda x: "None" not in x, [filtro_situacao, filtro_uf])
        return self.tb_parcelamento.query(' & '.join(list(params)))

    def busca_debitos_parcelamento(self, id_parcelamento):
        ''' id_parcelamento (int) '''

        if isinstance(id_parcelamento, int) is False:
            raise ValueError('id_parcelamento deve ser int')

        query = f'id_parcelamento == {id_parcelamento}'
        debitos = self.tb_debitos_parcelados.query(query)
        return debitos
