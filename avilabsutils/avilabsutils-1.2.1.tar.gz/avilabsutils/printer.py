import sys
from termcolor import cprint
from colorama import init

init()


def print_warn(text, *args, **kwargs):
    cprint(text, 'yellow', *args, **kwargs)


def print_error(text, *args, **kwargs):
    cprint(text, 'red', *args, **kwargs)


def print_success(text, *args, **kwargs):
    cprint(text, 'green', *args, **kwargs)


def print_code(text, *args, **kwargs):
    cprint(text, 'cyan', *args, **kwargs)


def print_now(text, *args, **kwargs):
    print(text, *args, **kwargs)
    sys.stdout.flush()

