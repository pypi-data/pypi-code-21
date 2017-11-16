from collections import namedtuple

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from ..tecutil import lock
from .annotation import Annotation, annotation_preamble


class TextBox(object):
    """The Box surrounding a `Text` object.

    .. warning::

        `annotation.TextBox` objects cannot be created directly. They are
        returned by the `annotation.Text.text_box` read-only property.

    """
    def __init__(self, uid, frame):
        self.uid = uid
        self.frame = frame

    def __str__(self):
        """The text to be displayed within the text box."""
        _, text_string = _tecutil.TextGetString(self.uid)
        return text_string

    @property
    @annotation_preamble
    def line_thickness(self):
        """Border line thickness.

        :type: `float <float>` (greater than 0, default: 0.1)

        Example showing how to set the line thickness of the `text box
        <annotation.TextBox>` for a `Text` object::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.line_thickness = 0.5
            >>> text.text_box.line_thickness
            0.5
        """
        return _tecutil.TextBoxGetLineThickness(self.uid)

    @line_thickness.setter
    @annotation_preamble
    def line_thickness(self, line_thickness):
        with lock():
            if __debug__ and line_thickness <= 0.0:
                raise TecplotLogicError(
                    'TextBox line thickness must be greater than 0.0')

            _tecutil.TextBoxSetLineThickness(self.uid, float(line_thickness))

    @property
    @annotation_preamble
    def margin(self):
        """Margin between the text and the surrounding border.

        Specify the margin as a percentage of the text character height. Margin
        must be greater than or equal to 0.0, and may be greater than 100.
        (default = 20.0)

        :type: `float <float>`

        Example showing how to set the margin of the `text box <TextBox>` for a
        `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.margin = 0.5
            >>> text.text_box.margin
            0.5
        """
        return _tecutil.TextBoxGetMargin(self.uid)

    @margin.setter
    @annotation_preamble
    def margin(self, margin):
        with lock():
            if __debug__ and margin < 0.0:
                raise TecplotLogicError('TextBox margin must be >= 0.0')

            _tecutil.TextBoxSetMargin(self.uid, float(margin))

    @property
    def fill_color(self):
        """Background fill color of the text box.

        :type: `Color`

        Example showing how to set the fill color of the `text box <TextBox>`
        for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.fill_color = Color.Blue
            >>> text.text_box.fill_color
            Color.Blue
        """
        return Color(_tecutil.TextBoxGetFillColor(self.uid))

    @fill_color.setter
    @lock()
    def fill_color(self, color):
        with self.frame.activated():
            _tecutil.TextBoxSetFillColor(self.uid, Color(color).value)

    @property
    def color(self):
        """Border line color of the text box.

        :type: `Color` (default: `Color.Black`)

        Example showing how to set the outline color of the `text box
        <TextBox>` for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.color = Color.Blue
            >>> text.text_box.color
            Color.Blue
        """
        return Color(_tecutil.TextBoxGetColor(self.uid))

    @color.setter
    @lock()
    def color(self, color):
        with self.frame.activated():
            _tecutil.TextBoxSetColor(self.uid, Color(color).value)

    _Position = namedtuple('Position', 'x1 y1 x2 y2 x3 y3 x4 y4')

    @property
    @annotation_preamble
    def position(self):
        """Position of the four corners of the `text box <TextBox>`.

        **Note:** This property is read-only.

        :type: 8-`tuple` of `floats <float>`

            * x1: X-Coordinate for bottom left corner of the `annotation.TextBox`.
            * y1: Y-Coordinate for bottom left corner of the `annotation.TextBox`.
            * x2: X-Coordinate for bottom right corner of the `annotation.TextBox`.
            * y2: Y-Coordinate for bottom right corner of the `annotation.TextBox`.
            * x3: X-Coordinate for upper right corner of the `annotation.TextBox`.
            * y3: Y-Coordinate for upper right corner of the `annotation.TextBox`.
            * x4: X-Coordinate for upper left corner of the `annotation.TextBox`.
            * y4: Y-Coordinate for upper left corner of the `annotation.TextBox`.

        There is no default, position will vary with text box properties.
        Example showing how to query position of the `text box <TextBox>` for a
        `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> x1,y1,x2,y2,x3,y3,x4,y4 = text.text_box.position
            >>> # x1,...,y4 contain the corners of the text box
        """
        return TextBox._Position(*_tecutil.TextBoxGetPosition(self.uid))

    @property
    @annotation_preamble
    def text_box_type(self):
        """The type of the box surrounding the `text <Text>` object

        :type: `constant.TextBox`

        The text box type can be set to the following:

            * None\_ - (default) Select this option to specify that no box is
                drawn around the text.
            * Filled - Select this option to specify a filled box around the
                text. A filled box is opaque; if you place it over another
                |Tecplot 360| object, the underlying object cannot be seen.
            * Hollow - Select this to specify a plain box around the text.

        Example showing how to set the type of the text box for a `text <Text>`
        object::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.text_box_type = TextBox.Filled
            >>> text.text_box.text_box_type
            TextBox.Filled
        """
        return _tecutil.TextBoxGetType(self.uid)

    @text_box_type.setter
    @annotation_preamble
    def text_box_type(self, text_box_type):
        with lock():
            _tecutil.TextBoxSetType(self.uid, text_box_type.value)


