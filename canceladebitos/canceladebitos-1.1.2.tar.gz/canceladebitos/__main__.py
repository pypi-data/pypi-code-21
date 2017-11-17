'''
    CLI para o script de cancelamento de débitos.
'''
import os
import sys

import fire

from .cancelador import Cancelador
from .config import config_siapa, config_spunet
#from .valida import main as Validador
from .valida import main as Validador
from .__init__ import __version__

def valida_config(config):
    for k, value in config.items():
        if value == '':
            msg = f'{k} inválido. Verifique a configuração no arquivo config.py do pacote.'
            print(msg)
            return False
    return True

def cli(validador=False):
    os.system('cls')
    print(f'CANCELA DÉBITOS PARCELAMENTO v{__version__}')
    print(f'===================================\n')

    if not all([valida_config(config_siapa), valida_config(config_spunet)]):
        sys.exit(1)

    if validador:
        Validador(config_siapa['cpf'], config_siapa['senha'])
    else:
        Cancelador(config_siapa['cpf'], config_siapa['senha'])


def main():
    fire.Fire(cli)
