import shlex
from itertools import accumulate
from functools import partial
from collections import OrderedDict
from ..exceptions import CouldNotParse, Exit
from ..annotations import Flag

def positionals(function, raw_values):
    values = list(raw_values)
    positional = []
    keyword1 = []
    var_positional = []

    while 0 < len(values):
        if len(positional) < len(function.positional):
            name = function.positional[len(positional)].name
            value = values.pop(0)
            positional.append((name, value))
        elif len(keyword1) < len(function.keyword1):
            name = function.keyword1[len(keyword1)].name
            value = values.pop(0)
            keyword1.append((name, value))
        elif len(var_positional) == 0 and len(function.var_positional) == 1:
            name = function.var_positional[0].name
            for value in values:
                var_positional.append((name, value))
            values.clear()
        else:
            raise CouldNotParse('Extra positional arguments: %s' % _sh(values))

    arguments = OrderedDict()
    for name, value in positional + keyword1 + var_positional:
        if not name in arguments:
            arguments[name] = []
        arguments[name].append(value)

    return arguments

def split_section(allow, program, xs):
    for section in sorted(program, key=len, reverse=True):
        if tuple(xs[:len(section)]) == section:
            valid = True
            break
    else:
        valid = False
    
    if valid and section in program:
        return section, xs[len(section):]
    else:
        for section in accumulate((a,) for a in xs if allow(a)):
            if section not in program:
                break
        else:
            section = tuple()
        if xs:
            msg = 'Bad subcommand'
        else:
            msg = 'Needs subcommand'
        raise CouldNotParse(section=section, message=msg)


def _sh(values):
    return ' '.join(map(shlex.quote, values))

def _yes_hyphen(x):
    return x.startswith('-')
def _no_hyphen(x):
    return not x.startswith('-')

cli_section = partial(split_section, _no_hyphen)
web_section = partial(split_section, lambda x: True)
