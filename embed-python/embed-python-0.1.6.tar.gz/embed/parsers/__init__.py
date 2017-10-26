from importlib import import_module


def get_parser(provider):
    try:
        return import_module('embed.parsers.' + provider)
    except ImportError:
        return import_module('embed.parsers.generic')
