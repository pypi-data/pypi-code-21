import pandas as pd
import numpy as np
import plotly
from plotly.graph_objs import Scatter, Layout
from os import listdir
from os.path import isfile, join, basename
from backtester.metrics.metrics import Metrics
from backtester.logger import *

'''
Usage(to test in console):
>> pip install plotly
>> python
>> from plotter import plot
>> plot(r'./runLogs/runLog_20170613_201741', []) # plots every file in directory
>> plot(r'./runLogs/runLog_20170613_201741', ['ADBE_features.csv']) # ignores the files listed here
>> plot(r'./runLogs/runLog_20170613_201741/ADBE_features.csv', []) # plots only ADBE_features
Replace the appropriate timeStamps

TODO: 1) Support excluding columns for each files.
      2) Cleanup the html files generated from plotting/dont regenerate and recycle ones present.
      3) Provide a selector GUI to chose the files.
'''

def generateGraph(df, fileName, stats, benchmark_pnl):
    layout = dict(
        title=stats,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(count=5,
                         label='5y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(),
            type='date'
        )
    )
    plot_data = {
        "data": [],
        "layout": layout
    }
    for col in df.columns[1:]:
        plot_data['data'] += [Scatter(x=df.index, y=df[col], name=col)]
    if benchmark_pnl is not None:
        plot_data['data'] += [Scatter(x=df.index,
                                      y=100 * benchmark_pnl, name='Benchmark (%)')]
    plotly.offline.plot(plot_data, filename=fileName + ".html")
