from builtins import int, super

from ..tecutil import (_tecutil, ArgList, Index, flatten_args, lock,
                       lock_attributes, sv)
from ..constant import *
from ..exception import *
from .. import legend, session, text


class ContourColormapOverride(session.Style):
    """Assigns contour bands to specific color.

    Specific contour bands can be assigned a unique basic color. This is useful
    for forcing a particular region to use blue, for example, to designate an
    area of water. You can define up to 16 color overrides.

    .. code-block:: python
        :emphasize-lines: 29,32-36

        from os import path
        import tecplot as tp
        from tecplot.constant import *

        # load the data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(datafile)

        # set plot type to 2D field plot
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()

        # show boundary faces and contours
        surfaces = plot.fieldmap(0).surfaces
        surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        # by default, contour 0 is the one that's shown,
        # set the contour's variable, colormap and number of levels
        contour = plot.contour(0)
        contour.variable = dataset.variable('T(K)')
        contour.colormap_name = 'Sequential - Yellow/Green/Blue'
        contour.levels.reset(9)

        # turn on colormap overrides for this contour
        contour_filter = contour.colormap_filter
        contour_filter.show_overrides = True

        # turn on override 0, coloring the first 4 levels red
        contour_override = contour_filter.override(0)
        contour_override.show = True
        contour_override.color = Color.Red
        contour_override.start_level = 7
        contour_override.end_level = 8

        # save image to file
        tp.export.save_png('contour_override.png', 600, supersample=3)


    .. figure:: /_static/images/contour_override.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, index, colormap_filter):
        self.index = Index(index)
        self.colormap_filter = colormap_filter
        super().__init__(colormap_filter._sv, sv.COLORMAPOVERRIDE,
                         **colormap_filter._style_attrs)

    @property
    def show(self):
        """Include this colormap override when filter is shown.

        :type: `boolean <bool>`

        Example usage::

            >>> colormap_filter = plot.contour(0).colormap_filter
            >>> cmap_override = colormap_filter.override(0)
            >>> cmap_override.show = True
        """
        return self._get_style(bool, sv.INCLUDE)

    @show.setter
    def show(self, show):
        self._set_style(bool(show), sv.INCLUDE)

    @property
    def color(self):
        """Color which will override the colormap.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> colormap_filter = plot.contour(0).colormap_filter
            >>> cmap_override = colormap_filter.override(0)
            >>> cmap_override.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self,value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def start_level(self):
        """First level to override.

        :type: `integer <int>`

        Example usage::

            >>> colormap_filter = plot.contour(0).colormap_filter
            >>> cmap_override = colormap_filter.override(0)
            >>> cmap_override.start_level = 2
        """
        return self._get_style(int, sv.STARTLEVEL)

    @start_level.setter
    def start_level(self,value):
        self._set_style(int(value), sv.STARTLEVEL)

    @property
    def end_level(self):
        """Last level to override.

        :type: `integer <int>`

        Example usage::

            >>> colormap_filter = plot.contour(0).colormap_filter
            >>> cmap_override = colormap_filter.override(0)
            >>> cmap_override.end_level = 2
        """
        return self._get_style(int, sv.ENDLEVEL)

    @end_level.setter
    def end_level(self,value):
        self._set_style(int(value), sv.ENDLEVEL)


class ContourColormapZebraShade(session.Style):
    """This filter sets a uniform color for every other band.

    Setting the color to `None` turns the bands off and makes them
    transparent::

        from os import path
        import numpy as np
        import tecplot as tp
        from tecplot.constant import Color, SurfacesToPlot

        # load the data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir,'SimpleData','Pyramid.plt')
        dataset = tp.data.load_tecplot(datafile)

        # show boundary faces and contours
        plot = tp.active_frame().plot()
        surfaces = plot.fieldmap(0).surfaces
        surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True
        plot.show_shade = False

        # set zebra filter on and make the zebra contours transparent
        cont0 = plot.contour(0)
        zebra = cont0.colormap_filter.zebra_shade
        zebra.show = True
        zebra.transparent = True

        tp.export.save_png('contour_zebra.png', 600, supersample=3)

    .. figure:: /_static/images/contour_zebra.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, colormap_filter):
        self.colormap_filter = colormap_filter
        super().__init__(colormap_filter._sv, sv.ZEBRA,
                         uniqueid=self.colormap_filter.contour.plot.frame.uid,
                         offset1=self.colormap_filter.contour.index)

    @property
    def show(self):
        """Show zebra shading in this `ContourGroup`.

        :type: `boolean <bool>`

        Example usage::

            >>> cmap_filter = plot.contour(0).colormap_filter
            >>> cmap_filter.zebra_shade.show = True
        """
        return self._get_style(bool, sv.INCLUDE)

    @show.setter
    def show(self,value):
        self._set_style(bool(value), sv.INCLUDE)

    @property
    def color(self):
        """Color of the zebra shading.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> filter = plot.contour(0).colormap_filter
            >>> zebra = filter.zebra_shade
            >>> zebra.show = True
            >>> zebra.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def transparent(self):
        """Set the the zebra bands to be transparent.

        :type: `boolean <bool>`

        Example usage::

            >>> filter = plot.contour(0).colormap_filter
            >>> zebra = filter.zebra_shade
            >>> zebra.show = True
            >>> zebra.transparent = True
        """
        return self._get_style(bool, sv.ISTRANSPARENT)

    @transparent.setter
    def transparent(self, value):
        self._set_style(bool(value), sv.ISTRANSPARENT)


