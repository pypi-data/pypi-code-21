from builtins import super, int

import ctypes

from collections import namedtuple
from textwrap import dedent

from ..tecutil import (_tecutil, Index, IndexRange, IndexSet, color_spec,
                       flatten_args, sv)
from ..constant import *
from ..exception import *
from .. import session
from .scatter import GeometrySymbol, TextSymbol, Symbol


class LinemapStyle(session.Style):
    def __init__(self, linemap, *svargs):
        kw = dict(uniqueid=linemap.plot.frame.uid, offset1=linemap.index,
                  multiset=True)
        super().__init__(linemap._sv, *svargs, **kw)

    def __eq__(self, that):
        return isinstance(that, type(self)) and (self.linemap == that.linemap)

    def __ne__(self, that):
        return not (self == that)


class LinemapBars(LinemapStyle):
    """Bar chart style control.

    A bar chart is an XY Line plot that uses vertical or horizontal bars placed
    along an axis to represent data points. Changing the function dependency of
    the linemap with `XYLinemap.function_dependency` controls the direction of
    the bars. By default, all mappings use :math:`y = f(x)` and appear as
    vertical bar charts. Setting *y* to be the independent variable will cause
    the bars to be horizontal.

    .. code-block:: python
        :emphasize-lines: 12,16-21

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        plot.show_bars = True

        lmap = plot.linemap(0)

        bars = lmap.bars
        bars.show = True
        bars.size = 0.6*(100 / dataset.zone(0).num_points)
        bars.fill_color = Color.Red
        bars.line_color = Color.Red
        bars.line_thickness = 0.01

        tp.export.save_png('linemap_bars.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap_bars.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, linemap):
        self.linemap = linemap
        super().__init__(linemap, sv.BARCHARTS)

    @property
    def show(self):
        """Display bars on the plot for this :ref:`Linemap`.

        :type: `bool`

        The parent plot object must have bars enabled as well::

            >>> plot.show_bars = True
            >>> plot.linemap(0).bars.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def size(self):
        """Width of the bars.

        :type: `float` (percentange of `Frame` width)

        Example usage::

            >>> plot.linemap(0).bars.size = 0.10
        """
        return self._get_style(float, sv.SIZE)

    @size.setter
    def size(self, value):
        self._set_style(float(value), sv.SIZE)

    @property
    def fill_mode(self):
        """fill mode for the bars.

        :type: `FillMode`

        Possible values: `FillMode.UseSpecificColor`, `FillMode.UseLineColor`,
            `FillMode.UseBackgroundColor` or `FillMode.None_`.

        Example usage::

            >>> from tecplot.constant import FillMode
            >>> bars = plot.linemap(0).bars
            >>> bars.fill_mode = FillMode.UseBackgroundColor
        """
        return self._get_style(FillMode, sv.FILLMODE)

    @fill_mode.setter
    def fill_mode(self, value):
        self._set_style(FillMode(value), sv.FILLMODE)

    @property
    def fill_color(self):
        """Fill color of the bars.

        :type: `Color` or `ContourGroup`.

        The ``fill_mode`` attribute must be set to
        `FillMode.UseSpecificColor`::

            >>> from tecplot.constant import Color, FillMode
            >>> bars = plot.linemap(0).bars
            >>> bars.fill_mode = FillMode.UseSpecificColor
            >>> bars.fill_color = Color.Red
        """
        return color_spec(self._get_style(Color, sv.FILLCOLOR),
                          self.linemap.plot)

    @fill_color.setter
    def fill_color(self, value):
        self._set_style(color_spec(value), sv.FILLCOLOR)

    @property
    def line_color(self):
        """Edge line color of the bars.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.linemap(0).bars.line_color = Color.Red
        """
        return self._get_style(Color, sv.COLOR)

    @line_color.setter
    def line_color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Edge line thickness of the bars.

        :type: `float`

        Example usage::

            >>> plot.linemap(0).bars.line_thickness = 0.1
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class LinemapCurve(LinemapStyle):
    """Curve-fitting of the line.

    This class controls how the line is to be drawn between data points. By
    default, the `CurveType.LineSeg` option is used and straight lines are
    used. Setting `curve_type` to a fit type or spline type will replace the
    line segments with a smooth curve:

    .. code-block:: python
        :emphasize-lines: 33-47

        import numpy as np
        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, CurveType

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)
        dataset.add_variable('Weight')

        # convert error to weighting to be used for fitting below
        # This converts the error to  (1 / error)
        # and normalizes to the range [1,100]
        zone = dataset.zone('ZONE 1')
        err1 = zone.values('Error 1')
        wvar = zone.values('Weight')
        err = err1.as_numpy_array()
        sigma = 1. / err
        dsigma = sigma.max() - sigma.min()
        sigma = (99 * (sigma - sigma.min()) / dsigma) + 1
        wvar[:] = sigma

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()

        xvar = dataset.variable(0)
        for lmap,var in zip(plot.linemaps(),list(dataset.variables())[1:4]):
            lmap.x_variable = xvar
            lmap.y_variable = var
            lmap.show = True

        curves = [lmap.curve for lmap in plot.linemaps()]

        curves[0].curve_type = CurveType.PolynomialFit
        curves[0].num_points = 1000
        curves[0].polynomial_order = 10

        curves[1].curve_type = CurveType.PowerFit
        curves[1].use_fit_range = True
        curves[1].fit_range = 4,8
        curves[1].weight_variable = dataset.variable('Weight')
        curves[1].use_weight_variable = True

        curves[2].curve_type = CurveType.Spline
        curves[2].clamp_spline = True
        curves[2].spline_derivative_at_ends = 0,0

        tp.export.save_png('linemap_curve.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap_curve.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, linemap):
        self.linemap = linemap
        super().__init__(linemap, sv.CURVES)

    _Limits = namedtuple('Limits', ['min', 'max'])
    _Limits.__new__.__defaults__ = (None, None)

    _Derivatives = namedtuple('Derivatives', ['start', 'end'])
    _Derivatives.__new__.__defaults__ = (None, None)

    @property
    def curve_type(self):
        """Type of curve to draw or fit.

        :type: `CurveType`

        Possible values: `LineSeg`, `PolynomialFit`, `EToRFit`, `PowerFit`,
        `Spline`, `ParaSpline`.

        `CurveType.LineSeg` (line segment, no curve-fit)
            A series of linear segments connect adjacent data points. In XY
            Line plots, these will be line segments.
        `CurveType.PolynomialFit`
            A polynomial of order `LinemapCurve.polynomial_order` is fit to the
            data points where :math:`1 <= N <= 10`. :math:`N = 1` is a
            straight-line fit.
        `CurveType.EToRFit` (exponential curve-fit)
            An exponential curve-fit that finds the best curve of the form
            :math:`Y = e^{b\cdot X+c}` which is equivalent to :math:`Y = a\cdot
            e^{b\cdot X}`, where :math:`a = e^c`. To use this curve type,
            *Y*-values for this variable must be all positive or all negative.
            If the function dependency is set to :math:`X = f(Y)` all
            *X*-values must be all positive or all negative.
        `CurveType.PowerFit`
            A power curve fit that finds the best curve of the form :math:`Y =
            e^{b \cdot \ln X + c}` which is equivalent to :math:`Y = a\cdot X^b`
            , where :math:`a = e^c`. To use this curve type, *Y*-values for this
            variable must be all positive or all negative; *X*-values must be
            all positive. If the function dependency is set to :math:`X =
            f(Y)`, *X*-values must be all positive or all negative, and the
            *Y*-values must all be positive.
        `CurveType.Spline`
            A smooth curve is generated that goes through every point. The
            spline is drawn through the data points after sorting the points
            into increasing values of the independent variable, resulting in a
            single-valued function of the independent variable. The spline may
            be clamped or free. With a clamped spline, you supply the
            derivative of the function at each end point; with a non-clamped
            (natural or free) spline, these derivatives are determined for you.
            In xy-line plots, specifying the derivative gives you control over
            the initial and final slopes of the curve.
        `CurveType.ParaSpline` (parametric spline)
            Creates a smooth curve as with a spline, except the assumption is
            that both variables are functions of the index of the data points.
            For example in xy-line plot, `ParaSpline` fits :math:`x = f(i)` and
            :math:`y=g(i)` where :math:`f()` and :math:`g()` are both smooth.
            No additional sorting of the points is performed. This spline may
            result in a multi-valued function of either or both axis variables.

        Example usage::

            >>> from tecplot.constant import CurveType
            >>> plot.linemap(0).curve.curve_type = CurveType.PolynomialFit
        """
        return self._get_style(CurveType, sv.CURVETYPE)

    @curve_type.setter
    def curve_type(self, value):
        self._set_style(CurveType(value), sv.CURVETYPE)

    @property
    def polynomial_order(self):
        """Order of the fit when set to polynomial.

        :type: `integer <int>` (1 to 10)

        A value of 1 will fit the data to a straight line. Example usage::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.polynomial_order = 4
        """
        return self._get_style(int, sv.POLYORDER)

    @polynomial_order.setter
    def polynomial_order(self, value):
        self._set_style(int(value), sv.POLYORDER)

    @property
    def num_points(self):
        """Number of points to use when drawing a fitted curve.

        :type: `integer <int>`

        Example usage::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.num_points = 100
        """
        return self._get_style(int, sv.NUMPTS)

    @num_points.setter
    def num_points(self, value):
        self._set_style(int(value), sv.NUMPTS)

    @property
    def use_weight_variable(self):
        """Use the specified variable for curve-fit weighting.

        :type: `boolean <bool>`

        Example usage::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.use_weight_variable = True
            >>> curve.weight_variable_index = 3
        """
        return self._get_style(bool, sv.USEWEIGHTVAR)

    @use_weight_variable.setter
    def use_weight_variable(self, value):
        self._set_style(bool(value), sv.USEWEIGHTVAR)

    @property
    def weight_variable_index(self):
        """Zero-based index of the variable to use for curve-fit weighting.

        :type: `integer <int>`

        The ``use_weight_variable`` attribute must be set to `True`::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.use_weight_variable = True
            >>> curve.weight_variable_index = 3
        """
        return self._get_style(Index, sv.WEIGHTVAR)

    @weight_variable_index.setter
    def weight_variable_index(self, index):
        self._set_style(Index(index), sv.WEIGHTVAR)

    @property
    def weight_variable(self):
        """Variable to use for curve-fit weighting.

        :type: `Variable`

        Example usage::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.use_weight_variable = True
            >>> curve.weight_variable = dataset.variable('P')
        """
        idx = self.weight_variable_index
        return self.linemap.plot.frame.dataset.variable(idx)

    @weight_variable.setter
    def weight_variable(self, variable):
        self.weight_variable_index = variable.index

    @property
    def use_fit_range(self):
        """Limit the fit to the ``fit_range`` specified.

        :type: `boolean <bool>`

        Example usage::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.use_fit_range = True
            >>> curve.fit_range = 5, 10
        """
        return self._get_style(bool, sv.USEINDVARRANGE)

    @use_fit_range.setter
    def use_fit_range(self, value):
        self._set_style(bool(value), sv.USEINDVARRANGE)

    @property
    def fit_range(self):
        """The range to fit and display a fitted curve.

        :type: 2-`tuple` of `floats <float>`

        Example showing how to set the limits of a polynomial fit to [5,10].
        The ``use_fit_range`` attribute must be set to `True`::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.PolynomialFit
            >>> curve.use_fit_range = True
            >>> curve.fit_range = 5, 10
        """
        vmin = self._get_style(float, sv.INDVARMIN)
        vmax = self._get_style(float, sv.INDVARMAX)
        return LinemapCurve._Limits(vmin, vmax)

    @fit_range.setter
    def fit_range(self, *limits):
        vmin, vmax = LinemapCurve._Limits(*flatten_args(*limits))
        if __debug__:
            if vmax is None or vmin is None:
                err = 'fit_range must be a tuple: (min,max)'
                raise TecplotLogicError(err)
        self._set_style(float(vmin), sv.INDVARMIN)
        self._set_style(float(vmax), sv.INDVARMAX)

    @property
    def clamp_spline(self):
        """Enable derivative clamping for spline fits.

        :type: `boolean <bool>`

        Example showing how to set the derivative at the limits of a spline
        curve to zero::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.Spline
            >>> curve.clamp_spline = True
            >>> curve.spline_derivative_at_ends = 0, 0
        """
        return self._get_style(bool, sv.CLAMPSPLINE)

    @clamp_spline.setter
    def clamp_spline(self, value):
        self._set_style(bool(value), sv.CLAMPSPLINE)

    @property
    def spline_derivative_at_ends(self):
        """Clamp the derivative of the spline fit at the edges of the range.

        :type: 2-`tuple` of `floats <float>`

        Example showing how to set the derivative at the limits of a spline
        curve to zero. Notice the ``clamp_spline`` attribute must be set to
        `True`::

            >>> from tecplot.constant import CurveType
            >>> curve = plot.linemap(0).curve
            >>> curve.curve_type = CurveType.Spline
            >>> curve.clamp_spline = True
            >>> curve.spline_derivative_at_ends = 0, 0
        """
        dstart = self._get_style(float, sv.SPLINEDERIVATIVEATSTART)
        dend = self._get_style(float, sv.SPLINEDERIVATIVEATEND)
        return LinemapCurve._Derivatives(dstart, dend)

    @spline_derivative_at_ends.setter
    def spline_derivative_at_ends(self, *values):
        dstart, dend = LinemapCurve._Derivatives(*flatten_args(*values))
        if __debug__:
            if dend is None or dstart is None:
                err = dedent('''\
                    spline_derivative_at_ends must be a tuple:
                    (deriv_at_start, deriv_at_end)''')
                raise TecplotLogicError(err)
        self._set_style(float(dstart), sv.SPLINEDERIVATIVEATSTART)
        self._set_style(float(dend), sv.SPLINEDERIVATIVEATEND)


class LinemapErrorBars(LinemapStyle):
    """Error bar style and variable assignment control.

    A single `XYLinemap` holds a single `Variable` assignment for error bars.
    Therefore, if you wish to have separate error bars for *x* and *y*, two
    linemaps are required:

    .. code-block:: python
        :emphasize-lines: 32-42, 45

        from math import sqrt
        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, ErrorBar

        # setup dataset
        frame = tp.active_frame()
        ds = frame.create_dataset('Dataset')
        for v in ['x', 'y', 'xerr', 'yerr']:
            ds.add_variable(v)
        zone = ds.add_ordered_zone('Zone', 5)

        # create some data (x, y)
        zone.values('x')[:] = [0,1,2,3,4]
        zone.values('y')[:] = [1,2,4,8,10]

        # error in x is a constant
        zone.values('xerr')[:] = [0.2]*5

        # error in y is the square-root of the value
        zone.values('yerr')[:] = [sqrt(y) for y in zone.values('y')[:]]

        frame.plot_type = PlotType.XYLine
        plot = frame.plot()

        plot.delete_linemaps()
        xerr_lmap = plot.add_linemap('xerr', zone, ds.variable('x'),
                                     ds.variable('y'))
        yerr_lmap = plot.add_linemap('yerr', zone, ds.variable('x'),
                                     ds.variable('y'))

        xerr_lmap.error_bars.variable = ds.variable('xerr')
        xerr_lmap.error_bars.bar_type = ErrorBar.Horz
        xerr_lmap.error_bars.color = Color.Blue
        xerr_lmap.error_bars.line_thickness = 0.8
        xerr_lmap.error_bars.show = True

        yerr_lmap.error_bars.variable = ds.variable('yerr')
        yerr_lmap.error_bars.bar_type = ErrorBar.Vert
        yerr_lmap.error_bars.color = Color.Blue
        yerr_lmap.error_bars.line_thickness = 0.8
        yerr_lmap.error_bars.show = True

        plot.show_lines = False
        plot.show_error_bars = True

        plot.view.fit()

        tp.export.save_png('linemap_error_bars.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap_error_bars.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, linemap):
        self.linemap = linemap
        super().__init__(linemap, sv.ERRORBARS)

    @property
    def show(self):
        """Display error bars on the plot for this :ref:`Linemap`.

        :type: `bool`

        The parent plot object must have error bars enables as well which will
        require a variable to be set::

            >>> plot.linemap(0).error_bars.variable = dataset.variable('E')
            >>> plot.show_error_bars = True
            >>> plot.linemap(0).error_bars.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def bar_type(self):
        """Style of the error bar to draw.

        :type: `ErrorBar`

        Possible values: `Up`, `Down`, `Left <ErrorBar.Left>`, `Right
        <ErrorBar.Right>`, `Horz`, `Vert`, `Cross`.

        Example usage::

            >>> from tecplot.constant import ErrorBar
            >>> plot.linemap(0).error_bars.bar_type = ErrorBar.Cross
        """
        return self._get_style(ErrorBar, sv.BARTYPE)

    @bar_type.setter
    def bar_type(self, value):
        self._set_style(ErrorBar(value), sv.BARTYPE)

    @property
    def color(self):
        """`Color` of the error bars.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.linemap(0).error_bars.color = Color.Red
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def endcap_size(self):
        """Length of the endcaps of the error bars.

        :type: `float`

        Example usage::

            >>> plot.linemap(0).error_bars.endcap_size = 2.5
        """
        return self._get_style(float, sv.SIZE)

    @endcap_size.setter
    def endcap_size(self, value):
        self._set_style(float(value), sv.SIZE)

    @property
    def line_thickness(self):
        """Width of the error bar lines.

        :type: `float`

        Example usage::

            >>> plot.linemap(0).error_bars.line_thickness = 0.8
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def step_mode(self):
        """Space the error bars by index or frame height.

        :type: `StepMode`

        This example will make sure all error bars are no closer than 10% of the
        frame height to each other::

            >>> from tecplot.constant import StepMode
            >>> ebars = plot.linemap(0).error_bars
            >>> ebars.step_mode = StepMode.ByFrameUnits
            >>> ebars.step = 10
        """
        return self._get_style(StepMode, sv.SKIPMODE)

    @step_mode.setter
    def step_mode(self, value):
        self._set_style(StepMode(value), sv.SKIPMODE)

    @property
    def step(self):
        """Space between points to show error bars.

        :type: `float`

        The step is specified either as a percentage of the frame height or
        as a number of indices to skip depending on the value of
        `LinemapErrorBars.step_mode`. This example will add error
        bars to every third point::

            >>> plot.linemap(0).error_bars.step = 3
        """
        return self._get_style(float, sv.SKIPPING)

    @step.setter
    def step(self, value):
        if __debug__:
            if value < 0:
                raise TecplotLogicError('step must be >= 0')
        self._set_style(float(value), sv.SKIPPING)

    @property
    def variable_index(self):
        """Zero-based variable index to use for error bar sizes.

        :type: `integer <int>`

        Example usage::

            >>> plot.linemap(0).error_bars.variable_index = 3
        """
        return self._get_style(Index, sv.VAR)

    @variable_index.setter
    def variable_index(self, index):
        self._set_style(Index(index), sv.VAR)

    @property
    def variable(self):
        """`Variable` to use for error bar sizes.

        :type: `Variable`

        Example usage::

            >>> ebars = plot.linemap(0).error_bars
            >>> ebars.variable = dataset.variable('Err')
        """
        return self.linemap.plot.frame.dataset.variable(self.variable_index)

    @variable.setter
    def variable(self, variable):
        self.variable_index = variable.index


class LinemapIndices(LinemapStyle):
    """Ordering and spacing of points to be drawn.

    Each mapping can show either *I*, *J*, or *K*-varying families of lines. By
    default, the *I*-varying family of lines are displayed. You can also choose
    which members of the family are drawn (and using which data points), by
    specifying index ranges for each of *I*, *J*, and *K*. The index range for
    the varying index says which points to include in each line, and the index
    ranges for the other indices determine which lines in the family to
    include.

    .. code-block:: python
        :emphasize-lines: 15-16

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, IJKLines

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()

        for lmap in list(plot.linemaps())[:3]:
            lmap.show = True
            lmap.indices.varying_index = IJKLines.I
            lmap.indices.i_range = 0,0,3

        # save image to file
        tp.export.save_png('linemap_indices.png', 600, supersample=3)


    ..  figure:: /_static/images/linemap_indices.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, linemap):
        self.linemap = linemap
        super().__init__(linemap, sv.INDICES)

    @property
    def varying_index(self):
        """Family of lines to be drawn.

        :type: `IJKLines`

        This is the order which varies along the lines drawn. *K*-varying is
        only available if the mapping is using an *IJK*-ordered zone::

            >>> from tecplot.constant import IJKLines
            >>> plot.linemap(0).indices.varying_index = IJKLines.J
        """
        return self._get_style(IJKLines, sv.IJKLINES)

    @varying_index.setter
    def varying_index(self, index):
        self._set_style(IJKLines(index), sv.IJKLINES)

    @property
    def i_range(self):
        """`IndexRange` for the *I* dimension of ordered data.

        :type: `tuple` of `integers <int>` (min, max, step)

        This example shows ``I``-lines at ``i = [0, 2, 4, 6, 8, 10]``::

            >>> plot.linemap(0).indices.i_range = 0, 10, 2
        """
        return self._get_style(IndexRange, sv.IRANGE)

    @i_range.setter
    def i_range(self, values):
        self._set_style(IndexRange(*values), sv.IRANGE)

    @property
    def j_range(self):
        """`IndexRange` for the *J* dimension of ordered data.

        :type: `tuple` of `integers <int>` (min, max, step)

        This example shows all ``J``-lines starting with ``j = 10`` up to the
        maximum ``J``-line of the associated `Zone <data_access>`::

            >>> plot.linemap(0).indices.j_range = 10, None, 1
        """
        return self._get_style(IndexRange, sv.JRANGE)

    @j_range.setter
    def j_range(self, values):
        self._set_style(IndexRange(*values), sv.JRANGE)

    @property
    def k_range(self):
        """`IndexRange` for the *K* dimension of ordered data.

        :type: `tuple` of `integers <int>` (min, max, step)

        This example shows all ``K``-lines starting with the first up to 5
        from the last ``K``-line of the associated `Zone <data_access>`::

            >>> plot.linemap(0).indices.k_range = None, -5
        """
        return self._get_style(IndexRange, sv.KRANGE)

    @k_range.setter
    def k_range(self, values):
        self._set_style(IndexRange(*values), sv.KRANGE)


