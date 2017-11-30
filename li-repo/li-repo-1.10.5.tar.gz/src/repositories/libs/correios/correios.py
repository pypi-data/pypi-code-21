# -*- coding: utf-8 -*-

from xml.dom.minidom import parseString

import logging
import math
import socket
import urllib
import urllib2
from decimal import Decimal
from pprint import pprint

from django.conf import settings

logger = logging.getLogger(__name__)


CORREIOS_TIMEOUT = 5


class CorreiosContrato(object):
    pac_sem_contrato = 41106
    sedex_sem_contrato = 40010
    sedex_a_cobrar_sem_contrato = 40045
    sedex_10_sem_contrato = 40215
    sedex_hoje_sem_contrato = 40290
    sedex_com_contrato_1 = 40096
    sedex_com_contrato_2 = 40436
    sedex_com_contrato_3 = 40444
    e_sedex_com_contrato = 81019
    pac_com_contrato = 41068


CORREIOS_CONTRATO = {
    CorreiosContrato.pac_sem_contrato: 'PAC, sem contrato',
    CorreiosContrato.sedex_sem_contrato: 'SEDEX, sem contrato',
    CorreiosContrato.sedex_a_cobrar_sem_contrato: 'SEDEX a Cobrar, sem contrato',
    CorreiosContrato.sedex_10_sem_contrato: 'SEDEX 10, sem contrato',
    CorreiosContrato.sedex_hoje_sem_contrato: 'SEDEX Hoje, sem contrato',
    CorreiosContrato.sedex_com_contrato_1: 'SEDEX, com contrato',
    CorreiosContrato.sedex_com_contrato_2: 'SEDEX, com contrato',
    CorreiosContrato.sedex_com_contrato_3: 'SEDEX, com contrato',
    CorreiosContrato.e_sedex_com_contrato: 'e-SEDEX, com contrato',
    CorreiosContrato.pac_com_contrato: 'PAC, com contrato'
}

CORREIOS_CODIGO_CONTRATO_SERVICO = {
    'pac': [CorreiosContrato.pac_sem_contrato, CorreiosContrato.pac_com_contrato],
    'sedex': [
        CorreiosContrato.sedex_sem_contrato,
        CorreiosContrato.sedex_com_contrato_1,
        CorreiosContrato.sedex_com_contrato_2,
        CorreiosContrato.sedex_com_contrato_3,
        CorreiosContrato.sedex_a_cobrar_sem_contrato
    ],
    'e_sedex': [CorreiosContrato.e_sedex_com_contrato],
    'sedex_10': [CorreiosContrato.sedex_10_sem_contrato],
    'sedex_hoje': [CorreiosContrato.sedex_hoje_sem_contrato]
}

CORREIOS_FORMATO = {
    1: 'Caixa ou pacote',
    2: 'Rolo ou prisma'
}

CORREIOS_LIMITES = {
    'tamanho_min': {'comprimento': 16, 'largura': 11, 'altura': 2},
    'tamanho_max': {'comprimento': 105, 'largura': 105, 'altura': 105, 'somado': 200},
    'peso_max': 30
}

CORREIOS_URL = 'http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx'


class CorreiosItemInexistente(Exception):
    pass

class CorreiosCodigoServicoInvalido(Exception):
    pass

class CorreiosFormasEnvioInexistente(Exception):
    pass

class CorreiosTamanhoPesoNaoCalculado(Exception):
    pass

class CorreiosWebserviceTimeout(Exception):
    pass


