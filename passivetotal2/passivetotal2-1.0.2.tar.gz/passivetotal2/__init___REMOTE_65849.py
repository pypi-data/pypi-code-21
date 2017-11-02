'''
passivetotal2

PassiveTotal client, version 2
'''
from .client import Client
from .cli import main

__title__ = 'passivetotal2'
__version__ = '1.0.0'
__all__ = ('Client',)
__author__ = 'Johan Nestaas <johan.nestaas@riskiq.net>, Nate Falke <nate.falke@riskiq.net>'
__license__ = 'Copyright RiskIQ'
__copyright__ = 'Copyright 2017 RiskIQ'


if __name__ == '__main__':
    main()
