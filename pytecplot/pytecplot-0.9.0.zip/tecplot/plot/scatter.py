from builtins import super

from ..constant import *
from ..exception import *
from ..session import Style
from ..tecutil import color_spec, inherited_property, lock_attributes, sv, Index

class Scatter(Style):
    """Plot-local scatter style settings.

    This class controls the style of drawn scatter points on a specific plot.
    """
    def __init__(self, plot):
        self.plot = plot
        super().__init__(sv.GLOBALSCATTER, uniqueid=self.plot.frame.uid)

    @property
    def variable_index(self):
        """Zero-based index of the `Variable` used for size of scatter symbols.

        .. code-block:: python

            >>> plot.scatter.variable_index = dataset.variable('P').index
            >>> plot.fieldmap(0).scatter.size_by_variable = True

        The `Dataset` attached to this contour group's `Frame` is used, and
        the variable itself can be obtained through it::

            >>> scatter = plot.scatter
            >>> scatter_var = dataset.variable(scatter.variable_index)
            >>> scatter_var.index == scatter.variable_index
            True
        """
        return self._get_style(Index, sv.VAR)

    @variable_index.setter
    def variable_index(self, index):
        self._set_style(Index(index), sv.VAR)

    @property
    def variable(self):
        """The `Variable` to be used when sizing scatter symbols.

        The variable must belong to the `Dataset` attached to the `Frame`
        that holds this `ContourGroup`. Example usage::

            >>> plot.scatter.variable = dataset.variable('P')
            >>> plot.fieldmap(0).scatter.size_by_variable = True
        """
        return self.plot.frame.dataset.variable(self.variable_index)

    @variable.setter
    def variable(self, variable):
        self.variable_index = variable.index


@lock_attributes
class Symbol(object):
    def __init__(self, parent, svarg=sv.SYMBOLSHAPE):
        self.parent = parent
        self._sv = [svarg]

    def _get_style(self, rettype, *svargs):
        return self.parent._get_style(rettype, *(self._sv + list(svargs)))
    def _set_style(self, value, *svargs):
        self.parent._set_style(value, *(self._sv + list(svargs)))

    @property
    def _symbol_type(self):
        if self._get_style(bool, sv.ISASCII):
            return SymbolType.Text
        else:
            return SymbolType.Geometry

    @_symbol_type.setter
    def _symbol_type(self, value):
        value = SymbolType(value)
        if value is SymbolType.Text:
            self._set_style(True, sv.ISASCII)
        else:
            self._set_style(False, sv.ISASCII)


