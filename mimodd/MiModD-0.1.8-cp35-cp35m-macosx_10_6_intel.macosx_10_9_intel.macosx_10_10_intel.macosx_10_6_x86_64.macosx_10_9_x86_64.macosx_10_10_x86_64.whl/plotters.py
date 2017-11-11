import itertools
import warnings

from decimal import Decimal
from math import floor, ceil, log10, log


try:
    import rpy2.rinterface as rinterface
    import rpy2.robjects as robjects
    RPY_EXCEPTION = None
except Exception as e:
    RPY_EXCEPTION = e


class PlotHandle (object):
    def __init__ (self, plotter, with_scatter = False, with_hist = True,
                  scatter_params = {}, hist_params = {}):
        if not with_scatter:
            if not with_hist:
                raise RuntimeError(
                    'at least one of "with_scatter" and "with_hist" needs '
                    'to be True.'
                    )
            if scatter_params:
                raise RuntimeError(
                    'scatter plot parameters can only be used on scatter plots.'
                    )
        self.plotter = plotter
        self.with_scatter = with_scatter
        self.with_hist = with_hist
        self.hist_params = hist_params
        self.scatter_params = scatter_params
        self.hist_plot_func = plot_histograms
        self.scatter_plot_func = plot_weighed_scatter

    def plot_histogram (self, data, params = None):
        if params is None:
            params = self.hist_params
        self.plotter.send([self.hist_plot_func, data, params])

    def plot_scatter (self, data, params = None):
        if params is None:
            params = self.scatter_params
        self.plotter.send([self.scatter_plot_func, data, params])

    def __enter__ (self):
        return self

    def __exit__ (self, *error_desc):
        self.plotter.close()


def contig_plotter (ofile, **plot_params):
    #robjects.r.postscript(ofile, paper='special', width=9, height=8)
    robjects.r.pdf(ofile, 8, 8)
    try:
        plot_func, data, current_plot_params = yield True
    except GeneratorExit:
        robjects.r["dev.off"]()
        return
    while True:
        merged_params = {k:v for k,v in plot_params.items()}
        merged_params.update(current_plot_params)
        try:
            plot_func(data, **merged_params)
        except rinterface.RRuntimeError as e:
            print (e)
            print ('There was an error creating the location plot pdf... '
                   'Please try again')
        try:
            plot_func, data, current_plot_params = yield True
        except GeneratorExit:
            robjects.r["dev.off"]()
            return


def plot_weighed_scatter (
    data, raw_data, title = '', xlab = '', ylab = '', loess_span = None,
    xlim = None, ylim = None, points_colors = None, loess_colors = None,
    major_tick_unit = None, draw_secondary_grid_lines = True,
    no_warnings = False
    ):    

    x_axis_scale = 10**6 # plot in Megabases

    if xlim:
        xlim = xlim / x_axis_scale
    else:
        xlim = max(d[0] for data_series in data for d in data_series) / x_axis_scale
    if major_tick_unit is None:
        major_tick_unit = x_axis_scale
        
    break_unit = major_tick_unit / x_axis_scale
    half_break_unit = break_unit / 2
    break_penta_unit = break_unit * 5

    if points_colors is None:
        points_colors = ['black']
    else:
        points_colors = points_colors[::-1]
    data = data[::-1]    
    rcoords = [robjects.r['xy.coords'](
        [d[0]/x_axis_scale for d in data_series], [d[1] for d in data_series]
        ) for data_series in data]