class ContourGroupStyle(session.Style):
    def __init__(self, contour, *svargs):
        kw = dict(uniqueid=contour.plot.frame.uid, offset1=contour.index)
        super().__init__(contour._sv, *svargs, **kw)


class ContourColorCutoff(ContourGroupStyle):
    """Color-mapped value limits to display.

    This lets you specify a range within which contour flooding and
    multi-colored objects, such as scatter symbols, are displayed.

    .. code-block:: python
        :emphasize-lines: 17-22

        import os
        import tecplot as tp
        from tecplot.constant import PlotType, SurfacesToPlot

        # load the data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir,'SimpleData','Pyramid.plt')
        dataset = tp.data.load_tecplot(datafile)

        # show boundary faces and contours
        plot = tp.active_frame().plot()
        surfaces = plot.fieldmap(0).surfaces
        surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        # cutoff contour flooding outside min/max range
        cutoff = plot.contour(0).color_cutoff
        cutoff.include_min = True
        cutoff.min = 0.5
        cutoff.include_max = True
        cutoff.max = 1.0
        cutoff.inverted = True

        tp.export.save_png('contour_color_cutoff.png',600)

    .. figure:: /_static/images/contour_color_cutoff.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, contour):
        self.contour = contour
        super().__init__(contour, sv.COLORCUTOFF)

    @property
    def include_min(self):
        """Use the minimum cutoff value.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.contour(0).color_cutoff.include_min = True
            >>> plot.contour(0).color_cutoff.min = 3.14
        """
        return self._get_style(bool, sv.INCLUDEMIN)

    @include_min.setter
    def include_min(self, value):
        self._set_style(bool(value), sv.INCLUDEMIN)

    @property
    def include_max(self):
        """Use the maximum cutoff value.

        :type: `boolean <bool>`

        Thie example turns off the maximum cutoff::

            >>> plot.contour(0).color_cutoff.include_max = False
        """
        return self._get_style(bool, sv.INCLUDEMAX)

    @include_max.setter
    def include_max(self, value):
        self._set_style(bool(value), sv.INCLUDEMAX)

    @property
    def min(self):
        """The minimum cutoff value.

        :type: `float` or `None`

        The ``include_min`` must be set to `True`::

            >>> plot.contour(0).color_cutoff.include_min = True
            >>> plot.contour(0).color_cutoff.min = 3.14
        """
        return self._get_style(float, sv.RANGEMIN)

    @min.setter
    def min(self,value):
        self._set_style(float(value), sv.RANGEMIN)

    @property
    def max(self):
        """The maximum cutoff value.

        :type: `float` or `None`

        The ``include_max`` must be set to `True`::

            >>> plot.contour(0).color_cutoff.include_max = True
            >>> plot.contour(0).color_cutoff.max = None
        """
        return self._get_style(float, sv.RANGEMAX)

    @max.setter
    def max(self,value):
        self._set_style(float(value), sv.RANGEMAX)

    @property
    def inverted(self):
        """Cuts values outside the range instead of inside.

        :type: `bool`

        .. code-block:: python

            >>> plot.contour(0).color_cutoff.inverted = True
        """
        return self._get_style(bool, sv.INVERTCUTOFF)

    @inverted.setter
    def inverted(self,value):
        self._set_style(bool(value), sv.INVERTCUTOFF)


class ContourColormapFilter(ContourGroupStyle):
    """Controls how the colormap is rendered for a given contour.

    .. code-block:: python
        :emphasize-lines: 27-31

        from os import path
        import tecplot as tp
        from tecplot.constant import *

        # load the data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir,'SimpleData','HeatExchanger.plt')
        ds = tp.data.load_tecplot(datafile)

        # set plot type to 2D field plot
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()

        # show boundary faces and contours
        surfaces = plot.fieldmap(0).surfaces
        surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        # by default, contour 0 is the one that's shown,
        # set the contour's variable, colormap and number of levels
        contour = plot.contour(0)
        contour.variable = ds.variable('P(N)')

        # cycle through the colormap three times and reversed
        # show a faithful (non-approximate) continuous distribution
        contour_filter = contour.colormap_filter
        contour_filter.num_cycles = 3
        contour_filter.reversed = True
        contour_filter.fast_continuous_flood = False
        contour_filter.distribution = ColorMapDistribution.Continuous

        # save image to file
        tp.export.save_png('contour_filtered.png', 600, supersample=3)

    .. figure:: /_static/images/contour_filtered.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, contour):
        self.contour = contour
        super().__init__(self.contour, sv.COLORMAPFILTER)

    def override(self, index):
        """Returns a `ContourColormapOverride` object by index.

        Parameters:
            index (`int`): The index of the colormap override object.

        Returns:
            `ContourColormapOverride`: The class controlling the specific
            contour colormap override requested by index.

        Example::

            >>> cmap_override = plot.contour(0).colormap_filter.override(0)
            >>> cmap_override.show = True
        """
        return ContourColormapOverride(index, self)

    @property
    def zebra_shade(self):
        """Returns a `ContourColormapZebraShade` filtering object.

        :type: `ContourColormapZebraShade`

        Example usage::

            >>> zebra = plot.contour(0).colormap_filter.zebra_shade
            >>> zebra.show = True
        """
        return ContourColormapZebraShade(self)

    @property
    def show_overrides(self):
        """Enable the colormap overrides in this contour group.

        :type: `boolean <bool>`

        The overrides themselves must be turned on as well for this
        to have an effect on the resulting plot::

            >>> contour = plot.contour(0)
            >>> cmap_filter = contour.colormap_filter
            >>> cmap_filter.show_overrides = True
            >>> cmap_filter.override(0).show = True
        """
        return self._get_style(bool, sv.COLORMAPOVERRIDEACTIVE)

    @show_overrides.setter
    def show_overrides(self, show):
        self._set_style(bool(show), sv.COLORMAPOVERRIDEACTIVE)

    @property
    def num_cycles(self):
        """Number of cycles to repeat the colormap.

        :type: `integer <int>`

        >>> plot.contour(0).colormap_filter.num_cycles = 3
        """
        return self._get_style(int, sv.COLORMAPCYCLES)

    @num_cycles.setter
    def num_cycles(self,value):
        self._set_style(int(value), sv.COLORMAPCYCLES)

    @property
    def distribution(self):
        """Rendering style of the colormap.

        :type: `ColorMapDistribution`

        Possible values:

        `Banded`
            A solid color is assigned for all values within the band between
            two levels.

        `Continuous`
            The color distribution assigns linearly varying colors to all
            multi-colored objects or contour flooded regions.

        Example::

            >>> from tecplot.constant import ColorMapDistribution
            >>> cmap_filter = plot.contour(0).colormap_filter
            >>> cmap_filter.distribution = ColorMapDistribution.Banded
        """
        return self._get_style(ColorMapDistribution, sv.COLORMAPDISTRIBUTION)

    @distribution.setter
    def distribution(self,value):
        self._set_style(ColorMapDistribution(value), sv.COLORMAPDISTRIBUTION)

    @property
    def reversed(self):
        """Reverse the colormap.

        :type: `bool`

        >>> plot.contour(0).colormap_filter.reversed = True
        """
        return self._get_style(bool, sv.REVERSECOLORMAP)

    @reversed.setter
    def reversed(self,value):
        self._set_style(bool(value), sv.REVERSECOLORMAP)

    @property
    def fast_continuous_flood(self):
        """Use a fast approximation to continuously flood the colormap.

        :type: `bool`

        Causes each cell to be flooded using interpolation between the color
        values at each node. When the transition from a color at one node to
        another node crosses over the boundary between control points in the
        color spectrum, fast flooding may produce colors not in the spectrum.
        Setting this to `False` is slower, but more accurate::

            >>> cmap_filter = plot.contour(0).colormap_filter
            >>> cmap_filter.fast_continuous_flood = True
        """
        return self._get_style(bool, sv.USEFASTAPPROXCONTINUOUSFLOOD)

    @fast_continuous_flood.setter
    def fast_continuous_flood(self,value):
        self._set_style(bool(value), sv.USEFASTAPPROXCONTINUOUSFLOOD)

    @property
    def continuous_min(self):
        """Lower limit for continuous colormap flooding.

        :type: `float`

        Example usage::

            >>> from tecplot.constant import ColorMapDistribution
            >>> cmap_filter = plot.contour(0).colormap_filter
            >>> cmap_filter.distribution = ColorMapDistribution.Continuous
            >>> cmap_filter.continuous_min = 3.1415
        """
        return self._get_style(float, sv.CONTINUOUSCOLOR, sv.CMIN)

    @continuous_min.setter
    def continuous_min(self, value):
        self._set_style(float(value), sv.CONTINUOUSCOLOR, sv.CMIN)

    @property
    def continuous_max(self):
        """Upper limit for continuous colormap flooding.

        :type: `float`

        Example set the limits to the (min, max) of a variable in a specific
        zone::

            >>> from tecplot.constant import ColorMapDistribution
            >>> cmap_filter = plot.contour(0).colormap_filter
            >>> cmap_filter.distribution = ColorMapDistribution.Continuous
            >>> pressure = dataset.variable('Pressure').values('My Zone')
            >>> cmap_filter.continuous_min = pressure.min()
            >>> cmap_filter.continuous_max = pressure.max()
        """
        return self._get_style(float, sv.CONTINUOUSCOLOR, sv.CMAX)

    @continuous_max.setter
    def continuous_max(self, value):
        self._set_style(float(value), sv.CONTINUOUSCOLOR, sv.CMAX)


