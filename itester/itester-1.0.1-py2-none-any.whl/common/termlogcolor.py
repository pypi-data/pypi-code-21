#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Meng xiangguo <mxgnene01@gmail.com>
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |]
#    [________]_|__|________)<     |MENG|
#     oo    oo  'oo OOOO-| oo\_   ~o~~~o~'
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#                        17/5/27  下午7:54

from __future__ import print_function
import os
import sys
import datetime

'''
参考： https://pypi.python.org/pypi/termcolor
'''
__ALL__ = [ 'colored', 'cprint' ]

VERSION = (1, 1, 0)

ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
            ],
            list(range(1, 9))
            ))
        )
del ATTRIBUTES['']


HIGHLIGHTS = dict(
        list(zip([
            'on_grey',
            'on_red',
            'on_green',
            'on_yellow',
            'on_blue',
            'on_magenta',
            'on_cyan',
            'on_white'
            ],
            list(range(40, 48))
            ))
        )


COLORS = dict(
            list(zip(['grey','red','green','yellow'],[47, 41, 42, 43]))
        )


END = '\033[0m'


def colored(text, color=None, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, grey.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['grey', 'blink'])
        colored('Hello, World!', 'green')
    """
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%d;30;1m%s'
        if color is not None:
            text = fmt_str % (COLORS[color], text)

        if on_color is not None:
            text = fmt_str % (HIGHLIGHTS[on_color], text)

        if attrs is not None:
            for attr in attrs:
                text = fmt_str % (ATTRIBUTES[attr], text)

        text += END
    return text


def cprint(text, color=None, on_color=None, attrs=None, **kwargs):

    print((colored(text, color, on_color, attrs)), **kwargs)


# next bit filched from 1.5.2's inspect.py
def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back


def findCaller():

    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    """
    if hasattr(sys, 'frozen'):  # support for py2exe
        _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
    elif __file__[-4:].lower() in ['.pyc', '.pyo']:
        _srcfile = __file__[:-4] + '.py'
    else:
        _srcfile = __file__

    _srcfile = os.path.normcase(_srcfile)

    f = currentframe()
    # On some versions of IronPython, currentframe() returns None if
    # IronPython isn't run with -X:Frames.
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == _srcfile:
            f = f.f_back
            continue
        rv = (co.co_filename, f.f_lineno, co.co_name)
        break
    return rv

class TermColor():
    '''
    支持jenkins 支持输出颜色
    '''
    colormap = dict(
        concern=dict(color='green', attrs=['bold']),
        info=dict(color='grey'),
        warn=dict(color='yellow', attrs=['bold']),
        warning=dict(color='yellow', attrs=['bold']),
        error=dict(color='red'),
        critical=dict(color='red', attrs=['bold']),
    )

    def msg_format(self, mode, msg):
        '''
        获取调用者的 文件名、调用函数、调用行
        '''
        fn, lineno, co_name = findCaller()
        filename = fn.split('/')[-1]
        now_date = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        msg_simple = ('[-] %s - %s(%s:%s@%s): %s') % (now_date, mode, filename, co_name, str(lineno), msg)

        return msg_simple

    def info(self, msg):
        self._log("info", msg)

    def concern(self, msg):
        self._log("concern", msg)

    def error(self, msg):
        self._log("error", msg)

    def warn(self, msg):
        self._log("warn", msg)

    def _log(self, funcname, msg):
        print(colored(self.msg_format(funcname, msg), **self.colormap[funcname]))


log = TermColor()

if __name__ == '__main__':
    print('Current terminal type: %s' % os.getenv('TERM'))
    print('Test basic colors:')
    cprint('Grey color', 'grey')
    cprint('Red color', 'red')
    cprint('Green color', 'green')
    cprint('Yellow color', 'yellow')
    print(('-' * 78))

    print('Test highlights:')
    cprint('On grey color', on_color='on_grey')
    cprint('On red color', on_color='on_red')
    cprint('On green color', on_color='on_green')
    cprint('On yellow color', on_color='on_yellow')
    cprint('On blue color', on_color='on_blue')
    cprint('On magenta color', on_color='on_magenta')
    cprint('On cyan color', on_color='on_cyan')
    cprint('On white color', color='grey', on_color='on_white')
    print('-' * 78)

    print('Test attributes:')
    cprint('Bold grey color', 'grey', attrs=['bold'])
    cprint('Dark red color', 'red', attrs=['dark'])
    cprint('Underline green color', 'green', attrs=['underline'])
    cprint('Blink yellow color', 'yellow', attrs=['blink'])
    print(('-' * 78))

    print('Test mixing:')
    cprint('Underline red on grey color', 'red', 'on_grey',
            ['underline'])
    cprint('Reversed green on red color', 'green', 'on_red', ['reverse'])

