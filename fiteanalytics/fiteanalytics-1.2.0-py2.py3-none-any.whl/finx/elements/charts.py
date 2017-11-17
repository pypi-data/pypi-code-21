#! python
"""
Fite Analytics LLC
purpose: collection of charts in easy-to-use functions
"""
import bqplot as bqp
import matplotlib.pyplot as plt

def simple(dataframe):
    dataframe.plot()
    plt.show()
    return None

def line_chart(df, title):
    x = bqp.OrdinalScale()
    y = bqp.LinearScale()
    line = bqp.Lines(x=df.index, y=df[df.columns[0]], scales={'x': x, 'y': y})
    ax_x = bqp.Axis(scale=x, grid_lines='solid', label='X')
    ax_y = bqp.Axis(scale=y, orientation='vertical', tick_format='0.2f', grid_lines='solid', label='Y')
    return bqp.Figure(marks=[line], axes=[ax_x, ax_y], title=title, legend_location='bottom-right')

def bar_chart(df, title):
    x = bqp.OrdinalScale()
    y = bqp.LinearScale()
    bar = bqp.Bars(x=df.index, y=df[df.columns[0]], scales={'x': x, 'y': y}, type='stacked')
    ax_x = bqp.Axis(scale=x, grid_lines='solid', label='X')
    ax_y = bqp.Axis(scale=y, orientation='vertical', tick_format='0.2f', grid_lines='solid', label='Y')
    return bqp.Figure(marks=[bar], axes=[ax_x, ax_y], title=title, legend_location='bottom-right')

def help():
    return 'Here is some information about our charting functions!'
