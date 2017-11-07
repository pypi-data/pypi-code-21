import argparse
import sys
import os

from .core import install, uninstall


def info():
    exe = os.path.normpath(os.path.join(os.path.dirname(sys.executable), 'gpython.exe'))
    print(exe if os.path.isfile(exe) else 'gpython.exe is not installed')


FUNCTION_MAP = {
    'info': info,
    'install': install,
    'uninstall': uninstall,
}

parser = argparse.ArgumentParser()
parser.add_argument('command', nargs='?', default='info', choices=FUNCTION_MAP.keys())
args = parser.parse_args()

func = FUNCTION_MAP[args.command]
func()
