import sys
import logging
from collections import ChainMap
from functools import partial
from . import _util
from ..program import Program
from ..annotations import OutputFile
from ..exceptions import AnnotationNotImplemented

logger = logging.getLogger(__name__)

def default(program, with_sections=False):
    '''
    Write a configuration file with a program's defaults.

    :type program: Program, callable, list, or dict
    :param program: The program for which to produce the interface,
    :param bool with_sections: Give each subcommand its own namespace rather
        than putting all of the arguments in a global namespace.
    '''
    if not isinstance(program, Program):
        program = Program(program)
    c = program.configuration()

    for section in program:
        function = program[section]
        params = {param.name: param for param in function.all_parameters()}
        for key, x in function.defaults.items():
            if not key in c:
                param = params[key]
                f = partial(param.dumps, 'raw')
                try:
                    if param.is_list_type:
                        c[section].extend(key, map(f, x))
                    else:
                        c[section].append(key, f(x))
                except AnnotationNotImplemented:
                    logger.warning('No dumps method for %s annotation, skipping' % key)

    return c.write(with_sections=with_sections)

def run(program, section=tuple()):
    '''
    Run a program, applying arguments from any included configuration files.

    :type program: Program, callable, list, or dict
    :param program: The program for which to produce the interface,
    :type section: Iterable of tuple of str
    :param section: Subcommand to run.
    '''
    if not isinstance(program, Program):
        program = Program(program)
    return program[section].run('raw', [])
