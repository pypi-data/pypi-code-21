import os
import sys
from echocolor.colorizer import Colorizer
from echocolor.escape_codes import COLORS, style


class TerminalEcho:
    def __init__(self, output=sys.stdout, force_color=False, colors=None):
        self.output = output
        self.force_color = force_color
        colors = colors or COLORS
        self.define_colors(colors)

    def define_colors(self, colors):
        for fg_color in colors:
            colorizer = Colorizer(fg_color, out=self.output)
            setattr(self, colorizer.__name__, self._color_out(colorizer))
            for bg_color in colors:
                colorizer = Colorizer(fg_color, bg_color, out=self.output)
                setattr(self, colorizer.__name__, self._color_out(colorizer))

    def _color_out(self, fn):
        def _fn(msg, *args, **kwargs):
            newline = kwargs.pop('newline', True)
            _kwargs = {
                'force': self.force_color,
            }
            _kwargs.update(kwargs)
            self.__call__(fn(msg, *args, **_kwargs), newline)
        return _fn

    @property
    def _tty_out(self):
        return hasattr(self.output, 'isatty') and self.output.isatty()

    def bold(self, msg, newline=True, force=False):
        if self._tty_out or self.force_color or force:
            msg = style('bold') + msg + style('reset')
        self.__call__(msg, newline=newline)

    def underline(self, msg, newline=True, force=False):
        if self._tty_out or self.force_color or force:
            msg = style('underlined') + msg + style('reset')
        self.__call__(msg, newline=newline)

    def __call__(self, msg, newline=True):
        self.output.write(self._format(msg, newline))

    def _format(self, msg, newline=True):
        if newline:
            return "{}\n".format(msg)
        else:
            return "{}".format(msg)


echo = TerminalEcho()

err = TerminalEcho(sys.stderr)
