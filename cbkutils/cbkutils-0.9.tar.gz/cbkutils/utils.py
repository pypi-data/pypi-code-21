""" Some utilities
"""
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

def status(message, style):
    """ Prints to screen and log file

    Args:
        message (str): The message to print
        style (str): A style with which to print

    """
    header = '\033[%s;%sm' % (C.BOLD, C.FG_WHITE)
    okgreen = '\033[%sm' % C.FG_GREEN
    warning = '\033[%s;%sm' % (C.BOLD, C.FG_YELLOW)
    fail = '\033[%s;%sm' % (C.BOLD, C.FG_RED)
    columns, _lines = get_terminal_size()
    endc = '\033[0m'
    if style == 'header':
        print("%s[%s] %s%s" % (header, message, ("*" * (columns - len(message) - 3)), C.RESET_SEQ))
    elif style == 'ok':
        print(u"%s%-*s%s%s" % (okgreen, columns - 5, message, u'[\u2714]', endc))
    elif style == 'warning':
        print(u"%s%-*s%s%s" % (warning, columns - 5, message, u'[!]', endc))
    elif style == 'fail':
        print(u"%s%-*s%s%s" % (fail, columns - 5, message, u'[\u2715]', endc))
