from builtins import super

from ..constant import *
from ..exception import *
from .. import session
from ..text import Font
from ..tecutil import XYPosition, sv


class LegendFont(Font):
    """LegendFont is a font that restricts the setting of size_units."""
    def __init__(self, parent, sv_textshape=sv.TEXTSHAPE):
        super().__init__(parent, sv_textshape)

    @property
    def size_units(self):
        """Units used by the size attribute.

        :type: `Units <constant.Units>`

        Possible values: `Units.Point`, `Units.Frame` (percentage of frame
        height). This example sets the axis title to 10% of the frame height::

            >>> legend.font.size_units = Units.Frame
            >>> legend.font.size = 10
        """
        return self._get_style(Units, sv.SIZEUNITS)

    @size_units.setter
    def size_units(self, value):
        value = Units(value)
        if __debug__:
            if value not in (Units.Frame, Units.Point):
                msg = '''\
                    Legend font size units must be one of:
                    Units.Frame, Units.Point'''
                raise TecplotValueError(msg)
        self._set_style(value, sv.SIZEUNITS)


class Legend(session.Style):
    @property
    def show(self):
        """Show or hide the legend.

        :type: `boolean <bool>`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> legend = frame.plot(PlotType.XYLine).legend
            >>> legend.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def anchor_alignment(self):
        """Anchor location of the legend.

        :type: `AnchorAlignment`

        Example usage::

            >>> from tecplot.constant import AnchorAlignment, PlotType
            >>> legend = frame.plot(PlotType.XYLine).legend
            >>> legend.anchor_alignment = AnchorAlignment.BottomCenter
        """
        return self._get_style(AnchorAlignment, sv.ANCHORALIGNMENT)

    @anchor_alignment.setter
    def anchor_alignment(self, value):
        self._set_style(AnchorAlignment(value), sv.ANCHORALIGNMENT)

    @property
    def row_spacing(self):
        """Spacing between rows in the legend.

        :type: `float`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> legend = frame.plot(PlotType.XYLine).legend
            >>> legend.row_spacing = 1.5
        """
        return self._get_style(float, sv.ROWSPACING)

    @row_spacing.setter
    def row_spacing(self, value):
        self._set_style(float(value), sv.ROWSPACING)

    @property
    def text_color(self):
        """Color of legend text.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import PlotType, Color
            >>> legend = frame.plot(PlotType.XYLine).legend
            >>> legend.text_color = Color.Blue
        """
        return self._get_style(Color, sv.TEXTCOLOR)

    @text_color.setter
    def text_color(self, value):
        self._set_style(Color(value), sv.TEXTCOLOR)

    @property
    def position(self):
        """Position of the legend as a percentage of frame width/height.

        The legend is automatically placed for you. You may specify the
        :math:`(x,y)` position of the legend by setting this value, where
        :math:`x` is the percentage of frame width, and :math:`y` is a
        percentage of frame height.

        :type: 2-`tuple` of `floats <float>`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> legend = frame.plot(PlotType.XYLine).legend
            >>> legend.position = (.1, .3)
            >>> pos = legend.position
            >>> pos.x  # == position[0]
            .1
            >>> pos.y  # == position[1]
            .3
        """
        return self._get_style(XYPosition, sv.XYPOS)

    @position.setter
    def position(self, pos):
        self._set_style(XYPosition(*pos), sv.XYPOS)
