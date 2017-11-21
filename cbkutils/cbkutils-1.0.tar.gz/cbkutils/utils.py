""" Some utilities
"""
from __future__ import print_function
import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
import jsonpickle
from cbkutils.backports.shutil_get_terminal_size import get_terminal_size
from . import constants as C

def ppc(obj):
    """ Pretty print an obj in color

    Args:
        obj (object): An object

    """
    serialized = jsonpickle.encode(obj, unpicklable=False)
    json_str = json.dumps(json.loads(serialized), indent=4, sort_keys=True)
    print(highlight(json_str, JsonLexer(), TerminalFormatter()))

def title(message):
    columns, _lines = get_terminal_size()
    print("%s %s" % (message, ("*" * (columns - len(message) - 3))))
