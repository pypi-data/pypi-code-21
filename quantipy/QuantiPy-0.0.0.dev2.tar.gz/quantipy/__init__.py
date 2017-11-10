# -*- coding: utf-8 -*-
"""

"""

import os

# Plot settings
import quantipy.mplrcsettings
from quantipy.mplrcsettings import choose_color_cycle

choose_color_cycle('fancy')
IS_SPHINX_BUILD = bool(os.getenv('SPHINX_BUILD'))