class Text(Annotation):
    """Text annotation.

    .. warning::

        `Text` objects cannot be created directly. They are returned by the
        `Frame.add_text()` method.

    """

    def __init__(self, uid, frame):
        super().__init__(uid, frame, Text)
        self._text_box = TextBox(uid, frame)  # type: TextBox

    def __str__(self):
        """Brief string representation.

        Returns:
            `string <str>`: Brief representation of this `Text`.

        Example::
            >>> import tecplot
            >>> frame = tecplot.active_frame()
            >>> print(frame.add_text('Orange'))
            Text: "Orange"
        """
        return self.text_string

    def __eq__(self, other):
        """Checks for `Text` equality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are the same for both
            `Text objects <Text>`.

        Example::
            >>> import tecplot
            >>> frame = tecplot.active_frame()
            >>> text_1 = frame.add_text('Orange')
            >>> text_2 = frame.add_text('Orange')
            >>> # The literal strings that the `Text` object holds are equal:
            >>> text_1.text_string == text_2.text_string
            True
            >>> # But the `Text` objects themselves are different:
            >>> text_1 == text_2
            False
        """
        return self.uid == other.uid

    def __ne__(self, other):
        """Checks for `Text` inequality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are not the same for both
            `Text objects <Text>`

        Example::
            >>> import tecplot
            >>> frame = tecplot.active_frame()
            >>> text_1 = frame.add_text('Orange')
            >>> text_2 = frame.add_text('Orange')
            >>> # The literal strings that the `Text` object holds are equal:
            >>> text_1.text_string == text_2.text_string
            True
            >>> # But the `Text` objects themselves are different:
            >>> text_1 == text_2
            False
        """

        return self.uid != other.uid

    def _delete(self):
        _tecutil.TextDelete(self.uid)

    @property
    def text_box(self):
        """The `text.TextBox` object for this `Text` object.

        The text box is a box that is drawn around the text. Note that
        in order to show the text box, you must set TextBox.type to a value
        other than TextBox.None.

       :type: `text.TextBox`

       .. note:: This property is read-only.

       Example showing how to enable the text box for a `text object
       <annotation.Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled # Show the text box
        """
        return self._text_box

    @property
    @annotation_preamble
    def typeface(self):
        """The font family used by the `Text` object.

        :type: `string <str>`

        For consistency across various platforms, |Tecplot 360| guarantees that
        the following standard typeface names are available:

            * "Helvetica"
            * "Times"
            * "Courier"
            * "Greek"
            * "Math"
            * "User Defined"

        Other typefaces may or may not be available depending on the TrueType
        fonts available. If the typeface or style is not available, a suitable
        replacement will be selected. This example shows how to set the
        typeface of a `text object <Text>` to 'Times'::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.typeface = 'Times'
            >>> text.typeface
            'Times'
        """
        return _tecutil.TextGetTypefaceFamily(self.uid)

    @typeface.setter
    @annotation_preamble
    def typeface(self, typeface):
        with lock():
            _tecutil.TextSetTypeface(
                self.uid,
                typeface,
                _tecutil.TextGetTypefaceIsBold(self.uid),
                _tecutil.TextGetTypefaceIsItalic(self.uid))

    @property
    @annotation_preamble
    def bold(self):
        """Use bold typeface in the `text object <Text>`.

        :type: `boolean <bool>`

        Example showing how to set the bold property of a `text object
        <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.typeface = 'Times'
            >>> text.bold = True
            >>> text.bold
            True
        """
        return _tecutil.TextGetTypefaceIsBold(self.uid)

    @bold.setter
    @annotation_preamble
    def bold(self, is_bold):
        with lock():
            _tecutil.TextSetTypeface(self.uid,
                                     _tecutil.TextGetTypefaceFamily(self.uid),
                                     is_bold,
                                     _tecutil.TextGetTypefaceIsItalic(self.uid))

    @property
    @annotation_preamble
    def italic(self):
        """Use italic typeface of the `text object <Text>`.

        :type: `boolean <bool>`

        Example showing how to set the italic property of a `text object
        <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.typeface = 'Times'
            >>> text.italic = True
            >>> text.italic
            False
        """
        return _tecutil.TextGetTypefaceIsItalic(self.uid)

    @italic.setter
    @annotation_preamble
    def italic(self, is_italic):
        with lock():
            _tecutil.TextSetTypeface(self.uid,
                                     _tecutil.TextGetTypefaceFamily(self.uid),
                                     _tecutil.TextGetTypefaceIsBold(self.uid),
                                     is_italic)

    @property
    @annotation_preamble
    def size(self):
        """The text size in the currently defined text size units.

        :type: `integer <int>`

        Example showing how to set the text size of a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text('abc')
            >>> text.size_units = Units.Point
            >>> text.size = 14
            >>> text.size
            14
        """
        return _tecutil.TextGetHeight(self.uid)

    @size.setter
    @annotation_preamble
    def size(self, value):
        with lock():
            _tecutil.TextSetHeight(self.uid, value)

    @property
    @annotation_preamble
    def anchor(self):
        """Anchor location for a `text object <Text>`.

        :type: `TextAnchor`

        Specify the anchor point, or fixed point, for the text object.
        As the text object grows or shrinks, the anchor location is fixed,
        while the rest of the box adjusts to accommodate the new size.
        (default = `TextAnchor.Left`)

        There are nine possible anchor position points, corresponding to the
        left, right, and center positions on the headline, midline,
        and baseline of the text box.

        Example showing how to set the anchor of a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text('abc')
            >>> text.anchor = TextAnchor.Center
            >>> text.anchor
            TextAnchor.Center
        """
        return TextAnchor(_tecutil.TextGetAnchor(self.uid))

    @anchor.setter
    @annotation_preamble
    def anchor(self, text_anchor):
        with lock():
            _tecutil.TextSetAnchor(self.uid, text_anchor.value)

    @property
    @annotation_preamble
    def angle(self):
        """Angle of the text box in degrees.

        :type: `float <float>` (degrees counter-clockwise)

        The text angle is the orientation of the text relative to the axis.
        The angle is measured in degrees counter-clockwise from horizontal.
        Horizontal text is at zero degrees; vertical text is at 90 degrees.

        Example showing how to set the angle of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.angle = 45
            >>> text.angle
            45.0
        """
        return _tecutil.TextGetAngle(self.uid)

    @angle.setter
    @annotation_preamble
    def angle(self, angle):
        with lock():
            _tecutil.TextSetAngle(self.uid, float(angle))

    @property
    @annotation_preamble
    def position_coordinate_system(self):
        """Position coordinate system of the `text object <Text>`.

        The text object may be positioned using either the grid coordinate
        system or the frame coordinate system.

        If the position_coordinate_system is `CoordSys.Frame`, then the
        size_units property must be `Units.Frame` or `Units.Point`.

        The text object's position and text height are adjusted so that it
        remains identical to its visual appearance in the original
        coordinate and unit system.

        :type: `CoordSys`, must be either `CoordSys.Frame` or `CoordSys.Grid`

        If the size units are `Units.Grid` and the position coordinate system
        is changed to `CoordSys.Frame`, then the size units will be changed
        to `Units.Frame`. (default = CoordSys.Frame)

        Example showing how to set the position coordinate system
        for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.position_coordinate_system = CoordSys.Grid
            >>> text.position_coordinate_system
            CoordSys.Grid


        Example showing side effect if size units are `CoordSys.Grid` and
        the coordinate system is changed to `CoordSys.Frame`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text("abc")
            >>> text.size_units = Units.Grid
            >>> text.size_units
            Units.Grid
            >>> # Setting the coord sys to frame will change units to frame.
            >>> text.position_coordinate_system = CoordSys.Frame
            >>> text.position_coordinate_system
            CoordSys.Frame
            >>> text.size_units
            Units.Frame

        """
        return CoordSys(_tecutil.TextGetPositionCoordSys(self.uid))

    @position_coordinate_system.setter
    @annotation_preamble
    def position_coordinate_system(self, coord_sys):
        with lock():
            size_units = _tecutil.TextGetSizeUnits(self.uid)
            if size_units == Units.Grid and coord_sys == CoordSys.Frame:
                # Set units to be frame to avoid an illegal combination
                # which would TU_ASSERT
                size_units = Units.Frame

            _tecutil.TextSetCoordSysAndUnits(
                self.uid, coord_sys.value, size_units.value)

    @property
    @annotation_preamble
    def size_units(self):
        """Units of the text character height.

        :type: `Units`

        `Units` may be one of the following:

            * `Units.Point`: Specify character height in points.
            * `Units.Frame`: Specify character height as a percentage of frame
                height
            * `Units.Grid`: Specify character height in grid units.

        (default = `Units.Point`)

        Notes::
            * One point is 1/72nd of an inch.
            * `Units.Grid` is available only if position_coordinate_system is
                `CoordSys.Grid`
            * The position coordinate system will be changed to `CoordSys.Grid`
                if size units is set to `Units.Grid`

        Example showing how to set the units of the character height for a
        `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.position_coordinate_system = CoordSys.Grid
            >>> text.size_units = Units.Point
            >>> text.size_units
            Units.Point
        """
        return Units(_tecutil.TextGetSizeUnits(self.uid))

    @size_units.setter
    @annotation_preamble
    def size_units(self, size_units):
        with lock():
            coord_sys = _tecutil.TextGetPositionCoordSys(self.uid)
            if size_units == Units.Grid:
                coord_sys = CoordSys.Grid

            _tecutil.TextSetCoordSysAndUnits(
                self.uid, coord_sys.value, Units(size_units).value)

    @property
    @annotation_preamble
    def line_spacing(self):
        """Spacing between lines in the text box.

        :type: `float <float>` (default = 1.0)

        Line spacing is dependent on the height of the text and the size unit
        system in which it is drawn. This example shows how to set the line
        spacing of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.line_spacing = 4
            >>> text.line_spacing
            4.0
        """
        return _tecutil.TextGetLineSpacing(self.uid)

    @line_spacing.setter
    @annotation_preamble
    def line_spacing(self, line_spacing):
        with lock():
            _tecutil.TextSetLineSpacing(self.uid, float(line_spacing))

    @property
    @annotation_preamble
    def text_string(self):
        """The text to be displayed in a text box.

        :type: `string <str>`

        You can embed Greek, Math, and User-defined characters into
        English-font strings by enclosing them with text formatting tags,
        together with the keyboard characters.

        The text formatting tags and their effects are as follows. Format tags
        are not case sensitive and may be either upper or lower case:

            * <b>...</b> - Boldface
            * <i>...</i> - Italic
            * <verbatim>...</verbatim> - Verbatim
            * <sub>...</sub> - Subscripts
            * <sup>...</sup> - Superscripts
            * <greek>...</greek> - Greek font.
            * <math>...</math> - Math font.
            * <userdef>...</userdef> - User-defined font.
            * <helvetica>...</helvetica> - Helvetica font.
            * <times>...</times> - Times font.
            * <courier>...</courier> - Courier font.

        Not all fonts have Bold and/or Italic variants. For fonts that do not
        have these styles, the <b> and/or <i> tags may have no effect.

        Embedding and escaping special characters work only in English-font
        text; they have no effect in text created in Greek, Math, or
        User-defined character sets.

        You can produce subscripts or superscripts by enclosing any characters
        with <sub>...</sub> or <sup>...</sup>, respectively. |Tecplot 360| has
        only one level of superscripts and subscripts. Expressions requiring
        additional levels must be created by hand using multiple text objects.
        If you alternate subscripts and superscripts, |Tecplot 360| positions
        the superscript directly above the subscript. To produce consecutive
        superscripts, enclose all superscript characters in a single pair of
        tags.

        To insert a tag into text literally, precede the first angle bracket
        with a backslash ("\"). To insert a backslash in the text, just type
        two backslashes ("\\"). This example shows how to set the text string
        of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.text_string
            'abc'
            >>> text.text_string ='def'
            >>> text.text_string
            'def'
        """
        result, text_string = _tecutil.TextGetString(self.uid)
        if not result:
            raise TecplotSystemError
        return text_string

    @text_string.setter
    @annotation_preamble
    def text_string(self, text_string):
        with lock():
            _tecutil.TextSetString(self.uid, text_string)