class LinemapLine(LinemapStyle):
    """Style control for the line to be drawn.

    This controls the style of the lines plotted for a given `XYLinemap`.

    .. code-block:: python
        :emphasize-lines: 15-19

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, LinePattern

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()

        lmap = plot.linemap(0)

        line = lmap.line
        line.color = Color.Blue
        line.line_thickness = 1
        line.line_pattern = LinePattern.LongDash
        line.pattern_length = 2

        # save image to file
        tp.export.save_png('linemap_line.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap_line.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, linemap):
        self.linemap = linemap
        super().__init__(linemap, sv.LINES)

    @property
    def show(self):
        """Display this point-to-point line on the plot.

        :type: `bool`

        Example usage::

            >>> plot.linemap(0).line.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def color(self):
        """`Color` of the line to be drawn.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.linemap(0).line.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Width of the line to be drawn.

        :type: `float`

        Example usage::

            >>> plot.linemap(0).line.line_thickness = 0.5
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def line_pattern(self):
        """Pattern style of the line to be drawn.

        :type: `LinePattern`

        Possible values: `Solid <LinePattern.Solid>`, `Dashed`, `DashDot`,
        `Dotted`, `LongDash`, `DashDotDot`.

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> lmap = plot.linemap(0)
            >>> lmap.line.line_pattern = LinePattern.LongDash
        """
        return self._get_style(LinePattern, sv.LINEPATTERN)

    @line_pattern.setter
    def line_pattern(self, value):
        self._set_style(LinePattern(value), sv.LINEPATTERN)

    @property
    def pattern_length(self):
        """Segment length of the repeated line pattern.

        :type: `float`

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> lmap = plot.linemap(0)
            >>> lmap.line.line_pattern = LinePattern.LongDash
            >>> lmap.line.pattern_length = 3.5
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self, value):
        self._set_style(float(value), sv.PATTERNLENGTH)


