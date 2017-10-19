import sys
from types import ModuleType

from .visualization import debug
from .constants import PROCGRAPH_INFO_VARIABLE, REQUIRES, REQUIRES_PARSED


def import_magic(module_name, required, member=None):
    ''' Equivalent to "from required import member" or "import required".
        Check that it was succesfull with import_succesful().
    '''
    info_structure = get_module_info(module_name)
    # Check that it was mentioned in the structure
    required_base = required.split('.')[0]
    if not required_base in info_structure[REQUIRES_PARSED]:
        raise Exception('Please specify that you need %r as a dependency '
                        'in the field %r of the %r structure in module %r.' %
                        (required_base, REQUIRES, PROCGRAPH_INFO_VARIABLE,
                         module_name))

    # FIXME: there's a bug in here, should find which base was selected
    if required == required_base:
        options = info_structure[REQUIRES_PARSED][required]
    else:
        options = [required]

    errors = ""
    for o in options:
        try:
            mod = __import__(o, fromlist=['dummy'])
            if member is not None:
                if not member in mod.__dict__:
                    raise Exception('No member %r in %r' % (member, o))
                return mod.__dict__[member]
            return mod
        except Exception as e: #@UnusedVariable
            # TODO: show error
            #debug(e)
            errors += '\n' + str(e)
            pass

    # We could not load anything.
    warn = ('Could not load dependency %r for %r.\n I will try to continue,'
           ' but an error might be thrown when %s actually tries to use %r.' %
           (required, module_name, module_name, required))

    if False: # TODO: think of configuration switch
        debug(warn)

    msg = ('I tried to let you continue, but it seems that module %r really'
           ' needs %r to work. Sorry! ' % (module_name, required))

    msg += '\nThe error message was:\n%s' % errors

    class warn_and_throw:
        def __getattr__(self, method_name): #@UnusedVariable
            raise Exception(msg)

    return warn_and_throw()


def get_module_info(module_name):
    # TODO: better Exception?
    if not module_name in sys.modules:
        raise Exception('Please pass  __package__ as argument (got: %r).'
                        % module_name)

    module = sys.modules[module_name]

    if not PROCGRAPH_INFO_VARIABLE in module.__dict__:
        raise Exception('Please define the structure %r for module %r. '
                        % (PROCGRAPH_INFO_VARIABLE, module_name))

    info = module.__dict__[PROCGRAPH_INFO_VARIABLE]

    ''' Returns dict   name -> list of possible modules '''
    parsed = {}
    if not REQUIRES in info:
        #raise Exception('Please define a field %r in dict %s.%s.' %
        #                (REQUIRES, module_name, PROCGRAPH_INFO_VARIABLE))
        pass
    else:
        requires = info[REQUIRES]
        for r in requires:
            if isinstance(r, str):
                # normal
                parsed[r] = [r]
            else:
                # TODO: check iterable
                name = r[0]
                options = list(r[1])
                # TODO: check options > 0
                parsed[name] = options

    info[REQUIRES_PARSED] = parsed

    return info

def import_successful(m):
    return isinstance(m, ModuleType)

import_succesful = import_successful  # oops, typo