class ContourLabels(ContourGroupStyle):
    """Contour line label style, position and alignment control.

    These are labels that identify particular contour levels either by value or
    optionally, by number starting from one. The plot type must be lines or
    lines and flood in order to see them:

    .. code-block:: python
        :emphasize-lines: 19-24

        from os import path
        import tecplot as tp
        from tecplot.constant import Color, ContourType, SurfacesToPlot

        # load the data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir,'SimpleData','Pyramid.plt')
        dataset = tp.data.load_tecplot(datafile)

        # show boundary faces and contours
        plot = tp.active_frame().plot()
        plot.fieldmap(0).contour.contour_type = ContourType.Lines
        surfaces = plot.fieldmap(0).surfaces
        surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        # set contour label style
        contour_labels = plot.contour(0).labels
        contour_labels.show = True
        contour_labels.auto_align = False
        contour_labels.color = Color.Blue
        contour_labels.background_color = Color.White
        contour_labels.margin = 20

        tp.export.save_png('contour_labels.png', 600, supersample=3)

    .. figure:: /_static/images/contour_labels.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, contour):
        self.contour = contour
        super().__init__(self.contour, sv.LABELS)

    @property
    def show(self):
        """Show the contour line labels.

        :type: `bool`

        Contour lines must be on for this to have any effect::

            >>> from tecplot.constant import ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self,value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def auto_align(self):
        """Automatically align the labels with the contour lines.

        :type: `bool`

        This causes the flow of the text to be aligned with the contour lines.
        Otherwise, the labels are aligned with the frame::

            >>> from tecplot.constant import ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.auto_align = False
        """
        return self._get_style(bool, sv.ALIGNAUTOLABELS)

    @auto_align.setter
    def auto_align(self,value):
        self._set_style(bool(value), sv.ALIGNAUTOLABELS)

    @property
    def spacing(self):
        """Spacing between labels along the contour lines.

        :type: `float`

        This is the distance between each label along each contour line
        in percentage of the frame height::

            >>> from tecplot.constant import ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.spacing = 20
        """
        return self._get_style(float, sv.AUTOLABELSPACING)

    @spacing.setter
    def spacing(self,value):
        self._set_style(float(value), sv.AUTOLABELSPACING)

    @property
    def step(self):
        """Number of contour lines from one label to the next.

        :type: `int`

        This is the number of contour bands between lines that are to be
        labeled::

            >>> from tecplot.constant import ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.step = 4
        """
        return self._get_style(int, sv.AUTOLEVELSKIP)

    @step.setter
    def step(self,value):
        self._set_style(int(value), sv.AUTOLEVELSKIP)

    @property
    def font(self):
        """`text.Font` used to show the labels.

        :type: `text.Font`

        Example::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.font.size = 3.5
        """
        return text.Font(self)

    @property
    def color(self):
        """Text color of the labels.

        :type: `Color`

        Example::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.color Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self,value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def filled(self):
        """Fill the background area behind the text labels.

        :type: `boolean <bool>`

        The background can be filled with a color or disabled (made
        transparent) by setting this property to `False`::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.filled = True
            >>> plot.contour(0).labels.background_color = Color.Blue
            >>> plot.contour(1).labels.show = True
            >>> plot.contour(1).labels.filled = False
        """
        return self._get_style(bool, sv.ISFILLED)

    @filled.setter
    def filled(self, value):
        self._set_style(bool(value), sv.ISFILLED)

    @property
    def background_color(self):
        """Background fill color behind the text labels.

        :type: `Color`

        The ``filled`` attribute must be set to `True`::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.background_color = Color.Blue
        """
        return self._get_style(Color, sv.FILLCOLOR)
    @background_color.setter
    def background_color(self,value):
        self._set_style(Color(value), sv.FILLCOLOR)

    @property
    def auto_generate(self):
        """Automatically generate labels along contour lines.

        :type: `bool`

        This causes a new set of contour labels to be created at each redraw::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.auto_generate = True
        """
        return self._get_style(bool, sv.GENERATEAUTOLABELS)

    @auto_generate.setter
    def auto_generate(self,value):
        self._set_style(bool(value), sv.GENERATEAUTOLABELS)

    @property
    def label_by_level(self):
        """Use the contour numbers as the label instead of the data value.

        :type: `bool`

        Contour level numbers start from one when drawn. Example usage::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.label_by_level = True
        """
        return not self._get_style(bool, sv.LABELWITHVALUE)

    @label_by_level.setter
    def label_by_level(self,value):
        self._set_style(not bool(value), sv.LABELWITHVALUE)

    @property
    def margin(self):
        """Spacing around the text and the filled background area.

        :type: `float` in percentage of the text height.

        Contour numbers start from one when drawn. Example usage::

            >>> from tecplot.constant import Color, ContourType
            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
            >>> plot.contour(0).labels.background_color = Color.Yellow
            >>> plot.contour(0).labels.margin = 20
        """
        return self._get_style(float, sv.MARGIN)

    @margin.setter
    def margin(self,value):
        self._set_style(float(value), sv.MARGIN)

    @property
    def format(self):
        """Number formatting for contour labels.

        :type: `LabelFormat`

        Example usage::

            >>> from tecplot.constant import NumberFormat
            >>> contour = plot.contour(0)
            >>> contour.labels.format.format_type = NumberFormat.Integer
        """
        return text.LabelFormat(self)


@lock_attributes
class ContourLevels(object):
    """List of contour level values.

    A contour level is a value at which contour lines are drawn, or for banded
    contour flooding, the border between different colors of flooding.
    Initially, each contour group consists of approximately 10 levels evenly
    spaced over the *z* coordinate in the `Frame`'s `Dataset`. These values can
    be manipulated with the `ContourLevels` object obtained via the
    `ContourGroup.levels` attribute.

    .. code-block:: python
        :emphasize-lines: 11-12

        from os import path
        import numpy as np
        import tecplot as tp

        # load layout
        examples_dir = tp.session.tecplot_examples_directory()
        example_layout = path.join(examples_dir,'SimpleData','3ElementWing.lpk')
        tp.load_layout(example_layout)
        frame = tp.active_frame()

        levels = frame.plot().contour(0).levels
        levels.reset_levels(np.linspace(55000,115000,61))

        # save image to file
        tp.export.save_png('contour_adjusted_levels.png', 600, supersample=3)

    .. figure:: /_static/images/contour_adjusted_levels.png
        :width: 300px
        :figwidth: 300px

    .. note::

        The streamtraces in the plot above is a side-effect of settings in
        layout file used. For more information about streamtraces, see the
        `plot.Streamtraces` class reference.
    """
    def __init__(self, contour):
        self.contour = contour

    @lock()
    def _ContourLevelX(self, arglist):
        arglist[sv.CONTOURGROUP] = self.contour.index+1
        with self.contour.plot.frame.activated():
            _tecutil.ContourLevelX(arglist)

    def _data(self):
        with self.contour.plot.frame.activated():
            success,n,values = _tecutil.ContourGetLevels(self.contour.index+1)
            if not success:
                raise TecplotLogicError('Could not query contour levels.')
            return [values[i] for i in range(n)]

    def __len__(self):
        return len(self._data())

    def __iter__(self):
        for i in self._data():
            yield i

    def __getitem__(self,i):
        return self._data()[i]

    def add(self, *values):
        """Adds new levels to the existing list.

        Parameters:
            *values (`floats <float>`): The level values to be added to the
                `ContourGroup`.

        The values added are inserted into the list of levels in ascending
        order::

            >>> levels = plot.contour(0).levels
            >>> list(levels)
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
            >>> levels.add(3.14159)
            >>> list(levels)
            [0.0, 1.0, 2.0, 3.0, 3.14159, 4.0, 5.0]
        """
        values = flatten_args(*values)
        with ArgList() as arglist:
            arglist[sv.CONTOURLEVELACTION] = ContourLevelAction.Add
            arglist[sv.NUMVALUES] = len(values)
            arglist[sv.RAWDATA] = map(float, values)
            self._ContourLevelX(arglist)

    def reset(self, num_levels=15):
        """Resets the levels to the number specified.

        Parameters:
            num_levels (`integer <int>`): Number of levels. (default: 10)

        This will reset the contour levels to a set of evenly
        distributed values spanning the entire range of the currently
        selected contouring variable::

            >>> plot.contour(0).levels.reset(30)
        """
        with ArgList() as arglist:
            arglist[sv.CONTOURLEVELACTION] = ContourLevelAction.Reset
            arglist[sv.NUMVALUES] = int(num_levels)
            self._ContourLevelX(arglist)

    def reset_levels(self, *values):
        """Resets the levels to the values specified.

        Parameters:
            *values (`floats <float>`): The level values to be added to the
                `ContourGroup`.

        This method replaces the current set of contour levels with a new set.
        Here, we set the levels to go from 0 to 100 in steps of 5::

            >>> plot.contour(0).levels.reset_levels(*range(0,101,5))
        """
        values = flatten_args(*values)
        with ArgList() as arglist:
            arglist[sv.CONTOURLEVELACTION] = ContourLevelAction.New
            arglist[sv.NUMVALUES] = len(values)
            arglist[sv.RAWDATA] = map(float, values)
            self._ContourLevelX(arglist)

    def reset_to_nice(self, num_levels=15):
        """Approximately resets the levels to the number specified.

        Parameters:
            num_levels (`integer <int>`): Approximate number of levels to
                create. (default: 10)

        This will reset the contour levels to a set of evenly distributed
        values that approximately spans the range of the currently selected
        contouring variable. Exact range and number of levels will be
        adjusted to make the contour levels have "nice" values::

            >>> plot.contour(0).levels.reset_to_nice(50)
        """
        with ArgList() as arglist:
            arglist[sv.CONTOURLEVELACTION] = ContourLevelAction.ResetToNice
            arglist[sv.APPROXNUMVALUES] = int(num_levels)
            self._ContourLevelX(arglist)

    def delete_range(self, min_value, max_value):
        """Inclusively, deletes all levels within a specified range.

        Parameters:
            min_value (`float`): Minimum value to remove.
            max_value (`float`): Maximum value to remove.

        This method deletes all contour levels between the specified minimum
        and maximum values of the contour variable (inclusive)::

            >>> plot.contour(0).levels.delete_range(0.5, 1.5)
        """
        with ArgList() as arglist:
            arglist[sv.CONTOURLEVELACTION] = ContourLevelAction.DeleteRange
            arglist[sv.RANGEMIN] = float(min_value)
            arglist[sv.RANGEMAX] = float(max_value)
            self._ContourLevelX(arglist)

    def delete_nearest(self, value):
        """Removes the level closest to the specified value.

        Parameters:
            value (`float`): Value of the level to remove.

        This method deletes the contour level with the value nearest the
        supplied value::

            >>> plot.contour(0).levels.delete_nearest(3.14)
        """
        with ArgList() as arglist:
            arglist[sv.CONTOURLEVELACTION] = ContourLevelAction.DeleteNearest
            arglist[sv.RANGEMIN] = float(value)
            self._ContourLevelX(arglist)


class ContourLines(ContourGroupStyle):
    """Contour line style.

    This object sets the style of the contour lines once turned on.

    .. code-block:: python
        :emphasize-lines: 19-22

        from os import path
        import tecplot as tp
        from tecplot.constant import (ContourLineMode, ContourType,
                                      SurfacesToPlot)

        # load the data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir,'SimpleData','Pyramid.plt')
        dataset = tp.data.load_tecplot(datafile)

        # show boundary faces and contours
        plot = tp.active_frame().plot()
        plot.fieldmap(0).contour.contour_type = ContourType.Lines
        surfaces = plot.fieldmap(0).surfaces
        surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        # set contour line style
        contour_lines = plot.contour(0).lines
        contour_lines.mode = ContourLineMode.SkipToSolid
        contour_lines.step = 4
        contour_lines.pattern_length = 2

        tp.export.save_png('contour_lines.png', 600, supersample=3)

    .. figure:: /_static/images/contour_lines.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, contour):
        self.contour = contour
        super().__init__(self.contour, sv.CONTOURLINESTYLE)

    @property
    def mode(self):
        """Type of lines to draw on the plot (`ContourLineMode`).

        :type: `ContourLineMode`

        Possible values:

            `UseZoneLineType`
                For each zone, draw the contour lines using the line pattern
                and pattern length specified in the `FieldmapContour` for the
                parent `Fieldmap`. If you are adding contour lines to
                polyhedral zones, the patterns will not be continuous from one
                cell to the next and the pattern will restart at every cell
                boundary.
            `SkipToSolid`
                Draw dashed lines between each pair of solid lines which are
                spaced out by the `ContourLines.step` property. This will
                override any line pattern or thickness setting in the parent
                `Fieldmap`'s `FieldmapContour` object.
            `DashNegative`
                Draw lines of positive contour variable value as solid lines
                and lines of negative contour variable value as dashed lines.
                This will override any line pattern or thickness setting in the
                parent `Fieldmap`'s `FieldmapContour` object.

        Example::

            >>> from tecplot.constant import ContourLineMode
            >>> lines = plot.contour(0).lines
            >>> lines.mode = ContourLineMode.DashNegative
        """
        return self._get_style(ContourLineMode, sv.CONTOURLINEMODE)

    @mode.setter
    def mode(self,value):
        self._set_style(ContourLineMode(value), sv.CONTOURLINEMODE)

    @property
    def step(self):
        """Number of lines to step for `SkipToSolid` line mode (`int`).

        :type: `int`

        Example::

            >>> from tecplot.constant import ContourLineMode
            >>> lines = plot.contour(0).lines
            >>> lines.mode = ContourLineMode.SkipToSolid
            >>> lines.step = 5
        """
        return self._get_style(int, sv.LINESKIP)

    @step.setter
    def step(self,value):
        self._set_style(int(value), sv.LINESKIP)

    @property
    def pattern_length(self):
        """Length of dashed lines and space between dashes (`float`).

        :type: `float`

        The length is in percentage of the frame height::

            >>> from tecplot.constant import ContourLineMode
            >>> lines = plot.contour(0).lines
            >>> lines.mode = ContourLineMode.SkipToSolid
            >>> lines.step = 5
            >>> lines.pattern_length = 5
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self,value):
        self._set_style(float(value), sv.PATTERNLENGTH)


class ContourGroup(session.Style):
    """Contouring of a variable using a colormap.

    This object controls the style for a specific contour group within
    a `Frame`. Contour levels, colormap and contour lines are accessed
    through this class.

    .. code-block:: python
        :emphasize-lines: 10,12-14

        from os import path
        import tecplot as tp
        from tecplot.constant import *

        # load data
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir,'SimpleData','CircularContour.plt')
        dataset = tp.data.load_tecplot(datafile)
        plot = dataset.frame.plot()
        plot.show_contour = True

        contour = plot.contour(0)
        contour.variable = dataset.variable('Mix')
        contour.colormap_name = 'Magma'

        # save image to file
        tp.export.save_png('contour_magma.png', 600, supersample=3)

    .. figure:: /_static/images/contour_magma.png
        :width: 300px
        :figwidth: 300px

    There are a fixed number of contour groups available for each plot. Others
    can be enabled and modified by specifying an index other than zero::

        >>> contour3 = plot.contour(3)
        >>> contour3.variable = dataset.variable('U')
    """
    def __init__(self, index, plot):
        if __debug__:
            assert 0 <= index < 8, 'Contour index out of range (must be < 8)'
        self.index = Index(index)
        self.plot = plot
        super().__init__(sv.GLOBALCONTOUR, uniqueid=self.plot.frame.uid,
                         offset1=self.index)

    def __eq__(self, obj):
        return (self.index == obj.index) and (self.plot == obj.plot)

    @property
    def variable_index(self):
        """Zero-based index of the `Variable` being contoured.

        .. code-block:: python

            >>> plot.contour(0).variable_index = dataset.variable('P').index

        The `Dataset` attached to this contour group's `Frame` is used::

            >>> contour = plot.contour(0)
            >>> contour_var = frame.dataset.variable(contour.variable_index)
            >>> contour_var.index == contour.variable_index
            True
        """
        return self._get_style(Index, sv.VAR)

    @variable_index.setter
    def variable_index(self, index):
        # Use the TecUtil X function to set the variable.
        # By using the X function to set the contour variable, we can set
        # the initialization mode to 'NiceResetLevels",
        # which is the GUI default.
        with lock():
            with ArgList() as arglist:
                arglist[sv.VAR] = index + 1
                arglist[sv.CONTOURGROUP] = self.index + 1
                arglist[sv.LEVELINITMODE] = ContourLevelsInitializationMode.NiceResetLevels
                if not _tecutil.ContourSetVariableX(arglist):
                    raise TecplotSystemError()

    @property
    def variable(self):
        """The `Variable` being contoured.

        The variable must belong to the `Dataset` attached to the `Frame`
        that holds this `ContourGroup`. Example usage::

            >>> plot.contour(0).variable = dataset.variable('P')
        """
        return self.plot.frame.dataset.variable(self.variable_index)

    @variable.setter
    def variable(self, variable):
        if __debug__:
            if variable not in self.plot.frame.dataset:
                raise TecplotLogicError('Variable not in dataset.')
        self.variable_index = variable.index

    @property
    def color_cutoff(self):
        """`ContourColorCutoff` object controlling color cutoff min/max.

        :type: `ContourColorCutoff`

        >>> cutoff = plot.contour(0).color_cutoff
        >>> cutoff.min = 3.14
        """
        return ContourColorCutoff(self)

    @property
    def colormap_filter(self):
        """`ContourColormapFilter` object controlling colormap style properties.

        :type: `ContourColormapFilter`

        >>> plot.contour(0).colormap_filter.reverse = True
        """
        return ContourColormapFilter(self)

    @property
    def labels(self):
        """`ContourLabels` object controlling contour line labels.

        :type: `ContourLabels`

        Lines must be turned on through the associated fieldmap object
        for style changes to be meaningful::

            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).labels.show = True
        """
        return ContourLabels(self)

    @property
    def legend(self):
        """`ContourLegend` associated with this `ContourGroup`.

        :type: `ContourLegend`

        This object controls the attributes of the contour legend associated
        with this `ContourGroup`.

        Example usage::

            >>> plot.contour(0).legend.show = True
        """
        return legend.ContourLegend(self)

    @property
    def levels(self):
        """`ContourLevels` holding the list of contour levels.

        :type: `ContourLevels`

        This object controls the values of the contour levels. Values can
        be added, deleted or overridden completely::

            >>> plot.contour(0).levels.reset_to_nice(15)
        """
        return ContourLevels(self)

    @property
    def lines(self):
        """`ContourLines` object controlling contour line style.

        :type: `ContourLines`

        Lines must be turned on through the associated fieldmap object
        for style changes to be meaningful::

            >>> plot.fieldmap(0).contour.contour_type = ContourType.Lines
            >>> plot.contour(0).lines.mode = ContourLineMode.DashNegative
        """
        return ContourLines(self)

    @property
    def default_num_levels(self):
        """Default target number (`int`) of levels used when resetting.

        :type: `integer <int>`

        Example::

            >>> plot.contour(0).default_num_levels = 20
        """
        return self._get_style(int, sv.DEFNUMLEVELS)

    @default_num_levels.setter
    def default_num_levels(self, value):
        self._set_style(int(value), sv.DEFNUMLEVELS)

    @property
    def colormap_name(self):
        """The name of the colormap (`str`) to be used.

        :type: `string <str>`

        Example::

            >>> plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
        """
        return self._get_style(str, sv.COLORMAPNAME)

    @colormap_name.setter
    def colormap_name(self,value):
        self._set_style(str(value), sv.COLORMAPNAME)
