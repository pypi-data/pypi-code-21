"""
This modules defines functions to enhance the basic input() for the standard lib with autocompletion.
"""

import glob
import os
from pathlib import Path


try:
    import readline
except ModuleNotFoundError:
    print('If you are on windows, you can install pyreadline to have the same functionnalities as readline.')
    raise

HOME = str(Path.home())


def prompt_autocomplete(prompt, complete, default=None):
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

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(real_completer)

    if default is not None:
        r = input('%s [%s]: ' % (prompt, default))
    else:
        r = ''
        while not r:
            r = input('%s: ' % prompt)

    r = r or default

    # remove the autocompletion before quitting for future input()
    readline.parse_and_bind('tab: self-insert')
    readline.set_completer(None)

    return r


def prompt_file(prompt, default=None, must_exist=True, is_dir=False):
    """
    Prompt a filename using using glob for autocompetion.
    
    If must_exist is True (default) then you can be sure that the value returned 
    is an existing filename or directory name.
    If is_dir is True, this will show only the directories for the completion.
    """

    def complete(text):
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
    
    if must_exist:
        r = prompt_autocomplete(prompt, complete, default)
        while not os.path.exists(r):
            print('This path does not exist.')
            r = prompt_autocomplete(prompt, complete, default)
    else:
        r = prompt_autocomplete(prompt, complete, default)

    return r

def prompt_choice(prompt, possibilities, default=None):
    """
    Prompt for a string in a given range of possibilities.

    The default must be in this range too.
    """

    assert len(possibilities) >= 1
    assert default is None or default in possibilities

    def complete(text):
        return [t for t in possibilities if t.startswith(text)]

    r = prompt_autocomplete(prompt, complete, default)
    while r not in possibilities:
        print('%s is not a possibility.' % r)
        r = prompt_autocomplete(prompt, complete, default)

    return r


__all__ = ['prompt_autocomplete', 'prompt_file', 'prompt_choice']