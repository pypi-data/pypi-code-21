# -*- coding: utf-8 -*-

import matplotlib
from matplotlib import rcParams
from distutils.version import StrictVersion
if StrictVersion(matplotlib.__version__) >= StrictVersion('1.5.0'):
    from cycler import cycler

rcParams['font.family'] = 'serif'
rcParams['text.usetex'] = True
rcParams['text.latex.preamble'] = r'\usepackage{amsmath},\usepackage{amssymb}'

rcParams['axes.titlesize'] = 14
rcParams['axes.labelsize'] = 14
rcParams['xtick.labelsize'] = 12
rcParams['ytick.labelsize'] = 12

rcParams['figure.figsize'] = 7.5, 5

rcParams['legend.fontsize'] = 10
#rcParams['legend.handletextpad'] = 0
rcParams['legend.scatterpoints'] = 1
rcParams['legend.numpoints'] = 1

rcParams['lines.markersize'] = 8

rcParams['axes.grid'] = True
rcParams['axes.axisbelow'] = True

#color_cycle
def choose_color_cycle(name='standard'):
    """
    Choose the default color cycle for plots. Possibilities are: 'standard', 'fancy',('tableau').
    """
    if name == 'standard':
        if StrictVersion(matplotlib.__version__) < StrictVersion('1.5.0'):
            rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        else:
            rcParams['axes.prop_cycle'] = cycler('color', ['b', 'g', 'r', 'c', 'm', 'y', 'k'])

    elif name == 'fancy' or name == 'tableau':
        tableau10 = [(31, 119, 180), (255, 170, 14),
                     (44, 160, 44), (255, 0, 0),
                     (0, 0, 0),
                     (148, 103, 189), (140, 86, 75),
                     (227, 119, 194), (127, 127, 127),
                     (188, 189, 34), (23, 190, 207)]
        tableau10 = ["#%02x%02x%02x" %rgbcolor for rgbcolor in tableau10]

        if StrictVersion(matplotlib.__version__) < StrictVersion('1.5.0'):
            rcParams['axes.color_cycle'] = tableau10
        else:
            rcParams['axes.prop_cycle'] = cycler('color', tableau10)

    else:
        raise ValueError('Unknown color_cycle name!')
