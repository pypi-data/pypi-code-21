# -*- coding: utf-8 -*-
"""Visualizer for BBD values."""
import numpy as np
# # make sure numpy warning are real warnings, as some of them tend to mess up the plotting
# np.seterr(all='warn')
import math
from scipy.special import beta
from scipy.misc import comb


from tornado.ioloop import IOLoop

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Span, Label, LabelSet
from bokeh.models.ranges import Range1d
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure
from bokeh.server.server import Server


ELEMENTS = dict()
MEAN_COLOR = "teal"
Y_AXIS = 0.4

class BinomBeta:
    """
    """

    def __init__(self, ds, a, b):
        """
        """

        self.n = math.floor((ds * (a + b)) / a)
        self.a = a
        self.b = b
        self.probs = np.array([self.binom_beta(k, self.n, a, b) for k in range(self.n+1)])
        self.values = np.arange(0,self.n+1)


    def binom_beta(self, k,n,a,b):
        """
        """
        c = comb(n,k)
        x = beta(k+a, n-k+b)
        y = beta(a,b)
        if np.isinf(c) and np.isclose(x*y, 0):
            # set values that are infinite for c but 0 for the rest to 0
            return 0
        elif np.isinf(c):
            # set values that are infinite for c to 1 (max val)
            return 1
        else:
            # return the normally computed value
            return c * x / y


    def variance(self):
        """
        """
        return self.n*self.a*self.b*(self.a+self.b+self.n) / ((self.a+self.b)*(self.a+self.b)*(self.a+self.b+1))

    def std_dev(self):
        """
        """
        return math.sqrt(self.variance())

    def get_first_stddevs(self):
        """
        """
        sdev = self.std_dev()
        mean = self.mean()
        return (mean - sdev, mean + sdev)

    def mean(self):
        """
        """
        return (self.n * self.a) / (self.a + self.b)

    def mode(self):
        return np.argmax(self.probs), np.max(self.probs)


# Set up callbacks
def update_title(attrname, old, new):
    """Change title of plot after text has been changed."""
    ELEMENTS["text"].value = new
    ELEMENTS["plot"].title.text = new


def update_data(attrname, old, new):
    """Update all widgets after a slider has been changed.

    Move labels and lines, redraw the curve
    """
    # Get the current slider values
    a_val = ELEMENTS["a_slider"].value
    b_val = ELEMENTS["b_slider"].value
    ds_val = ELEMENTS["ds_slider"].value

    # Generate the new curve, recompute the bbd
    bb = BinomBeta(ds_val, a_val, b_val)
    ELEMENTS["distribution_data_source"].data = dict(x=bb.values, y=bb.probs)

    current_y_axis = max(Y_AXIS, max(bb.probs))
    # 
    mean = bb.mean()
    mean_x = np.array([mean, mean])
    lower_stddev, higher_stddev = bb.get_first_stddevs()
    mode = bb.mode()
    lower_stddev_x = np.array([lower_stddev, lower_stddev])
    higher_stddev_x = np.array([higher_stddev, higher_stddev])
    mode_x = np.array([mode[0], mode[0]])
    mode_y = np.array([0, mode[1]])
    ELEMENTS["line_data_source"].data = dict(mean_x=mean_x, lower_stddev_x=lower_stddev_x, higher_stddev_x=higher_stddev_x, mode_x=mode_x, mode_y=mode_y, y=ELEMENTS["line_data_source"].data["y"])
    ELEMENTS["mean_label"].x = mean + (0.025 * bb.n)
    ELEMENTS["lower_stddev_label"].x = lower_stddev - (0.025 * bb.n)
    ELEMENTS["higher_stddev_label"].x = higher_stddev + (0.025 * bb.n)
    # make sure the right first stddev is always visible
    ELEMENTS["plot"].x_range.end = max(bb.n + 5, higher_stddev)
    ELEMENTS["plot"].y_range.end = current_y_axis

    ELEMENTS["parameters_text"].value = '--BBD-alpha {} --BBD-beta {}'.format(a_val, b_val)



