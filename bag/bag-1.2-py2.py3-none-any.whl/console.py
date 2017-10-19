# -*- coding: utf-8 -*-

"""Functions for user interaction at the terminal/console."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from nine import str, input


def ask(prompt='', default=None):
    """Print the ``prompt``, get user's answer, return it -- or a default."""
    if prompt:
        if default:
            prompt = prompt + ' [' + default + ']'
        prompt = prompt + ' '
    answer = None
    while not answer:
        answer = input(prompt)
        if default and not answer:
            return default
    return answer


def bool_input(prompt, default=None):
    """Print ``prompt``; return True or False based on the user's choice."""
    if default is None:
        choices = ' (y/n) '
    elif default:
        choices = ' (Y/n) '
    else:
        choices = ' (y/N) '
    opt = input(prompt + choices).lower()
    if opt == 'y':
        return True
    elif opt == "n":
        return False
    elif not opt and default is not None:
        return default
    else:  # Invalid answer, let's ask again
        return bool_input(prompt)


def pick_one_of(options, prompt='Pick one: ', to_str=None):
    """Let the user choose an item (from a sequence of options) by number.

    ``to_str()`` is a callback that must take an item as argument and must
    return a corresponding string to be displayed.
    """
    alist = options if isinstance(options, list) else list(options)
    c = 0
    for o in alist:
        c += 1
        print(str(c).rjust(2) + ". " + to_str(o) if to_str else str(o))
    while True:
        try:
            opt = int(input(prompt))
        except ValueError:
            continue
        return alist[opt - 1]


def screen_header(text, decor='=', max=79):
    """Return a header to be displayed on screen, by decorating ``text``."""
    text = str(text)
    available = max - len(text)
    if available > 3:
        text = '  ' + text + '  '
        available -= 4
    else:
        return text
    req_space = len(decor) * 2
    while available >= req_space:
        text = decor + text + decor
        available -= req_space
        if len(text) == available - len(decor):  # Add just one more =
            text += decor          # in order to fill the whole screen
            available -= len(decor)
    return text