class LinemapSymbols(LinemapStyle):
    """Style control for markers placed along lines.

    This class allows the user to set the style of the symbols to be shown
    including setting a geometric shape, text character, line and fill
    colors and spacing. The plot-level ``show_symbols`` attribute must be
    enabled to show symbols in any specific linemap within the plot:

    .. code-block:: python
        :emphasize-lines: 12,15-21

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, FillMode, GeomShape

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        plot.show_symbols = True

        for lmap in list(plot.linemaps())[:3]:
            lmap.symbols.show = True
            lmap.symbols.symbol().shape = GeomShape.Square
            lmap.symbols.size = 2.5
            lmap.symbols.color = Color.Blue
            lmap.symbols.line_thickness = 0.4
            lmap.symbols.fill_mode = FillMode.UseSpecificColor
            lmap.symbols.fill_color = Color.Azure

        # save image to file
        tp.export.save_png('linemap_symbols.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap_symbols.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, linemap):
        self.linemap = linemap
        super().__init__(linemap, sv.SYMBOLS)

    @property
    def show(self):
        """Display symbols along the lines to be drawn.

        :type: `bool`

        The parent plot object must have symbols enabled as well::

            >>> plot.show_symbols = True
            >>> plot.linemap(0).symbols.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def symbol_type(self):
        """The `SymbolType` to use for this linemap.

        :type: `SymbolType`

        Possible values are: `SymbolType.Geometry`, `SymbolType.Text`.

        This sets the active symbol type. Use LinemapSymbols.symbol` to access
        the symbol::

            >>> from tecplot.constant import SymbolType
            >>> linemap = plot.linemap(0)
            >>> linemap.symbols.symbol_type = SymbolType.Text
            >>> symbol = linemap.symbols.symbol(SymbolType.Text)
            >>> symbol.text = 'a'
        """
        return Symbol(self)._symbol_type

    @symbol_type.setter
    def symbol_type(self, value):
        Symbol(self)._symbol_type = value

    def symbol(self, symbol_type=None):
        """Returns a linemap symbol style object.

        Parameters:
            symbol_type (`SymbolType`, optional): The type of symbol to return.
                By default, this will return the active symbol type which is
                obtained from `LinemapSymbols.symbol_type`.

        Returns: `TextSymbol` or `GeometrySymbol`

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> plot.linemap(0).symbols.symbol_type = SymbolType.Text
            >>> symbol = plot.linemap(0).symbols.symbol()
            >>> symbol.text = 'a'
        """
        _dispatch = {
            SymbolType.Text: TextSymbol,
            SymbolType.Geometry: GeometrySymbol}
        return _dispatch[symbol_type or self.symbol_type](self)

    @property
    def step_mode(self):
        """Space the symbols by index or frame height.

        :type: `StepMode`

        This example will make sure all symbols are no closer than 10% of the
        frame height to each other::

            >>> from tecplot.constant import StepMode
            >>> sym = plot.linemap(0).symbols
            >>> sym.step_mode = StepMode.ByFrameUnits
            >>> sym.step = 10
        """
        return self._get_style(StepMode, sv.SKIPMODE)

    @step_mode.setter
    def step_mode(self, value):
        self._set_style(StepMode(value), sv.SKIPMODE)

    @property
    def step(self):
        """Space between symbols to be shown.

        :type: `float`

        The step is specified either as a percentage of the frame height or
        as a number of indices to skip depending on the value of
        `LinemapSymbols.step_mode`. This example will add symbols
        to every third point::

            >>> plot.linemap(0).symbols.step = 3
        """
        return self._get_style(float, sv.SKIPPING)

    @step.setter
    def step(self, value):
        if __debug__:
            if value < 0:
                raise TecplotLogicError('step must be >= 0')
        self._set_style(float(value), sv.SKIPPING)

    @property
    def size(self):
        """Size of the symbols to draw.

        :type: `float`

        Example usage::

            >>> plot.linemap(0).symbols.size = 3.5
        """
        return self._get_style(float, sv.SIZE)

    @size.setter
    def size(self, value):
        self._set_style(float(value), sv.SIZE)

    @property
    def fill_mode(self):
        """The fill mode for the background.

        :type: `FillMode`

        Possible values: `FillMode.UseSpecificColor`, `FillMode.UseLineColor`,
            `FillMode.UseBackgroundColor` or `FillMode.None_`.

        Example usage::

            >>> from tecplot.constant import Color, FillMode
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.fill_mode = FillMode.UseBackgroundColor
        """
        return self._get_style(FillMode, sv.FILLMODE)

    @fill_mode.setter
    def fill_mode(self, value):
        self._set_style(FillMode(value), sv.FILLMODE)

    @property
    def fill_color(self):
        """The fill or background color.

        :type: `Color`

        The ``fill_mode`` attribute must be set to
        `FillMode.UseSpecificColor`::

            >>> from tecplot.constant import Color, FillMode
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.fill_mode = FillMode.UseSpecificColor
            >>> symbols.fill_color = Color.Yellow
        """
        return self._get_style(Color, sv.FILLCOLOR)

    @fill_color.setter
    def fill_color(self, value):
        self._set_style(Color(value), sv.FILLCOLOR)

    @property
    def color(self):
        """Edge or text `Color` of the drawn symbols.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.linemap(1).symbols.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Width of the lines when drawing geometry symbols.

        :type: `float`

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> symbols = plot.linemap(0).symbols
            >>> symbols.symbol_type = SymbolType.Geometry
            >>> symbols.line_thickness = 0.8
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class Linemap(session.Style):
    """Style control for line plots.

    The Linemap layer controls how ordered or connected data is represented.
    This may be either a simple collection of line segments connecting all the
    data points, or a curve fitted to the original data::

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, LinePattern, AxisTitleMode

        # load data from examples directory
        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        # get handle to the active frame and set plot type to XY Line
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()

        # We will set the name, color and a few other properties
        # for the first three linemaps in the dataset.
        names = ['Seattle', 'Dallas', 'Miami']
        colors = [Color.Blue, Color.DeepRed, Color.Khaki]

        # loop over the linemaps, setting style for each
        for lmap,name,color in zip(plot.linemaps(),names,colors):
            lmap.show = True
            lmap.name = name # This will be used in the legend

            # Changing some line attributes
            line = lmap.line
            line.color = color
            line.line_thickness = 1
            line.line_pattern = LinePattern.LongDash
            line.pattern_length = 2

        # Set the y-axis label
        plot.axes.y_axis(0).title.title_mode = AxisTitleMode.UseText
        plot.axes.y_axis(0).title.text = 'Rainfall'

        # Turn on legend
        plot.legend.show = True

        # Adjust the axes limits to show all the data
        plot.view.fit()

        # save image to file
        tp.export.save_png('linemap.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, uid, plot):
        self.uid = uid
        self.plot = plot
        super().__init__(sv.LINEMAP, uniqueid=self.plot.frame.uid,
                         offset1=self.index, multiset=True)

    def __eq__(self, that):
        return self.uid == that.uid

    def __ne__(self, that):
        return not (self == that)

    @property
    def aux_data(self):
        """Auxiliary data for this linemap.

        Returns: `AuxData`

        This is the auxiliary data attached to the linemap. Such data is
        written to the layout file by default and can be retrieved later.
        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = tp.active_frame().plot(PlotType.XYLine)
            >>> aux = plot.linemap(0).aux_data
            >>> aux['Result'] = '3.14159'
            >>> print(aux['Result'])
            3.14159
        """
        return session.AuxData(self.plot.frame, AuxDataObjectType.Linemap,
                               self.index)

    @property
    def index(self):
        """Zero-based integer identifier for this :ref:`Linemap`.

        :type: `integer <int>`

        Example::

            >>> lmap = plot.linemap(1)
            >>> print(lmap.index)
            1
        """
        with self.plot.frame.activated():
            return Index(_tecutil.LineMapGetNumByUniqueID(self.uid) - 1)

    @property
    def name(self):
        """Name identifier of this :ref:`Linemap`.

        :type: `string <str>`

        Names are automatically assigned to each mapping. The nature of the
        name depends on the type of data used to create the mapping. If your
        data has only one dependent variable, the default is to use the zone
        name for the mapping. If your data has multiple dependent variables,
        then the default is to use the dependent variable name for the mapping.
        In either case each mapping is assigned a special name (``&ZN&`` or
        ``&DN&``) that is replaced with the zone or variable name when the name
        is displayed.

        Selecting variables in a 3D finite element zone may require significant
        time, since the variable must be loaded over the entire zone. XY and
        Polar line plots are best used with linear or ordered data, or with
        two-dimensional finite element data.

        Certain placeholder text will be replaced with values based on elements
        within the plot. By combining static text with these placeholders, you
        can construct a name in any format you like::

            >>> plot.linemap(2).name = 'Zone: &ZN&'

        The placeholders available are:

        Zone name (``&ZN&``)
            This will be replaced with the actual name of the zone assigned to
            that mapping.
        Zone number (``&Z#&``)
            This will be replaced with the actual number of the zone assigned
            to the mapping.
        Independent variable name (``&IV&``)
            This will be replaced with the actual name of the independent
            variable assigned to that mapping.
        Independent variable number (``&I#&``)
            This will be replaced with the actual number of the independent
            variable assigned to the mapping.
        Dependent variable name (``&DV&``)
            This will be replaced with the actual name of the dependent
            variable assigned to that mapping.
        Dependent variable number (``&D#&``)
            This will be replaced with the actual number of the dependent
            variable assigned to the mapping.
        Map number (``&M#&``)
            This will be replaced with the actual number of the mapping.
        X-Axis number (``&X#&``)
            This will be replaced with the actual number of the X-axis assigned
            to that mapping for XY Line plots. This option is not available
            for Polar Line plots.
        Y-Axis number (``&Y#&``)
            This will be replaced with the actual number of the Y-axis assigned
            to that mapping for XY Line plots. This option is not available
            for Polar Line plots.
        """
        return self._get_style(str, sv.NAME)

    @name.setter
    def name(self, name):
        self._set_style(str(name), sv.NAME)

    @property
    def show(self):
        """Display this linemap on the plot.

        :type: `bool`

        Example usage for turning on all linemaps::

            >>> for lmap in plot.linemaps():
            ...     lmap.show = True
        """
        return self.index in self.plot.active_linemap_indices

    @show.setter
    def show(self, show):
        assignment = AssignOp.PlusEquals if show else AssignOp.MinusEquals
        session.set_style({self.index}, sv.ACTIVELINEMAPS,
                          assignmodifier=assignment,
                          uniqueid=self.plot.frame.uid)

    @property
    def zone_index(self):
        """Zero-based index of the `Zone <data_access>` this :ref:`Linemap` will draw.

        :type: `integer <int>`

        Example usage::

            >>> plot.linemap(0).zone_index = 2
        """
        return self._get_style(Index, sv.ASSIGN, sv.ZONE)

    @zone_index.setter
    def zone_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.ZONE)

    @property
    def zone(self):
        """`Zone <data_access>` this :ref:`Linemap` will draw.

        :type: `Zone <data_access>`

        Example usage::

            >>> plot.linemap(0).zone = dataset.zone('Zone 1')
        """
        return self.plot.frame.dataset.zone(self.zone_index)

    @zone.setter
    def zone(self, zone):
        self.zone_index = getattr(zone, 'index', zone)

    @property
    def show_in_legend(self):
        """Show this :ref:`Linemap` in the legend.

        :type: `LegendShow`

        Possible values:

        `LegendShow.Always`
            The mapping appears in the legend even if the mapping is turned off
            (deactivated) or its entry in the table looks exactly like another
            mapping's entry.

        `LegendShow.Never`
            The mapping never appears in the legend.

        `LegendShow.Auto` (default)
            The mapping appears in the legend only when the mapping is turned
            on. If two mappings would result in the same entry in the legend,
            only one entry is shown.
        """
        return self._get_style(LegendShow, sv.ASSIGN, sv.SHOWINLEGEND)

    @show_in_legend.setter
    def show_in_legend(self, value):
        self._set_style(LegendShow(value or 1), sv.ASSIGN, sv.SHOWINLEGEND)

    @property
    def sort_mode(self):
        """Mode controlling which `Variable` to use when sorting lines.

        :type: `LineMapSort`

        Possible values:  `LineMapSort.BySpecificVar`,
        `LineMapSort.ByIndependentVar`, `LineMapSort.ByDependentVar` or
        `LineMapSort.None_`.

        Example usage::

            >>> from tecplot.constant import LineMapSort
            >>> plot.linemap(0).sort_mode = LineMapSort.ByDependentVar
        """
        return self._get_style(LineMapSort, sv.ASSIGN, sv.SORT)

    @sort_mode.setter
    def sort_mode(self, value):
        try:
            self._set_style(LineMapSort(value), sv.ASSIGN, sv.SORT)
        except TecplotSystemError:
            msg = dedent('''\
                A variable must be set using sort_variable before the mode can
                be set to BySpecificVar''')
            raise TecplotLogicError(msg)

    @property
    def sort_variable(self):
        """Specific `Variable` used when listing lines.

        :type: `Variable`

        The ``sort_mode`` attribute must be set to `LineMapSort.BySpecificVar`::

            >>> from tecplot.constant import LineMapSort
            >>> plot.linemap(0).sort_by = LineMapSort.BySpecificVar
            >>> plot.linemap(0).sort_variable = dataset.variable('P')
        """
        idx = self.sort_variable_index
        return self.plot.frame.dataset.variable(idx)

    @sort_variable.setter
    def sort_variable(self, value):
        self.sort_variable_index = value.index

    @property
    def sort_variable_index(self):
        """Zero-based index of the specific `Variable` used for sorting.

        :type: `integer <int>`

        The ``sort_mode`` attribute must be set to `LineMapSort.BySpecificVar`::

            >>> from tecplot.constant import LineMapSort
            >>> plot.linemap(0).sort_by = LineMapSort.BySpecificVar
            >>> plot.linemap(0).sort_variable_index = 3
        """
        return self._get_style(Index, sv.ASSIGN, sv.SORTVAR)

    @sort_variable_index.setter
    def sort_variable_index(self, value):
        self._set_style(Index(value), sv.ASSIGN, sv.SORTVAR)

    @property
    def curve(self):
        """`LinemapCurve` style and fitting-method control for lines.

        :type: `LinemapCurve`
        """
        return LinemapCurve(self)

    @property
    def indices(self):
        """`LinemapIndices` object controlling which lines are shown.

        :type: `LinemapIndices`
        """
        return LinemapIndices(self)

    @property
    def line(self):
        """`LinemapLine` style for lines to be drawn.

        :type: `LinemapLine`
        """
        return LinemapLine(self)

    @property
    def symbols(self):
        """`LinemapSymbols` style for markers at points along the lines.

        :type: `LinemapSymbols`
        """
        return LinemapSymbols(self)