class Correios(object):
    """Define a comunicação com o webservice dos Correios para calculo de frete."""
    def __init__(self, cep_destino):
        self.cep_destino = cep_destino
        self.calculado_tamanho_peso = False
        self.formas_envio = []
        self.itens = []
        self.medidas = [0, 0, 0, 0]

    def adicionar_forma_envio(self, codigo_servico, cep_origem,
                              codigo_contrato='', senha_contrato='', entrega_mao_propria=False,
                              valor_declarado=0, aviso_recebimento=False, item_id=None, nome=None):
        if codigo_servico == 'false':
            raise CorreiosCodigoServicoInvalido(u'Código de serviço inválido ou inexistente')
        forma_envio = {'codigo_servico': codigo_servico, 'cep_origem': cep_origem,
                       'codigo_contrato': codigo_contrato, 'senha_contrato': senha_contrato,
                       'entrega_mao_propria': entrega_mao_propria, 'valor_declarado': valor_declarado,
                       'aviso_recebimento': aviso_recebimento, 'item_id': item_id, 'nome': nome}
        self.formas_envio.append(forma_envio)

    def adicionar_item(self, comprimento, largura, altura, peso, valor=None):
        """Adiciona um item para ser enviado. Todos os valores são float."""
        self.itens.append([comprimento, largura, altura, peso, valor])

    def _converter_para_decimal(self, valor):
        """Converte uma string para Decimal."""
        if valor is None:
            return None
        valor = valor.replace('.', '').replace(',', '.')

        return Decimal(valor)

    def _calcular_tamanho_peso(self):
        """Calcula o tamanho e peso dos items.

        O cálculo é feito primeiro ordenando as medidas de comprimento, altura e
        largura de forma decrescente. Após isso pegamos o maior comprimento, a
        maior altura e o somatório das larguras.
        """
        # As medidas são zeradas logo de início para que o peso não seja
        # somado entre as diferentes formas de pagamento.
        self.medidas = [0, 0, 0, 0]

        # Alterei o cálculo das dimensões para corrigir um erro com um
        # determinado cliente, ele tinha um produto com tamanho 3 x 4 x 6
        # e o sistema dizia que não poderia enviar mais que 36 produtos ao
        # mesmo tempo. Com o novo cálculo ele pode enviar mais de 700 produtos
        # de uma vez, mas ainda não é o correto. Na realidade ele poderia
        # enviar 3997 produtos dentro de uma caixa de 66 x 66 x 66 cm (padrão
        # dos Correios).
        # Ass.: Jonatas

        # Este cálculo foi tirado do plugin woocomerce-correios.
        medidas = []
        for item in self.itens:
            medidas.append([item[0], item[1], item[2]])
            self.medidas[3] += item[3]

        # Calcula a cubagem total do pacote.
        cubagem_total = 0
        for medida in medidas:
            cubagem_total += (medida[0] or 1) * (medida[1] or 1) * (medida[2] or 1)

        alturas, larguras, comprimentos = zip(*medidas)
        maiores_medidas = [max(alturas), max(larguras), max(comprimentos)]

        raiz = 0
        if cubagem_total > 0:
            try:
                divisao = float(cubagem_total) / max(maiores_medidas)
                raiz = round(math.sqrt(divisao), 1)
            except ZeroDivisionError:
                raiz = 0

        maior = max(maiores_medidas)
        self.medidas[0] = max(maior, CORREIOS_LIMITES['tamanho_min']['comprimento'])
        self.medidas[1] = max(raiz, CORREIOS_LIMITES['tamanho_min']['largura'])
        self.medidas[2] = max(raiz, CORREIOS_LIMITES['tamanho_min']['altura'])

        self.calculado_tamanho_peso = True
        self.xml = None

    def _pegar_xml(self):
        """Envia os dados coletados para o webservice do Correios."""
        if not self.calculado_tamanho_peso:
            raise CorreiosTamanhoPesoNaoCalculado(u'Antes é preciso calcular o tamanho e peso.')

        def to_decimal_br(valor):
            return ('%.2f' % valor).replace('.', ',')

        url = CORREIOS_URL
        params = [['nCdEmpresa', str(self.codigo_contrato)],
                  ['sDsSenha', str(self.senha_contrato)],
                  ['nCdServico', ','.join([str(x) for x in self.codigo_servico])],
                  ['sCepOrigem', str(self.cep_origem)],
                  ['sCepDestino', str(self.cep_destino)],
                  ['nVlPeso', to_decimal_br(self.medidas[3])],  # Kg
                  ['nCdFormato', 1],
                  ['nVlComprimento', to_decimal_br(self.medidas[0])],  # Cm
                  ['nVlLargura', to_decimal_br(self.medidas[1])],  # Cm
                  ['nVlAltura', to_decimal_br(self.medidas[2])],  # Cm
                  ['nVlDiametro', 0],  # Cm
                  ['sCdMaoPropria', self.entrega_mao_propria and 'S' or 'N'],
                  ['nVlValorDeclarado', to_decimal_br(self.valor_declarado)],  # R$
                  ['sCdAvisoRecebimento', self.aviso_recebimento and 'S' or 'N'],
                  ['StrRetorno', 'xml']]

        params = urllib.urlencode(dict(params))
        url_with_params = "%s?%s" % (url, params)

        logger.debug(u"URL CORREIOS: \n{}\n".format(url_with_params))

        try:
            f = urllib2.urlopen(url_with_params, timeout=CORREIOS_TIMEOUT)
        except (urllib2.URLError, socket.timeout):
            # Quando der erro tenta pegar depois do cache.
            logger.debug("CORREIOS TIMEOUT: \nVai Pegar do ES\n")
            raise CorreiosWebserviceTimeout(u'O webservice dos Correios não está disponível no momento.')

        xml_string = f.read()
        #logger.debug(u"DADOS RETORNADOS DOS CORREIOS: \n{}\n".format(xml_string))
        self.xml = parseString(xml_string)

    def _parse_xml(self):
        retorno = []

        servicos = self.xml.getElementsByTagName('cServico')
        contador = 0
        for servico in servicos:
            traducao = {
                'codigo_servico': 'Codigo',
                'valor': 'Valor',
                'prazo_entrega': 'PrazoEntrega',
                'valor_mao_propria': 'ValorMaoPropria',
                'valor_aviso_recebimento': 'ValorAvisoRecebimento',
                'valor_valor_declarado': 'ValorValorDeclarado',
                'entrega_domiciliar': 'EntregaDomiciliar',
                'entrega_sabado': 'EntregaSabado',
                'erro': 'Erro',
                'msg_erro': 'MsgErro'
            }
            retorno_servico = {}
            for chave, valor in traducao.items():
                if servico.getElementsByTagName(valor):
                    value = servico.getElementsByTagName(valor)[0].firstChild
                    if value:
                        retorno_servico[chave] = value.data
                    else:
                        retorno_servico[chave] = None

            # Tratando o valor do frete.
            retorno_servico['valor'] = self._converter_para_decimal(
                retorno_servico['valor'])
            retorno_servico['valor_mao_propria'] = self._converter_para_decimal(
                retorno_servico['valor_mao_propria'])
            retorno_servico['valor_aviso_recebimento'] = self._converter_para_decimal(
                retorno_servico['valor_aviso_recebimento'])
            retorno_servico['valor_valor_declarado'] = self._converter_para_decimal(
                retorno_servico['valor_valor_declarado'])

            # Adicionando informações do contrato...
            retorno_servico['codigo_contrato'] = self.codigo_contrato
            retorno_servico['cep_origem'] = self.cep_origem
            retorno_servico['nome_servico'] = CORREIOS_CONTRATO.get(
                int(retorno_servico.get('codigo_servico') or 0))
            retorno_servico['item_id'] = self.item_id[contador]
            retorno_servico['nome'] = self.nomes[contador]
            for nome_codigo_servico, codigos in CORREIOS_CODIGO_CONTRATO_SERVICO.items():
                if int(retorno_servico.get('codigo_servico') or 0) in codigos:
                    retorno_servico['nome_codigo_servico'] = nome_codigo_servico
            retorno.append(retorno_servico)
            contador += 1

        return retorno


    def calcular_frete(self):
        if not self.itens:
            raise CorreiosItemInexistente(u'É necessário adicionar pelo menos um item.')

        if not self.formas_envio:
            raise CorreiosFormasEnvioInexistente(u'É necessário adicionar pelo menos uma forma de envio.')

        # Verificando se os dados internos das formas de envio são todos iguais.
        formas_envio_agrupadas = {}

        # Procurando por envios com o mesmo cep e nenhum contrato.
        for forma_envio in self.formas_envio:
            cep_origem = forma_envio.get('cep_origem')
            codigo_contrato = forma_envio.get('codigo_contrato')
            entrega_mao_propria = forma_envio.get('entrega_mao_propria')
            valor_declarado = forma_envio.get('valor_declarado')
            aviso_recebimento = forma_envio.get('aviso_recebimento')

            chave = '%s-%s-%s-%s-%s' % (codigo_contrato, cep_origem, entrega_mao_propria and 'S' or 'N', valor_declarado or 'N', aviso_recebimento and 'S' or 'N')
            if chave not in formas_envio_agrupadas:
                formas_envio_agrupadas[chave] = []
            formas_envio_agrupadas[chave].append(forma_envio)

        retorno = []

        logger.debug(u"FORMAS DE ENVIO AGRUPADAS: \n{}\n".format(formas_envio_agrupadas))

        for codigo, forma_envio_agrupada in formas_envio_agrupadas.items():
            forma_envio = forma_envio_agrupada[0]
            codigos_servico = [x.get('codigo_servico') for x in forma_envio_agrupada]
            itens_id = [x.get('item_id') for x in forma_envio_agrupada]
            nomes = [x.get('nome') for x in forma_envio_agrupada]

            # Colocando os dados necessários na instância.
            self.codigo_servico = codigos_servico
            self.cep_origem = forma_envio.get('cep_origem')
            self.codigo_contrato = forma_envio.get('codigo_contrato')
            self.senha_contrato = forma_envio.get('senha_contrato')
            self.entrega_mao_propria = forma_envio.get('entrega_mao_propria')
            self.valor_declarado = forma_envio.get('valor_declarado')
            self.aviso_recebimento = forma_envio.get('aviso_recebimento')
            self.item_id = itens_id
            self.nomes = nomes

            # Calculando o tamanho e peso.
            self._calcular_tamanho_peso()

            self._pegar_xml()
            retorno += self._parse_xml()

        return retorno


