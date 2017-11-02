'''
passivetotal2

passivetotal2 client
'''
from .client import Client
from .cli import main

__title__ = 'passivetotal2'
__version__ = '0.0.1'
__all__ = ('Client',)
__author__ = 'Johan Nestaas <johan.nestaas@riskiq.net>, Gabe Pack <gabe@riskiq.net>'
__license__ = 'Copyright RiskIQ'
__copyright__ = 'Copyright 2017 RiskIQ'


if __name__ == '__main__':
    main()