class TextSymbol(Symbol):
    """Text character for linemap symbols.

    Only a single character can be used.

    .. code-block:: python
        :emphasize-lines: 23,28

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, SymbolType, FillMode

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        plot.show_symbols = True

        cols = [Color.DeepRed, Color.Blue, Color.Fern]
        chars = ['S','D','M']

        for lmap,color,character in zip(plot.linemaps(), cols, chars):
            lmap.show = True
            lmap.line.color = color

            syms = lmap.symbols
            syms.show = True
            syms.symbol_type = SymbolType.Text
            syms.size = 2.5
            syms.color = Color.White
            syms.fill_mode = FillMode.UseSpecificColor
            syms.fill_color = color
            syms.symbol().text = character

        plot.view.fit()

        # save image to file
        tp.export.save_png('linemap_symbols_text.png', 600, supersample=3)

    .. figure:: /_static/images/linemap_symbols_text.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, parent, svarg=sv.SYMBOLSHAPE):
        super().__init__(parent, svarg)
        self._sv += [sv.ASCIISHAPE]

    @property
    def text(self):
        """The ASCII character to use as the symbol to show

        .. note:: This is limited to a single character.

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.symbol_type = SymbolType.Text
            >>> symbols.symbol().text = 'X'
        """
        return self._get_style(str, sv.ASCIICHAR)

    @text.setter
    def text(self, value):
        self._set_style(str(value)[0], sv.ASCIICHAR)

    @property
    def use_base_font(self):
        """Use the base typeface when rendering text-based symbols.

        :type: `boolean <bool>`

        When `False`, the ``font_override`` attribute takes effect::

            >>> from tecplot.constant import SymbolType, Font
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.symbol_type = SymbolType.Text
            >>> symbols.symbol().use_base_font = False
            >>> symbols.symbol().font_override = Font.Greek
        """
        return self._get_style(bool, sv.USEBASEFONT)

    @use_base_font.setter
    def use_base_font(self, value):
        self._set_style(bool(value), sv.USEBASEFONT)

    @property
    def font_override(self):
        """Typeface to use when rendering text-based symbols.

        :type: `constant.Font`

        Possible values: `constant.Font.Greek`, `constant.Font.Math` or `constant.Font.UserDefined`.

        The ``use_base_font`` attribute must be set to `False`::

            >>> from tecplot.constant import SymbolType, Font
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.symbol_type = SymbolType.Text
            >>> symbols.symbol().use_base_font = False
            >>> symbols.symbol().font_override = Font.Greek
        """
        return self._get_style(Font, sv.FONTOVERRIDE)

    @font_override.setter
    def font_override(self, value):
        if __debug__:
            valid_typefaces = [Font.Greek, Font.Math, Font.UserDefined]
            if value not in valid_typefaces:
                msg = 'font_override must be one of: '
                msg += ' '.join(str(x) for x in valid_typefaces)
                raise TecplotLogicError(msg)
        self._set_style(Font(value), sv.FONTOVERRIDE)


class TextScatterSymbol(TextSymbol):
    """Text character for scatter plots.

    Only a single character can be used.

    .. code-block:: python
        :emphasize-lines: 14,20-25

        from os import path
        import tecplot as tp
        from tecplot.constant import (Color, PlotType, PointsToPlot, SymbolType,
                                          GeomShape, FillMode)
        
        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(infile)
        
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()
        plot.show_shade = True
        plot.show_scatter = True
        
        for i,fmap in enumerate(plot.fieldmaps()):
            fmap.points.points_to_plot = PointsToPlot.SurfaceCellCenters
            fmap.points.step = (4,4)
        
            fmap.scatter.color = Color((i%4)+13)
            fmap.scatter.fill_mode = FillMode.UseSpecificColor
            fmap.scatter.fill_color = Color.Yellow
            fmap.scatter.size = 3
            fmap.scatter.symbol_type = SymbolType.Text
            fmap.scatter.symbol().text = hex(i)[-1]
            
            fmap.shade.color = Color.LightBlue
    

        tp.export.save_png('fieldmap_scatter_text.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_scatter_text.png
        :width: 300px
        :figwidth: 300px
    """

    @inherited_property(TextSymbol)
    def text(self):
        """The ASCII character to use as the symbol to show

        .. note:: This is limited to a single character.

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Text
            >>> scatter.symbol().text = 'X'
        """

    @inherited_property(TextSymbol)
    def use_base_font(self):
        """Use the base typeface when rendering text-based scatter.

        :type: `boolean <bool>`

        When `False`, the ``font_override`` attribute takes effect::

            >>> from tecplot.constant import SymbolType, Font
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Text
            >>> scatter.symbol().use_base_font = False
            >>> scatter.symbol().font_override = Font.Greek
        """

    @inherited_property(TextSymbol)
    def font_override(self):
        """Typeface to use when rendering text-based scatter.

        :type: `constant.Font`

        Possible values: `constant.Font.Greek`, `constant.Font.Math` or `constant.Font.UserDefined`.

        The ``use_base_font`` attribute must be set to `False`::

            >>> from tecplot.constant import SymbolType, Font
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Text
            >>> scatter.symbol().use_base_font = False
            >>> scatter.symbol().font_override = Font.Math
        """


class GeometrySymbol(Symbol):
    """Geometric shape for linemap symbols.

    .. code-block:: python
        :emphasize-lines: 28-29

        from os import path
        import tecplot as tp
        from tecplot.constant import (PlotType, Color, GeomShape, SymbolType,
                                      FillMode)

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        plot.show_symbols = True

        cols = [Color.DeepRed, Color.Blue, Color.Fern]
        shapes = [GeomShape.Square, GeomShape.Circle, GeomShape.Del]

        for lmap,color,shape in zip(plot.linemaps(), cols, shapes):
            lmap.show = True
            lmap.line.color = color

            symbols = lmap.symbols
            symbols.show = True
            symbols.size = 4.5
            symbols.color = color
            symbols.fill_mode = FillMode.UseSpecificColor
            symbols.fill_color = color
            symbols.symbol_type = SymbolType.Geometry
            symbols.symbol().shape = shape

        plot.view.fit()

        # save image to file
        tp.export.save_png('linemap_symbols_geometry.png', 600, supersample=3)

    .. figure:: /_static/images/linemap_symbols_geometry.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def shape(self):
        """Geometric shape to use when plotting linemap symbols.

        :type: `GeomShape`

        Possible values: `Square <GeomShape.Square>`, `Del`, `Grad`, `RTri`,
        `LTri`, `Diamond`, `Circle <GeomShape.Circle>`, `Cube`, `Sphere`,
        `Octahedron`, `Point <GeomShape.Point>`.

        Example usage::

            >>> from tecplot.constant import SymbolType, GeomShape
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.symbol_type = SymbolType.Geometry
            >>> symbols.symbol().shape = GeomShape.Diamond
        """
        return self._get_style(GeomShape, sv.GEOMSHAPE)

    @shape.setter
    def shape(self, value):
        self._set_style(GeomShape(value), sv.GEOMSHAPE)


class GeometryScatterSymbol(GeometrySymbol):
    """Geometric shape for scatter plots.

    .. code-block:: python
        :emphasize-lines: 13,21-28

        from os import path
        import tecplot as tp
        from tecplot.constant import (Color, PlotType, PointsToPlot, SymbolType,
                                      GeomShape, FillMode)

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()
        plot.show_scatter = True


        for i,fmap in enumerate(plot.fieldmaps()):
            points = fmap.points
            points.points_to_plot = PointsToPlot.SurfaceCellCenters
            points.step = (2,2)
        
            scatter = fmap.scatter
            scatter.color = Color(i)
            scatter.fill_mode = FillMode.UseSpecificColor
            scatter.fill_color = Color(i+plot.num_fieldmaps)
            scatter.size = 2
            scatter.line_thickness = 0.5
            scatter.symbol_type = SymbolType.Geometry
            scatter.symbol().shape = GeomShape(i%7)
        
        tp.export.save_png('fieldmap_scatter_geometry.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_scatter_geometry.png
        :width: 300px
        :figwidth: 300px
    """

    @inherited_property(GeometrySymbol)
    def shape(self):
        """Geometric shape to use when plotting scatter points.

        :type: `GeomShape`

        Possible values: `Square <GeomShape.Square>`, `Del`, `Grad`, `RTri`,
        `LTri`, `Diamond`, `Circle <GeomShape.Circle>`, `Cube`, `Sphere`,
        `Octahedron`, `Point <GeomShape.Point>`.

        Example usage::

            >>> from tecplot.constant import SymbolType, GeomShape
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Geometry
            >>> scatter.symbol().shape = GeomShape.Diamond
        """
