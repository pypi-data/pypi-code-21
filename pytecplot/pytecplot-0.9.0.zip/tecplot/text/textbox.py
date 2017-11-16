from builtins import super

from .. import constant, session
from ..tecutil import sv

#
# Note: The TextBox class is similar to the annotation.TextBox class, except
# that annotation.TextBox is specific to text annotations and uses the
# TecUtilText API to get/set properties.
#
# The TextBox class below uses style to get/set properties.
#
# Therefore, this class must be separate from annotation.TextBox
#


class TextBox(session.Style):
    """Rectangular frame around a text element.

    .. warning::

        `text.TextBox` objects cannot be created directly. They are returned by
        various other read-only properties.

    """
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent._sv, sv.BOX, **parent._style_attrs)

    @property
    def box_type(self):
        """Type of box surrounding the text.

        :type: `constant.TextBox`

        Example usage::

            >>> plot = frame.plot()
            >>> plot.legend.box.box_type = constant.TextBox.None_
        """
        return self._get_style(constant.TextBox, sv.BOXTYPE)

    @box_type.setter
    def box_type(self, value):
        self._set_style(constant.TextBox(value), sv.BOXTYPE)

    @property
    def color(self):
        """Color of the box surrounding the text.

        :type: `Color`

        Example usage::

            >>> plot = frame.plot()
            >>> plot.legend.box.color = Color.Blue
        """
        return self._get_style(constant.Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(constant.Color(value), sv.COLOR)

    @property
    def fill_color(self):
        """Fill color of the box surrounding the text.

        :type: `Color`

        Example usage::

            >>> plot = frame.plot()
            >>> plot.legend.box.fill_color = Color.Blue
        """
        return self._get_style(constant.Color, sv.FILLCOLOR)

    @fill_color.setter
    def fill_color(self, value):
        self._set_style(constant.Color(value), sv.FILLCOLOR)

    @property
    def line_thickness(self):
        """Line thickness of the box surrounding the text.

        :type: `float`

        Example usage::

            >>> plot = frame.plot()
            >>> plot.legend.box.line_thickness = 0.2
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def margin(self):
        """Margin of the box surrounding the text.

        This property is the margin between the text inside the text box
        and the box as a percentage of frame height.

        :type: `float`

        Example usage::

            >>> plot = frame.plot()
            >>> plot.legend.box.margin = 0.3
        """
        return self._get_style(float, sv.MARGIN)

    @margin.setter
    def margin(self, value):
        self._set_style(float(value), sv.MARGIN)
