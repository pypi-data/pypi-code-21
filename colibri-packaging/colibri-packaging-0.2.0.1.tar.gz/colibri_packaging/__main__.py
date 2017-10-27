# coding: utf-8
from __future__ import absolute_import
import argparse
import os
from .empacotar import (
    INNOSERV, PACOTE, VERSAO, MENSAGEM, DEVELOP, SUBPACOTES, empacotar
)


parser = argparse.ArgumentParser(
    description=(
        u"Gera um pacote do Colibri Master. " +
        u"Este programa usa partes do 7-Zip," +
        u" que é licenciado sob GNU LGPL." +
        u" O código pode ser obtido em http://www.7-zip.org"
    )
)
parser.add_argument('caminho', type=str,
                    help='Caminho dos arquivos do pacote')
parser.add_argument('--pasta_saida', dest='pasta_saida',
                    help=u'Pasta de saída')
parser.add_argument('--senha', dest='senha', default='', help='Senha')
parser.add_argument('--' + INNOSERV, dest=INNOSERV,
                    help=u'parametro IGNORADO')
parser.add_argument('--' + PACOTE, dest=PACOTE, help=u'Id do pacote')
parser.add_argument('--' + VERSAO, dest=VERSAO, help=u'Versão do produto')
parser.add_argument('--nome_exibicao', dest='nome_exibicao',
                    help=u'Nome de exibição do produto')
parser.add_argument(
    '--' + SUBPACOTES, dest=SUBPACOTES, nargs='+',
    help=u'Pacotes a adicionar a esse pacote'
)
parser.add_argument(
    '--' + MENSAGEM, dest=MENSAGEM,
    help=u'Mensagem descritiva do pacotes'
)
parser.register(
    'type', 'bool', lambda v: v.lower() in ("true", "t", "1")
)
parser.add_argument(
    '--' + DEVELOP, dest=DEVELOP, help=u'Pacote de desenvolvimento',
    type='bool', default=True
)
parser.add_argument(
    '--versao_base', nargs=2, dest='versoes_bases', action='append',
    help='Nome do schema e versao do banco', metavar=('schema', 'versao')
)

args = vars(parser.parse_args())

caminho = args.pop('caminho')
caminho_destino = args.pop('pasta_saida') or os.getcwd()
saida = empacotar(caminho, caminho_destino, args.pop('senha'),
                  **{k: args[k] for k in args if args[k] is not None})
