"""Utils module for package.

Utility code for the package.
"""
from __future__ import print_function
from colorama import Fore, Style


def get_color(format_type):
    """Function: get_color.

    Summary: return text format color for correpondent type
    Examples: get_color("error")

    Attributes
    ----------
        @param (format_type):string

    Returns
    -------
    Object: Colorama Fore instance

    """
    return {
        'start': Fore.BLUE,
        'error': Fore.RED,
        'quote': Fore.GREEN
    }.get(format_type, Fore.WHITE)


def _console(text, format_type):
    if not format_type:
        print(text)
    else:
        print("{}{}{}".format(
            get_color(format_type),
            text,
            Style.RESET_ALL
        ))


def console(text, format_type=None):
    """Function: console.

    Summary: print command replacement using colors
    Examples: console("Hello World!", format_type="quote")

    Attributes
    ----------
        @param (text):String
        @param (format_type) default=None: String

    """
    if isinstance(text, list):
        for line in text:
            _console(line, format_type)
    else:
        _console(text, format_type)
