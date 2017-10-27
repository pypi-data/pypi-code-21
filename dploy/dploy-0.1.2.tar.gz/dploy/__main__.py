#!/usr/bin/env python3
"""
The entry point when dploy is called as a module
"""

import sys
from dploy import cli
assert sys.version_info >= (3, 3), "Requires Python 3.3 or Greater"


def main():
    """
    main entry point when using dploy from the command line
    """
    cli.run()


if __name__ == '__main__':
    main()
