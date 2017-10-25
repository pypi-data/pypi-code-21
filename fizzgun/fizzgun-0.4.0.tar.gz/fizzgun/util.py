import collections
import os.path
import urllib.parse


def fizzgun_path(*args):
    """Builds an absolute path from sub-paths relative to Fizzgun's root dir"""
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        *args
    )


def tpl(name):
    """Shortcut for retrieving full path of mustache templates"""
    return fizzgun_path('data', 'templates', 'mustache', "%s.mustache" % name)


def parse_qs(qs, keep_blank_values=False, strict_parsing=False,
             encoding='utf-8', errors='replace'):
    """
    Same than `urllib.parse.parse_qs` but uses an ordered dict
    """
    parsed_result = collections.OrderedDict()
    pairs = urllib.parse.parse_qsl(qs, keep_blank_values, strict_parsing,
                                   encoding=encoding, errors=errors)
    for name, value in pairs:
        if name in parsed_result:
            parsed_result[name].append(value)
        else:
            parsed_result[name] = [value]
    return parsed_result
