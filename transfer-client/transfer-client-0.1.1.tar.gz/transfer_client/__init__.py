"""Transfer server client CLI.


Copyright (c) 2017 Leiden University Medical Center <humgen@lumc.nl>
Copyright (c) 2017 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
Copyright (c) 2017 Mark Santcroos <m.a.santcroos@lumc.nl>

Licensed under the MIT license, see the LICENSE file.
"""
from .transfer_client import TransferClient


__version_info__ = ('0', '1', '1')

__version__ = '.'.join(__version_info__)
__author__ = 'LUMC, Jeroen F.J. Laros'
__contact__ = 'J.F.J.Laros@lumc.nl'
__homepage__ = 'https://git.lumc.nl/j.f.j.laros/transfer_client'

usage = __doc__.split('\n\n\n')


def doc_split(func):
    return func.__doc__.split('\n\n')[0]


def version(name):
    return '{} version {}\n\nAuthor   : {} <{}>\nHomepage : {}'.format(
        name, __version__, __author__, __contact__, __homepage__)
