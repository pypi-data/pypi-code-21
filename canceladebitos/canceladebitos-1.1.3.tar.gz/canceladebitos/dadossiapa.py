'''
    Funções responsáveis pela extração de dados da base Siapa.
'''

from siapatools import SIAPA

CANCELADO_PARC_MANUAL = '20'


def busca_debitos_cancelados():
    '''
    Retorna os débitos cancelados por parcelamento manual da base Siapa.
    '''
    siapa = SIAPA()
    siapa.minAnoDtBase = '1964'
    tabela = siapa.pega_debitos(filtro_situacao=[CANCELADO_PARC_MANUAL],
                                colunas=['nu_debito'])
    debitos = set(tabela['nu_debito'])
    qtd_debitos = len(debitos)
    msg = f'{qtd_debitos} débitos cancelados por parcelamento manual.'
    #print(msg)
    siapa.con.close()
    return debitos


def busca_uf_rip():
    siapa = SIAPA()
    imoveis = siapa.imoveis
    uf_rip = imoveis.merge(siapa.UF, how='left', left_on='ed_numero_uf',
                           right_on='nu_uf')
    colunas = ['nu_rip', 'sg_uf']
    uf_rip = uf_rip[colunas]
    uf_rip = uf_rip.rename(columns={'sg_uf': 'uf_rip'})
    erros = len(uf_rip[uf_rip['uf_rip'].isnull()])
    assert erros == 0
    return uf_rip
