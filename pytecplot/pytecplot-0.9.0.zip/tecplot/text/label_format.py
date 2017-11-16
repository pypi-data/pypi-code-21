from builtins import int, super

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import session
from ..tecutil import Index, StringList, flatten_args, lock, sv


class LabelFormat(session.Style):
    """Formatting of numbers shown along in axes and in legends.

    This example shows how to format tick label along an axis:

    .. code-block:: python
        :emphasize-lines: 31-36

        from datetime import datetime
        import tecplot as tp
        from tecplot.constant import PlotType, AxisMode, AxisAlignment, NumberFormat

        tp.new_layout()
        plot = tp.active_frame().plot(tp.constant.PlotType.Sketch)
        plot.activate()

        # setup the plot area margins
        plot.axes.viewport.left = 10
        plot.axes.viewport.right = 90

        # show the x-axis, set the title, and alignment with the viewport
        xaxis = plot.axes.x_axis
        xaxis.show = True
        xaxis.title.text = 'Negative numbers in parentheses'
        xaxis.title.offset = 20
        xaxis.line.alignment = AxisAlignment.WithViewport
        xaxis.line.position = 50

        # set limits, tick placement and tick label properties
        xaxis.ticks.auto_spacing = False
        xaxis.min, xaxis.max = -5.123e-5, 5.234e-5
        xaxis.ticks.spacing = (xaxis.max - xaxis.min) / 6
        xaxis.ticks.spacing_anchor = 0
        xaxis.tick_labels.angle = 45
        xaxis.tick_labels.offset = 3

        # format the tick labels in superscript form. example: 1.234x10^5
        # format negative numbers to use parentheses instead of a negative sign
        xformat = xaxis.tick_labels.format
        xformat.format_type = NumberFormat.SuperScript
        xformat.precision = 3
        xformat.show_negative_sign = False
        xformat.negative_prefix = '('
        xformat.negative_suffix = ')'

        tp.export.save_png('label_format.png', 600, supersample=3)

    ..  figure:: /_static/images/label_format.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, labels):
        self.labels = labels
        super().__init__(labels._sv, sv.NUMFORMAT, **labels._style_attrs)

    @property
    def format_type(self):
        """Type of number formatting to use.

        :type: `NumberFormat`

        Possible values: `Integer`, `FixedFloat`, `Exponential`, `BestFloat`,
        `SuperScript`, `CustomLabel`, `LogSuperScript`, `RangeBestFloat`,
        `DynamicLabel`, `TimeDate`.

        Example usage::

            >>> from tecplot.constant import NumberFormat
            >>> axis.tick_labels.format.format_type = NumberFormat.BestFloat
        """
        return self._get_style(NumberFormat, sv.FORMATTING)

    @format_type.setter
    def format_type(self, value):
        self._set_style(NumberFormat(value), sv.FORMATTING)

    @property
    def custom_labels_index(self):
        """Index of the custom label to use.

        :type: `Index` (zero-based)

        Example usage::

            >>> axis.tick_labels.format.custom_labels_index = 0
        """
        return self._get_style(Index, sv.CUSTOMLABEL)

    @custom_labels_index.setter
    def custom_labels_index(self, index):
        index = (self.num_custom_labels + index) if index < 0 else index
        self._set_style(Index(index), sv.CUSTOMLABEL)

    @property
    def num_custom_labels(self):
        """Number of custom label sets available to use.

        :type: `int`

        Example usage::

            >>> print(axis.tick_labels.format.num_custom_labels)
            1
        """
        return _tecutil.CustomLabelsGetNumSets()

    def custom_labels(self, index):
        """List of labels for custom labels for set specified by index.

        Example usage::

            >>> axis.tick_labels.format.custom_labels(0)
            ['apples', 'bananas', 'carrots']
        """
        index = (self.num_custom_labels + index) if index < 0 else index
        sl = _tecutil.CustomLabelsGet(index + 1)
        ret = list(sl)
        sl.dealloc()
        return ret

    @lock()
    def add_custom_labels(self, *labels):
        """Append a list of custom labels as a new set.

        Example usage::

            >>> labels = ['apples', 'bananas', 'carrots']
            >>> axis.tick_labels.format.add_custom_labels(*labels)
            >>> print(axis.tick_labels.format.custom_labels(-1))
            ['apples', 'bananas', 'carrots']
        """
        with StringList(*flatten_args(labels)) as sl:
            if not _tecutil.CustomLabelsAppend(sl):
                raise TecplotSystemError()

    @property
    def precision(self):
        """Number digits after decimal for fixed floating point format.

        :type: `integer <int>`

        Example usage::

            >>> from tecplot.constant import NumberFormat
            >>> axis.tick_labels.format.format_type = NumberFormat.FixedFloat
            >>> axis.tick_labels.format.precision = 3
        """
        return self._get_style(int, sv.PRECISION)

    @precision.setter
    def precision(self, value):
        self._set_style(int(value), sv.PRECISION)

    @property
    def remove_leading_zeros(self):
        """Strip leading zeros in the formatted number.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.tick_labels.format.remove_leading_zeros = True
        """
        return self._get_style(bool, sv.REMOVELEADINGZEROS)

    @remove_leading_zeros.setter
    def remove_leading_zeros(self, value):
        self._set_style(bool(value), sv.REMOVELEADINGZEROS)

    @property
    def show_decimals_on_whole_numbers(self):
        """Include trailing decimal character with whole numbers.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.tick_labels.format.show_decimals_on_whole_numbers = True
        """
        return self._get_style(bool, sv.SHOWDECIMALSONWHOLENUMBERS)

    @show_decimals_on_whole_numbers.setter
    def show_decimals_on_whole_numbers(self, value):
        self._set_style(bool(value), sv.SHOWDECIMALSONWHOLENUMBERS)

    @property
    def show_negative_sign(self):
        """Include negative sign for negative values.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.tick_labels.format.show_negative_sign = True
        """
        return self._get_style(bool, sv.SHOWNEGATIVESIGN)

    @show_negative_sign.setter
    def show_negative_sign(self, value):
        self._set_style(bool(value), sv.SHOWNEGATIVESIGN)

    @property
    def negative_prefix(self):
        """Prefix string to use for negative valued tick labels.

        :type: `string <str>`

        This example shows how to use parentheses instead of a negative sign::

            >>> axis.tick_labels.format.show_negative_sign = False
            >>> axis.tick_labels.format.negative_prefix = '('
            >>> axis.tick_labels.format.negative_suffix = ')'
        """
        return self._get_style(str, sv.NEGATIVEPREFIX)

    @negative_prefix.setter
    def negative_prefix(self, value):
        self._set_style(str(value), sv.NEGATIVEPREFIX)

    @property
    def negative_suffix(self):
        """Suffix string to use for negative valued tick labels.

        :type: `string <str>`

        This example shows how to use parentheses instead of a negative sign::

            >>> axis.tick_labels.format.show_negative_sign = False
            >>> axis.tick_labels.format.negative_prefix = '('
            >>> axis.tick_labels.format.negative_suffix = ')'
        """
        return self._get_style(str, sv.NEGATIVESUFFIX)

    @negative_suffix.setter
    def negative_suffix(self, value):
        self._set_style(str(value), sv.NEGATIVESUFFIX)

    @property
    def positive_prefix(self):
        """Prefix string to use for positive valued tick labels.

        :type: `string <str>`

        Example usage::

            >>> axis.tick_labels.format.positive_prefix = 'increase: '
        """
        return self._get_style(str, sv.POSITIVEPREFIX)

    @positive_prefix.setter
    def positive_prefix(self, value):
        self._set_style(str(value), sv.POSITIVEPREFIX)

    @property
    def positive_suffix(self):
        """Suffix string to use for positive valued tick labels.

        :type: `string <str>`

        Example usage::

            >>> axis.tick_labels.format.positive_suffix = ' (m)'
        """
        return self._get_style(str, sv.POSITIVESUFFIX)

    @positive_suffix.setter
    def positive_suffix(self, value):
        self._set_style(str(value), sv.POSITIVESUFFIX)

    @property
    def zero_prefix(self):
        """Prefix string to use for zero valued tick labels.

        :type: `string <str>`

        Example usage::

            >>> axis.tick_labels.format.zero_prefix = 'origin: '
        """
        return self._get_style(str, sv.ZEROPREFIX)

    @zero_prefix.setter
    def zero_prefix(self, value):
        self._set_style(str(value), sv.ZEROPREFIX)

    @property
    def zero_suffix(self):
        """Suffix string to use for zero valued tick labels.

        :type: `string <str>`

        Example usage::

            >>> axis.tick_labels.format.zero_suffix = ' (origin)'
        """
        return self._get_style(str, sv.ZEROSUFFIX)

    @zero_suffix.setter
    def zero_suffix(self, value):
        self._set_style(str(value), sv.ZEROSUFFIX)

    @property
    def datetime_format(self):
        r"""The date/time format to be used.

        :type: `string <str>`

        Example usage::

            >>> from tecplot.constant import NumberFormat
            >>> axis.tick_labels.format.format_type = NumberFormat.TimeDate
            >>> axis.tick_labels.format.datetime_format = 'mmm d, yyyy'

        The format can be any combination of the following codes. Placing a
        backslash in front of a y, m, d, or s in the Time/Date formula will
        keep it from being processed as part of the formula. All characters not
        part of the Time/Date formula will appear as entered. For example,
        "\\year yyyy" will appear as "year 2008", as the backslash keeps the
        first y from being processed as part of the formula. If you use "m"
        immediately after the "h" or "hh" code or immediately before the "ss"
        code, the minutes instead of the month will be displayed.

        =============== =========================
        Years:
        -----------------------------------------
            ``yy``      00-99
            ``yyyy``    1800-9999
        --------------- -------------------------
        Months:
        -----------------------------------------
            ``m``       1-12
            ``mm``      01-12
            ``mmm``     Jan-Dec
            ``mmmm``    January-December
            ``mmmmm``   first letter of the month
        --------------- -------------------------
        Days:
        -----------------------------------------
            ``[d]``     elapsed days
            ``d``       1-31
            ``dd``      01-31
            ``ddd``     Sun-Sat
            ``dddd``    Sunday-Saturday
            ``ddddd``   S,M,T,W,T,F,S
        --------------- -------------------------
        Hours:
        -----------------------------------------
            ``[h]``     elapsed hours
            ``h``       0-23 or 1-12
            ``hh``      00-23 or 1-12
            ``AM/PM``   AM or PM
            ``A/P``     AM or PM as "A" or "P"
        --------------- -------------------------
        Minutes:
        -----------------------------------------
            ``[m]``     elapsed minutes
            ``m``       0-59
            ``mm``      00-59
        --------------- -------------------------
        Seconds:
        --------------- -------------------------
            ``s``       0-59
            ``ss``      00-59
            ``.0``      Tenths
            ``.00``     Hundredths
            ``.000``    Thousandths
        =============== =========================

        To display the time and date on your plot as a "Sat-Jan-05-2008", enter
        the following code::

            "ddd-mmm-dd-yyyy"

        To display the time and date on your plot as a "1-3-08", enter the
        following code::

            "m-d-yy"

        To display the time and date on your plot as a "9:30:05 AM", enter the
        following code::

            "h:mm:ss AM"

        To display an elapsed time, such as "3:10:15", enter the following
        code::

            "[d]:hh:mm"
        """
        return self._get_style(str, sv.TIMEDATEFORMAT)

    @datetime_format.setter
    def datetime_format(self, value):
        self._set_style(str(value), sv.TIMEDATEFORMAT)
