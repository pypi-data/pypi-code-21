# -*- coding: utf-8 -*-

import logging
import re

from datetime import datetime, date, time
from django.conf import settings
from li_common.helpers import send_email
from repositories.libs.aws import AWS
from unicodedata import normalize

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
TEMPORARY_FOLDER = '/tmp/'


LOGRADOUROS = {
    u'AEROPORTO': 'AER', u'ALAMEDA': 'AL', u'APARTAMENTO': 'AP',
    u'AVENIDA': 'AV', u'BECO': 'BC', u'BLOCO': 'BL', u'CAMINHO': 'CAM',
    u'ESCADINHA': 'ESCD', u'ESTAÇÃO': 'EST', u'ESTRADA': 'ETR',
    u'FAZENDA': 'FAZ', u'FORTALEZA': 'FORT', u'GALERIA': 'GL',
    u'LADEIRA': 'LD', u'LARGO': 'LGO', u'PRAÇA': 'PCA',
    u'PARQUE': 'PRQ', u'PRAIA': 'PR', u'QUADRA': 'QD',
    u'QUILÔMETRO': 'KM', u'QUINTA': 'QTA', u'RODOVIA': 'ROD',
    u'RUA': 'RUA', u'SUPER QUA': 'SQD', u'TRAVESSA': 'TRV',
    u'VIADUTO': 'VD', u'VILA': 'VL',
}


def formatar_decimal_br(valor, casas_decimais=2, separador_milhar=True):
    """
    Formata valor com duas casas decimais e virgula.

    >>> formatar_decimal_br(3)
    '3,00'
    >>> formatar_decimal_br(29.9)
    '29,90'
    >>> formatar_decimal_br('abc')
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    ValueError: Numero decimal invalido.

    """
    if casas_decimais is None or casas_decimais < 0:
        casas_decimais = 0

    if not valor:
        return '0%s%s' % (casas_decimais and ',' or '', '0' * casas_decimais)

    valor = re.sub(r'[^0-9\.\,\-]+', '', str(valor))
    valor = float(valor)

    valor = (('%%.%sf' % casas_decimais) % valor).replace('.', ',')
    if ',' in valor:
        inteiro, decimal = valor.split(',')
    else:
        inteiro, decimal = valor, None

    if len(inteiro) > 3:
        if not separador_milhar:
            valor_convertido = inteiro
        else:
            # inverte o valor para contar as casas de 3 em 3
            rev = inteiro[::-1]
            vezes = len(rev) / 3

            if len(rev) % 3 == 0:
                vezes -= 1

            valor_convertido = ''
            cont = 0

            # a cada três casas adiciona um '.'
            for i in range(vezes):
                valor_convertido += rev[cont: 3 + cont] + '.'
                cont += 3

            # adiciona o resto do valor
            valor_convertido += rev[cont: 3 + cont]

            # retorna o valor revertido e correto
            # agora pode se receber zilhões como valor
            valor_convertido = valor_convertido[::-1]
    else:
        return valor

    if decimal:
        return valor_convertido + ',' + decimal
    else:
        return valor_convertido


def delete_from_s3(nome_imagem):
    if not nome_imagem:
        return False
    aws = AWS()
    balde = aws.get_balde(settings.AWS_S3_BUCKET_IMAGES)
    return balde.delete(nome_imagem)


def delete_uploaded_file(nome_imagem):
    delete_from_s3(nome_imagem)
    return True


def enviar_email(
        request,
        template_file=None,
        context=None,
        cliente_id=None,
        usuario_id=None,
        pedido_venda_id=None,
        countdown=0,
        to_email=None,
        reply_to=None,
        salva_evidencia=True):

    # Se o desenvolvimento for loca, nao envia email
    # if settings.ENVIRONMENT == 'local':
    #     return True

    if hasattr(request, 'conta'):
        conta_id = request.conta.id
    else:
        conta_id = None

    # Verifica se a loja eh PRO
    if (hasattr(request, 'plano_vigente') and
        hasattr(request.plano_vigente, 'content')
            and request.plano_vigente.content.plano.indice > 1) or request.GET.get('pro') or request.POST.get('pro'):

        if context is not None:
            context['pro'] = True
        else:
            context = {'pro': True}

    send_email(
        template_file=template_file,
        context=context,
        cliente_id=cliente_id,
        pedido_venda_id=pedido_venda_id,
        conta_id=conta_id,
        contrato_id=request.contrato.id,
        usuario_id=usuario_id,
        countdown=countdown,
        salva_evidencia=salva_evidencia,
        to_email=to_email,
        reply_to=reply_to
    )

    return True


def validar_tipo_desconto(tipo, valor):
    """ Faz a validação e retorna um boleano"""
    if tipo != 'frete_gratis' and not valor:
        return False
    if tipo == 'porcentagem' and float(valor) > 100:
        return False
    return True


def validar_validade_cupom(data):
    """ Valida a data do cupom de desconto """
    if data:
        if isinstance(data, date):
            data = datetime.combine(data, time.min)
        if data < datetime.now():
            return False
    return True


def formatar_cep(cep):
    """
    Formata CEP.

    >>> formatar_cep('01301000')
    '01301-000'
    >>> formatar_cep('59152100')
    '59152-100'
    >>> formatar_cep(1301000)
    '01301-000'
    >>> formatar_cep('01234')
    '00001-234'
    >>> formatar_cep(None)
    None
    """

    if isinstance(cep, int):
        cep = str(cep)

    if not cep:
        return cep

    if len(cep) < 8:
        cep = cep.rjust(8, '0')

    if len(cep) == 8 and cep.isdigit():
        return '%s-%s' % (cep[:5], cep[5:])
    else:
        return cep


def aninhar_categorias(categorias):
    copia = list(categorias)
    for categoria in copia:
        categoria.categorias_filhas = []

        for categoria_filha in copia:

            if categoria_filha.parent_id and \
                    categoria_filha.parent_id == categoria.id:
                categoria.categorias_filhas += [categoria_filha]

    return [x for x in copia if not x.parent_id]


def flat_categorias(categorias):
    flat = []
    for categoria in categorias:
        flat += [categoria]
        if hasattr(categoria, 'categorias_filhas'):
            flat += flat_categorias(categoria.categorias_filhas)
    return flat


def to_ascii(texto):
    """Remove qualquer acentuação e qualquer caractere estranho."""
    try:
        return normalize('NFKD',
                         texto.decode('utf-8')).encode('ASCII',
                                                       'ignore')
    except UnicodeEncodeError:
        return normalize('NFKD', texto).encode('ASCII', 'ignore')