#    for i, data_series in enumerate(data):
#        print(i, ':')
#        print(len(data_series))
#        print(len([d[0] for d in data_series]))
#        print(len([d[1] for d in data_series]))        

    # Set the color range for the scatter plot data.
    # The user-specified points_color is used as the right end of a range of
    # 16 shades. The left end is a lighter version of that color (213/255, an
    # empirically determined ratio) along the way to white).
    rcolsasrgb = [robjects.r['col2rgb'](c) for c in points_colors]
    rstartcols = [robjects.r['rgb'](*[(c+(255-c)*213/255)/255 for c in col]) for col in rcolsasrgb]
    rcolranges = [robjects.r['c'](s, c) for s, c in zip(rstartcols, points_colors)]
    rpalettes = [robjects.r['colorRampPalette'](rcolrange)(16) for rcolrange in rcolranges]
    palettes_cycle = itertools.cycle(rpalettes)
    # the color of individual data points is based on their quadratic weight
    # with the data point with the highest weight being plotted in the
    # user-defined points_color. The quadratic dependency was empirically
    # determined to yield good contrast in most situations.
    max_weight = max(d[2] for data_series in data for d in data_series)
    rcols = [robjects.r['c'](
        *[ceil(d[2]**2*16/max_weight) for d in data_series]
        ) for data_series in data]

    # plot the scatter data
    optional_params = {}
    if ylim is not None:
        optional_params.update(ylim=robjects.r['c'](0, ylim))
    rplot = robjects.r['plot']
    rpoints = robjects.r['points']
    old_palette = robjects.r['palette'](next(palettes_cycle))
    rplot(rcoords[0],
          col=rcols[0],
          cex=0.5,
          pch=15,
          main='LG {}'.format(title or '?'),
          xlab=xlab,
          ylab=ylab,
          xlim=robjects.r['c'](0, xlim),
          **optional_params
          )
    for coords, cols in zip(rcoords[1:], rcols[1:]):
        _ = robjects.r['palette'](next(palettes_cycle))
        rpoints(coords, col=cols, cex=0.5, pch=15)
    
    if loess_span:
        with warnings.catch_warnings():
            # Need to disable warnings transiently or
            # an RRuntimeWarning would be shown on stderr when the
            # Loess calculation fails in addition to our own stdout
            # message below.
            warnings.simplefilter('ignore')
            # loess line
            raw_coords = [
                (robjects.r['c'](*[d[0]/x_axis_scale for d in data_series]),
                 robjects.r['c'](*[d[1] for d in data_series]))
                for data_series in raw_data
                ]
            if loess_colors is None:
                loess_colors = ['black']
            loess_colors_cycle = itertools.cycle(loess_colors)
            for i, raw_coord_series in enumerate(raw_coords):
                try:
                    loess_fit = robjects.r['loess.smooth'](
                        *raw_coord_series,
                        # we want to evaluate the Loess function at as many points
                        # as we have hexbins
                        evaluation=len(data[i]),
                        span=loess_span
                        )
                except rinterface.RRuntimeError as e:
                    if not no_warnings:
                        print('Could not generate a Loess regression line for',
                              title)
                        print('R reported this problem:')
                        print(e)
                        # TO DO: write a message to the plot
                        # explaining that there is no regression line because of
                        # a too small span
                else:
                    robjects.r['lines'](
                        loess_fit, lwd=2, col=next(loess_colors_cycle)
                        )
        
    # axes
    robjects.r(
        'axis(1, at=seq(0,{xlim},by={xunits}), labels=FALSE, tcl=-0.5)'
        .format(xlim=xlim, xunits=break_unit)
        )
    robjects.r(
        'axis(1, at=seq(0,{xlim},by={xunits}), labels=FALSE, tcl=-0.25)'
        .format(xlim=xlim, xunits=half_break_unit)
        )
    robjects.r('axis(2, at=seq(0,1,by=0.1), labels=FALSE, tcl=-0.2)')

    # optional grid lines
    if draw_secondary_grid_lines:
        robjects.r(
            'abline(h=seq(0,1,by=0.1), v=seq(0,{xlim},by=1), col="gray")'
            .format(xlim=xlim)
            )