def modify_doc(doc):

    # Set up data
    N, a, b = 30, 6, 2
    # compute values using a generator class as used by ddRAGE
    bbgen = BinomBeta(N, a, b)
    # assemble data source, mapping coverage (x axis) versus
    # probability of the coverage value being chosen (y axis)
    distribution_data_source = ColumnDataSource(data=dict(x=bbgen.values, y=bbgen.probs))

    mean = bbgen.mean()
    mean_x = np.array([mean, mean])
    lower_stddev, higher_stddev = bbgen.get_first_stddevs()
    mode = bbgen.mode()
    lower_stddev_x = np.array([lower_stddev, lower_stddev])
    higher_stddev_x = np.array([higher_stddev, higher_stddev])
    
    mode_x = np.array([mode[0], mode[0]])
    mode_y = np.array([0, mode[1]])
    current_y_axis = max(Y_AXIS, max(bbgen.probs))
    line_data_source = ColumnDataSource(
        data=dict(
            mean_x=mean_x,
            lower_stddev_x=lower_stddev_x,
            higher_stddev_x=higher_stddev_x,
            mode_x=mode_x,
            mode_y=mode_y,
            y=np.array([0,current_y_axis]),
            )
        )
    
    # Set up plot
    plot = figure(title="Beta-binomial distribution with moved mean",
                  tools="crosshair,pan,reset,save,wheel_zoom",
                  x_range=[0, max(bbgen.n + 5, higher_stddev)], y_range=[0, current_y_axis])
    
    plot.line('x', 'y', source=distribution_data_source, line_width=3, line_alpha=0.6)
    plot.line('mean_x', 'y', source=line_data_source, line_width=2, line_dash="dashed", line_alpha=0.6, color=MEAN_COLOR)
    plot.line('lower_stddev_x', 'y', source=line_data_source, line_width=1.25, line_dash="dashed", line_alpha=0.6, color=MEAN_COLOR)
    plot.line('mode_x', 'mode_y', source=line_data_source, line_width=2, line_alpha=0.6, color=MEAN_COLOR)
    plot.line('higher_stddev_x', 'y', source=line_data_source, line_width=1.25, line_dash="dashed", line_alpha=0.6, color=MEAN_COLOR)
    
    # Set up widgets
    text = TextInput(title="title", value='Beta-binomial distribution with moved mean')
    step_size = 0.05
    ds_slider = Slider(title="dₛ", value=30, start=1, end=100.0, step=1)
    a_slider = Slider(title="a", value=6.0, start=step_size, end=10.0, step=step_size)
    b_slider = Slider(title="b", value=2.0, start=step_size, end=10.0, step=step_size)
    parameters_text = TextInput(title="RAGE parameters", value='--BBD-alpha {} --BBD-beta {}'.format(a_slider.value, b_slider.value))

    mean_label = Label(x=mean+(0.025*bbgen.n), y=Y_AXIS, text='μ', render_mode='css',
                       text_baseline="top", text_color=MEAN_COLOR)
    lower_stddev_label = Label(x=lower_stddev-(0.025*bbgen.n), y=Y_AXIS-0.05, text='μ - σ', render_mode='css',
                               text_baseline="top", text_align="right", text_color=MEAN_COLOR)
    higher_stddev_label = Label(x=higher_stddev+(0.025*bbgen.n), y=Y_AXIS-0.05, text='μ + σ', render_mode='css',
                                text_baseline="top", text_color=MEAN_COLOR)
    plot.add_layout(mean_label)
    plot.add_layout(higher_stddev_label)
    plot.add_layout(lower_stddev_label)

    # Collect widgestds and datasource in global dict to easily modify them
    ELEMENTS["text"] = text
    ELEMENTS["parameters_text"] = parameters_text
    ELEMENTS["plot"] = plot
    ELEMENTS["ds_slider"] = ds_slider
    ELEMENTS["a_slider"] = a_slider
    ELEMENTS["b_slider"] = b_slider
    ELEMENTS["distribution_data_source"] = distribution_data_source
    ELEMENTS["line_data_source"] = line_data_source
    ELEMENTS["mean_label"] = mean_label
    ELEMENTS["lower_stddev_label"] = lower_stddev_label
    ELEMENTS["higher_stddev_label"] = higher_stddev_label

    # link on_change functions to widgets
    text.on_change('value', update_title)
    for w in [a_slider, b_slider, ds_slider]:
        w.on_change('value', update_data)

    # Set up layouts and add to document
    inputs = widgetbox(text, a_slider, b_slider, ds_slider, parameters_text)
    doc.add_root(row(inputs, plot))
    
    doc.title = "BBD with moved mean"
    

def main_standalone():
    io_loop = IOLoop.current()
    bokeh_app = Application(FunctionHandler(modify_doc))

    server = Server({'/': bokeh_app}, io_loop=io_loop)
    server.start()
    print('Opening Bokeh application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()

if __name__ == '__main__':
    main_standalone()
else:
    modify_doc(curdoc())
