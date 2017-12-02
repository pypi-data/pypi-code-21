import sys
from echocolor.escape_codes import COLORS, bg, fg, style


class Colorizer:
    """
    Create a callable object that wraps a string in an ANSI escape sequence to color it in
    terminal output.
    """
    force_color = False

    def __init__(self, color, bg_color=None, out=sys.stdout):
        """
        color should be a lowercase name of a color, eg "cyan", "red", "green".
        bg_color is optional and should also be a lowercase color name.
        """
        self.color = color
        self.bg_color = bg_color
        self.out = out

    @property
    def __name__(self):
        if self.bg_color:
            return '{}_on_{}'.format(self.color.lower(), self.bg_color.lower())
        else:
            return self.color.lower()

    def __call__(self, msg, force=False, output=None):
        """
        By default, if self.out is not a terminal, this will just return the string that
        is passed in. This can be changed by passing force=True as a keyword argument.
        """
        output = output or self.out
        terminal_out = (hasattr(output, 'isatty') and output.isatty())
        if terminal_out or force or self.force_color:
            return self._colorize(msg)
        else:
            return msg

    @property
    def style(self):
        if self.bg_color is None:
            return fg(self.color)
        else:
            return fg(self.color) + bg(self.bg_color)

    def _colorize(self, msg):
        return self.style + msg + style('reset')