def plot_histograms (
    data, title = '', xlab = '', ylab = '', xlim = None, ylim = None,
    major_tick_unit = None, hist_colors = None, lines_plot = None
    ):
    
    x_axis_scale = Decimal(10**6) # plot in Megabases
    if major_tick_unit is None:
        major_tick_unit = x_axis_scale
    if xlim:
        xlim = xlim / x_axis_scale

    break_unit = major_tick_unit / x_axis_scale
    half_break_unit = break_unit / 2
    break_penta_unit = break_unit * 5

    if hist_colors is None:
        hist_colors = ['darkgrey', 'red']
    color_cycle = itertools.cycle(hist_colors)
    
    # does the translation into R
    for n, binned_data in enumerate(data.items()):
        bin_width, data_series = binned_data
        bin_width = Decimal(bin_width) / x_axis_scale
        
        varname = 'series' + str(n)
        robjects.r('{var} <- c({data})'
                   .format(var=varname,
                           data=','.join(str(d)
                                         for d in data_series.values())
                           )
          )
        if ylim is None:
            # use the maximum value observed in the data for this plot
            max_observed_y = max(value for series in data.values()
                                       for value in series.values())
            ylim = pretty_round(max_observed_y)

        if not xlim:
            xlim = bin_width * len(data_series)
        if n == 0:
            # first fresh plot
            robjects.r(
                'barplot({var}, main="LG {title}", '
                'xlim=c(0,{xlim}), ylim=c(0,{ylim}), width={width}, space=0, '
                'col="{color}", xlab="{xlab}", ylab="{ylab}")'
                .format(var=varname,
                        ylim=ylim,
                        xlim=xlim,
                        width=bin_width,
                        xlab=xlab,
                        ylab=ylab,
                        title=title or '?',
                        color=next(color_cycle))
                )
            # axes
            robjects.r(
                'axis(1, hadj=1, at=seq(0,{xlim},by={width}), labels=FALSE, '
                'tcl=-0.5)'
                .format(xlim=xlim, width=break_unit)
                )
            robjects.r(
                'axis(1, at=seq(0,{xlim},by={width}), labels=TRUE, tcl=-0.5)'
                .format(xlim=xlim, width=break_penta_unit)
                )
            robjects.r(
                'axis(1, at=seq(0,{xlim},by={width}), labels=FALSE, tcl=-0.25)'
                .format(xlim=xlim, width=half_break_unit)
                )
        else:
            # additional histograms are just added to the first plot
            robjects.r(
                 'barplot({var}, '
                 'add=TRUE, space=0, col="{color}", width={width})'
                 .format(var=varname,
                         width=bin_width,
                         color=next(color_cycle))
                 )

    if lines_plot:
        # Kernel density estimates based on the binned data in lines_plot
        # are to be calculated and shown on top of the regular histograms.
        for bin_width, data_series in lines_plot.items():
            bin_width = Decimal(bin_width) / x_axis_scale
            # weight_scale=sum(d for d in data_series.values())
            kde =robjects.r['density'](
                x=robjects.r['seq'](
                    f=float(bin_width/2), by=float(bin_width),
                    length=len(data_series)
                    ),
                weights=robjects.r['c'](
                    *[float(d) for d in data_series.values()]
                    ),
                kernel='gaussian',
                bw='nrd',
                adjust=0.3
                )
            x_values = robjects.r['c'](
                *[x/float(x_axis_scale) for x in kde.rx2('x')]
                )
            robjects.r['lines'](kde)

            # TO DO: the following adds text information about the maximum
            # of the kde to the plot, but currently only works reasonably if
            # a single kde gets calculated (as in VAF mapping mode).
            # If lines_plot contains several binned distributions, then the
            # text pieces are printed to the same coordinates in the plot,
            # overwriting each other.
            x_estimate, y_estimate = max(zip(kde.rx2('x'), kde.rx2('y')),
                                         key=lambda x: x[1])
            estimate_message = 'best mapping estimate based on 10 kb interval kde: pos={0}, score={1:.2f}'\
                               .format(round(x_estimate*float(x_axis_scale)),
                                       y_estimate)
            robjects.r['text'](
                x=float(xlim/2),
                y=float(ylim),
                pos=1,
                labels=estimate_message
                )

    
def pretty_round (max_observed_y, scale = 1.1):
    scale = type(max_observed_y)(scale)
    if max_observed_y < 10:
        return int(scale*max_observed_y) or 1
    max_observed_y = int(scale*int(max_observed_y))
    return int(round(max_observed_y, 1-floor(log10(max_observed_y)) or -1))