class XYLinemap(Linemap):
    """Data mapping for 2D Cartesian line plots.

    Linemaps connect a specific `Zone <data_access>`/`Variable` combination to
    a line or set of lines, depending on the dimension of the data if ordered.
    Linemaps can share any of the axes available in the plot and orientation
    can be verical or horizontal by setting the independent variable with
    `XYLinemap.function_dependency`:

    .. code-block:: python
        :emphasize-lines: 13-16,17-23

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()

        lmap = plot.linemap(0)
        lmap.line.line_thickness = 0.8
        lmap.line.color = Color.DeepRed
        lmap.y_axis.title.color = Color.DeepRed

        lmap = plot.linemap(1)
        lmap.show = True
        lmap.y_axis_index = 1
        lmap.line.line_thickness = 0.8
        lmap.line.color = Color.Blue
        lmap.y_axis.title.color = lmap.line.color

        tp.export.save_png('linemap_xy.png', 600, supersample=3)

    ..  figure:: /_static/images/linemap_xy.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def x_axis_index(self):
        """Zero-based index of the x-axis used by this linemap.

        :type: `integer <int>`

        Example usage::

            >>> plot.linemap(0).x_axis_index = 2
        """
        return self._get_style(Index, sv.ASSIGN, sv.XAXIS)

    @x_axis_index.setter
    def x_axis_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.XAXIS)

    @property
    def x_axis(self):
        """X-axis used by this linemap.

        :type: `LineAxis`

        Example usage::

            >>> plot.linemap(0).x_axis = plot.axes.x_axis(2)
        """
        return self.plot.axes.x_axis(self.x_axis_index)

    @x_axis.setter
    def x_axis(self, axis):
        self.x_axis_index = axis.index

    @property
    def y_axis_index(self):
        """Zero-based index of the y-axis used by this linemap.

        :type: `integer <int>`

        Example usage::

            >>> plot.linemap(0).y_axis_index = 2
        """
        return self._get_style(Index, sv.ASSIGN, sv.YAXIS)

    @y_axis_index.setter
    def y_axis_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.YAXIS)

    @property
    def y_axis(self):
        """Y-axis used by this linemap.

        :type: `LineAxis`

        Example usage::

            >>> plot.linemap(0).x_axis = plot.axes.y_axis(2)
        """
        return self.plot.axes.y_axis(self.y_axis_index)

    @y_axis.setter
    def y_axis(self, axis):
        self.y_axis_index = axis.index

    @property
    def x_variable_index(self):
        """Zero-based index of the `Variable` used for x-positions.

        :type: `integer <int>`

        Example usage::

            >>> plot.linemap(0).x_variable_index = 2
        """
        return self._get_style(Index, sv.ASSIGN, sv.XAXISVAR)

    @x_variable_index.setter
    def x_variable_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.XAXISVAR)

    @property
    def x_variable(self):
        """`Variable` used for x-positions of this linemap.

        :type: `Variable`

        Example usage::

            >>> plot.linemap(0).x_variable = dataset.variable('P')
        """
        return self.plot.frame.dataset.variable(self.x_variable_index)

    @x_variable.setter
    def x_variable(self, variable):
        self.x_variable_index = variable.index

    @property
    def y_variable_index(self):
        """Zero-based index of the `Variable` used for y-positions.

        :type: `integer <int>`

        Example usage::

            >>> plot.linemap(0).y_variable_index = 2
        """
        return self._get_style(Index, sv.ASSIGN, sv.YAXISVAR)

    @y_variable_index.setter
    def y_variable_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.YAXISVAR)

    @property
    def y_variable(self):
        """`Variable` used for y-positions of this linemap.

        :type: `Variable`

        Example usage::

            >>> plot.linemap(0).y_variable = dataset.variable('Q')
        """
        return self.plot.frame.dataset.variable(self.y_variable_index)

    @y_variable.setter
    def y_variable(self, variable):
        self.y_variable_index = variable.index

    @property
    def function_dependency(self):
        """The independent variable for function evalulation.

        :type: `FunctionDependency`

        Possible values: `XIndependent`, `YIndependent`.

        Example usage::

            >>> from tecplot.constant import FunctionDependency
            >>> lmap = plot.linemap(0)
            >>> lmap.function_dependency = FunctionDependency.YIndependent
        """
        return self._get_style(FunctionDependency, sv.ASSIGN,
                               sv.FUNCTIONDEPENDENCY)

    @function_dependency.setter
    def function_dependency(self, value):
        self._set_style(FunctionDependency(value), sv.ASSIGN,
                        sv.FUNCTIONDEPENDENCY)

    @property
    def bars(self):
        """`LinemapBars` style for bar charts.

        :type: `LinemapBars`
        """
        return LinemapBars(self)

    @property
    def error_bars(self):
        """`LinemapErrorBars` style for error bars.

        :type: `LinemapErrorBars`
        """
        return LinemapErrorBars(self)


class PolarLinemap(Linemap):

    @property
    def r_axis(self):
        """Radial axis used by this linemap.

        :type: `RadialLineAxis`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.PolarLine)
            >>> plot.linemap(0).r_axis.title = 'distance (m)'
        """
        return self.plot.axes.r_axis

    @property
    def theta_axis(self):
        """Angular axis used by this linemap.

        :type: `PolarAngleLineAxis`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.PolarLine)
            >>> plot.linemap(0).theta_axis.title = 'angle (deg)'
        """
        return self.plot.axes.theta_axis

    @property
    def r_variable_index(self):
        """:math:`r`-component `Variable` index of the plotted line.

        :type: `integer <int>` (Zero-based index)

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.PolarLine)
            >>> plot.linemap(0).r_variable_index = 0
        """
        return self._get_style(Index, sv.ASSIGN, sv.RAXISVAR)

    @r_variable_index.setter
    def r_variable_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.RAXISVAR)

    @property
    def r_variable(self):
        return self.plot.frame.dataset.variable(self.r_variable_index)

    @r_variable.setter
    def r_variable(self, variable):
        self.r_variable_index = variable.index

    @property
    def theta_variable_index(self):
        """:math:`\theta`-component `Variable` index of the plotted line.

        :type: `integer <int>` (Zero-based index)

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.PolarLine)
            >>> plot.linemap(0).theta_variable_index = 1
        """
        return self._get_style(Index, sv.ASSIGN, sv.THETAAXISVAR)

    @theta_variable_index.setter
    def theta_variable_index(self, index):
        self._set_style(Index(index), sv.ASSIGN, sv.THETAAXISVAR)

    @property
    def theta_variable(self):
        return self.plot.frame.dataset.variable(self.theta_variable_index)

    @theta_variable.setter
    def theta_variable(self, variable):
        self.theta_variable_index = variable.index

    @property
    def function_dependency(self):
        """The independent variable for function evalulation.

        :type: `FunctionDependency`

        Possible values: ``RIndependent``, ``ThetaIndependent``. Example
        usage::

            >>> from tecplot.constant import FunctionDependency, PlotType
            >>> plot = frame.plot(PlotType.PolarLine)
            >>> lmap = plot.linemap(0)
            >>> lmap.function_dependency = FunctionDependency.ThetaIndependent
        """
        return self._get_style(FunctionDependency, sv.ASSIGN,
                               sv.FUNCTIONDEPENDENCY)

    @function_dependency.setter
    def function_dependency(self, value):
        self._set_style(FunctionDependency(value), sv.ASSIGN,
                        sv.FUNCTIONDEPENDENCY)
