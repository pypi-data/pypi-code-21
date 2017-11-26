from typing import Any

from hues import huestr

from amino import __


def green(msg: Any) -> str:
    return huestr(str(msg)).green.colorized


def red(msg: Any) -> str:
    return huestr(str(msg)).red.colorized


def yellow(msg: Any) -> str:
    return huestr(str(msg)).yellow.colorized


def blue(msg: Any) -> str:
    return huestr(str(msg)).blue.colorized


def magenta(msg: Any) -> str:
    return huestr(str(msg)).magenta.colorized

indent = __.map(' {}'.format)

green_check = green('✓')

red_cross = red('✗')

yellow_clock = yellow('⌚')

green_plus = green('+')

red_minus = red('-')

spec_sign = '⛤'


def spec_headline(mod: str) -> str:
    return magenta(f'{spec_sign} {mod}')


__all__ = ('indent', 'green_check', 'red_cross', 'green', 'red', 'yellow_clock', 'green_plus', 'red_minus', 'blue',
           'magenta', 'spec_sign', 'spec_headline')
