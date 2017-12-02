from __future__ import print_function
import inspect
import argparse
from funcsigs import Parameter, signature
import re
from functools import wraps
import sys

def sig2cli(fn):
    """Decorator that transforms the signature of a function to the input of an argument parser.
    It lets you define a function signature instead of writing a lot of verbose argparse code.
    Keyword arguments are the default.
    It supports short args (the first letter of each argument) only if they are all different.
    Default bool arguments are registered as flags.


    The decorated function should then be called with sys.argv[1:] as the argument.

    Example
        @sig2cli
        def a(first,second=0,third=0):
            '''Just a simple example

            Args:
                first : int. An int 
                second : int. Another int
                third : int. Yet another int
            '''
            return first + second + third
        
        assert a(['--first', '5']) == 5
        assert a(['--first', '5', '--second', '3']) == 8

    Arguments
        fn : function, The function to be changed

    Returns
        The function with the updated signature.
    """
    _types_dict = {
        'str':str,
        'int':int,
        'float':float,
        'bool':bool
    }
    sig = signature(fn)
    non_defaults = [x for x,v in sig.parameters.items() if v.default == Parameter.empty]
    defaults = {k:v.default for k,v in sig.parameters.items() if v.default != Parameter.empty}
    doc = fn.__doc__
    descr = re.findall(r'^([\s\S]*)\s+Arg', doc.strip()) if doc else ''
    parser = argparse.ArgumentParser(description=descr[0] if len(descr)>0 else '')
    par_type = {}
    par_help = {}
    if doc:
        par_typename = dict(re.findall(r'(\w+)\s*:(?!\n)\s*(\w+)', doc))
        par_type = {k:_types_dict[v] for k,v in par_typename.items() if v in _types_dict and k in non_defaults}
        par_help = dict(re.findall(r'(\w+)\s*\:(?!\n)\s*(.*)', doc))
    # check that all the starting letters are different
    easy_short_args = len(set(x[0] for x in sig.parameters.keys())) == len(sig.parameters.keys())
    for nd in non_defaults:
        names = ('-'+nd[0], '--'+nd) if easy_short_args else ('--'+nd,) 
        parser.add_argument(*names, required=True, type=par_type.get(nd, str), help=par_help.get(nd, ''))
    for d,v in defaults.items():
        names = ('-'+d[0], '--'+d) if easy_short_args else ('--'+d,) 
        if type(v) == bool:
            action = 'store_false' if v else 'store_true'
            parser.add_argument(*names, action=action, help=par_help.get(d, ''))
        else:
            parser.add_argument(*names, default=v, type=type(v), help=par_help.get(d, ''))
    @wraps(fn)
    def wrapped(argv):
        opt, _ = parser.parse_known_args(argv)
        mem = inspect.getmembers(opt)
        kwargs = {x[0]:x[1] for x in mem if not x[0].startswith('_')}
        return fn(**kwargs)
    return wrapped

def run(fn):
    """run a function taking the arguments from the command line.
    """
    a_fn = sig2cli(fn)
    a_fn(sys.argv[1:])

if __name__ == '__main__':
    #'''
    @sig2cli
    def a(first,second=0,third=0):
        """Just a simple example

        Args:
            first : int. An int 
            second : int. Another int
            third : int. Yet another int
        """
        return first + second + third

    assert a(['--first', '5']) == 5
    assert a(['--first', '5', '--second', '3']) == 8
    assert a(['--first', '5', '--second', '3', '--third', '-4']) == 4
    help_str = """usage: sig2cli.py [-h] --first FIRST [--second SECOND] [--third THIRD]

Just a simple example

optional arguments:
  -h, --help       show this help message and exit
  --first FIRST    int. An int
  --second SECOND  int. Another int
  --third THIRD    int. Yet another int
"""
    #assert help_str == a(['-h'])
    #'''

    #'''
    def b(one, two=2, log=False):
        """
        one: int. An int
        two: int. Another integer
        """
        if log:
            print('Logging')
        print(one + two)

    run(b)
    #'''