def test():
    c = Correios('24928020')

    c.adicionar_forma_envio(CorreiosContrato.pac_sem_contrato, '59152100', item_id='1231', nome=u'PAC')
    c.adicionar_forma_envio(CorreiosContrato.sedex_sem_contrato, '59152100', item_id='35', nome=u'SEDEX')
    c.adicionar_forma_envio(CorreiosContrato.sedex_10_sem_contrato, '59152100', item_id='124', nome=u'SEDEX 10')

    c.adicionar_forma_envio(CorreiosContrato.sedex_com_contrato_2, '88307750', '10346147', '047776032', item_id='532')
    c.adicionar_forma_envio(CorreiosContrato.e_sedex_com_contrato, '88307750', '10346147', '047776032', item_id='88')

    c.adicionar_forma_envio(CorreiosContrato.pac_com_contrato, '20040003', '10108920', '009110343', item_id='999')
    c.adicionar_forma_envio(CorreiosContrato.sedex_com_contrato_1, '01209000', '10284907', '07868103', item_id='534')

    c.adicionar_item(5, 5, 5, 0.10)
    c.adicionar_item(10, 3, 2, 0.25)
    c.adicionar_item(7, 5, 10, 2)

    pprint(c.calcular_frete())


if __name__ == '__main__':
    test()
