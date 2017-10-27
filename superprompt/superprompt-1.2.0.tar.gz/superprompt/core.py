"""
This modules defines functions to enhance the basic input() for the standard lib with autocompletion.
"""

import glob
import os
import colorama
from colorama import Fore
from pathlib import Path


try:
    import readline
except ModuleNotFoundError:
    print('If you are on windows, you can install pyreadline to have the same functionnalities as readline.')
    raise

colorama.init()
HOME = str(Path.home())


def path_complete(is_dir=False):
    def _path_complete(text):
        text = text.replace('~', HOME)

        suggs = glob.glob(text + '*')
        real_sugg = []

        if suggs:
            for i, sugg in enumerate(suggs):

                sugg = sugg.replace(HOME, '~')
                sugg = sugg.replace('\\', '/')

                if os.path.isdir(sugg) and not sugg.endswith('/'):
                    sugg += '/'

                if is_dir and not os.path.isdir(sugg):
                    continue

                real_sugg.append(sugg)

        return real_sugg
    return _path_complete


def prompt_autocomplete(prompt, complete, default=None, contains_spaces=True, show_default=True, color=None):
    """
    Prompt a string with autocompletion

    :param complete: A function that returns a list of possible strings that
        should be completed on a given text.
        def complete(text: str) -> List[str]: ...
    """

    def real_completer(text, state):
        possibilities = complete(text) + [None]

        if possibilities:
            return possibilities[state]
        return None

    readline.set_completer_delims('\t\n' + ' ' * (not contains_spaces))
    readline.parse_and_bind("tab: complete")
    readline.set_completer(real_completer)
    
    if default is not None and show_default:
        prompt += ' [%s]' % default

    prompt += ': '

    colors = {
        'red': Fore.RED,
        'blue': Fore.BLUE,
        'green': Fore.GREEN,
        'cyan': Fore.CYAN,
        'magenta': Fore.MAGENTA,
        'yellow': Fore.YELLOW,
        'white': Fore.WHITE,
        'black': Fore.LIGHTBLACK_EX
    }

    if color:
        prompt = colors[color.lower()] + prompt + Fore.RESET

    if default is not None:
        r = input(prompt)
    else:
        while True:
            r = input(prompt)
            if r:
                break

    r = r or default

    # remove the autocompletion before quitting for future input()
    readline.parse_and_bind('tab: self-insert')
    readline.set_completer(None)

    return r


def prompt_file(prompt, default=None, must_exist=True, is_dir=False, show_default=True, color=None):
    """
    Prompt a filename using using glob for autocompetion.

    If must_exist is True (default) then you can be sure that the value returned
    is an existing filename or directory name.
    If is_dir is True, this will show only the directories for the completion.
    """

    if must_exist:
        while True:
            r = prompt_autocomplete(prompt, path_complete(is_dir), default, show_default=show_default, color=color)
            if os.path.exists(r):
                break
            print('This path does not exist.')
    else:
        r = prompt_autocomplete(prompt, path_complete(is_dir), default, show_default=show_default, color=color)

    return r


def prompt_choice(prompt, possibilities, default=None, only_in_poss=True, show_default=True, color=None):
    """
    Prompt for a string in a given range of possibilities.

    This also sets the history to the list of possibilities so
    the user can scroll is with the arrow to find  what he wants,
    If only_in_poss is False, you are not guaranteed that this
    will return one of the possibilities.
    """

    assert len(possibilities) >= 1
    assert not only_in_poss or default is None or default in possibilities, '$s not in possibilities' % default

    contains_spaces = any(' ' in poss for poss in possibilities)

    possibilities = sorted(possibilities)

    readline.clear_history()
    for kw in possibilities:
        readline.add_history(kw)

    def complete(text):
        return [t for t in possibilities if t.startswith(text)]

    while 1:
        r = prompt_autocomplete(prompt, complete, default, contains_spaces=contains_spaces, show_default=show_default, color=color)
        if not only_in_poss or r in possibilities:
            break
        print('%s is not a possibility.' % r)
        
    readline.clear_history()

    return r


__all__ = ['prompt_autocomplete', 'prompt_file', 'prompt_choice']