""" Graphviz
"""
import logging
from Globals import INSTANCE_HOME
from pydot import __find_executables as _find_executables

logger = logging.getLogger('eea.relations.graph')


def find_graphviz():
    """ This assumes that Graphviz is installed in
    {buildout:directory}/parts/graphviz

    """
    paths = INSTANCE_HOME.split('/parts/')
    if len(paths) < 2:
        logger.warn('Graphviz NOT INSTALLED via zc.buildout')
        return None

    paths[-1] = 'graphviz/bin'
    binpath = '/parts/'.join(paths)
    prog = _find_executables(binpath)
    if prog:
        logger.info('Graphviz INSTALLED via zc.buildout')
    else:
        logger.warn('Graphviz NOT INSTALLED via zc.buildout')
    return prog

GRAPHVIZ_PATHS = find_graphviz()
