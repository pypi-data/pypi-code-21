# -*- coding: utf-8 -*-

import platform

__version__ = '0.1.1'
__author__ = 'Seliverstov Maksim'
__email__ = 'Maksim.V.Seliverstov@yandex.ru'


if platform.system() == 'Windows':
    from .sc_windows import *
elif platform.system() == 'Linux':
    from .sc_linux import *
else:
    raise Exception('{} platform does not support'.format(platform.system()))
