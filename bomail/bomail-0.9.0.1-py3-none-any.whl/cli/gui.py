####
# bomail.cli.gui
#
# Launch the user interface (which is text based, so not a GUI. I know)
####

import sys
import os
import locale
import curses

import bomail.guistuff.mygui as mygui


def main(screen):
  mygui.main(screen)


def main_cli():
  os.environ.setdefault('ESCDELAY', '25')
  locale.setlocale(locale.LC_ALL, '')
  curses.wrapper(main)


if __name__ == "__main__":
  main_cli()

