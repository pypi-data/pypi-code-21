#!/usr/bin/env python
# coding=utf-8
"""
This is the console entry point (from setup.py) for the FullMonty application.

"""

# hack the system path so you can run this file directly in your dev environment and it also works fine packaged.
# note that importing hack_sys_path will modify the system path so should be the first import in your "main" module.
# noinspection PyUnresolvedReferences
import hack_sys_path

from fullmonty.fullmonty_app import FullMontyApp
from fullmonty.fullmonty_cli import FullMontyCLI

__docformat__ = 'restructuredtext en'
__all__ = ('main',)


def main():
    """
    This is the console entry point.
    """

    cli = FullMontyCLI()
    cli.execute(FullMontyApp())


if __name__ == '__main__':
    main()
