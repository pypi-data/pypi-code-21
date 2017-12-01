"""trapmk: TrapHack adventure builder.

Usage:
    trapmk DIRECTORY
    trapmk --version
    trapmk (-h | --help)

Options:
    --version       Show version.
    -h --help       Show this screen.

"""

import sys

from docopt import docopt

from . import __version__
from . import trapmk


def entrypoint():
    """The Python "entrypoint" (main) of this CLI script.

    """

    arguments = docopt(__doc__, version='trapmk v' + __version__)
    if 'DIRECTORY' in arguments:
        trapmk.build_adventure(arguments['DIRECTORY'])
    elif arguments['--version']:
        print(__version__)
