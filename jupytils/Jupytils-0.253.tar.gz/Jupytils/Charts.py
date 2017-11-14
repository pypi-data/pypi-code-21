from __future__ import absolute_import

"""Functions to quickly display charts in a Notebook.
"""

import string
import random
import json
import copy

from IPython.core import getipython
from IPython.core.display import display, HTML
import numpy as np;

# Note that Highstock includes all Highcharts features.
HIGHCHARTS_SCRIPTS = """
<script src="//code.highcharts.com/stock/highstock.js"></script>
<script src="//code.highcharts.com/highcharts-more.js"></script>
<script src="//code.highcharts.com/modules/exporting.js"></script>
"""


def load_highcharts():
    return display(HTML(HIGHCHARTS_SCRIPTS))

# Automatically insert the script tag into your Notebook.
# Call when you import this module.
if 'IPKernelApp' in getipython.get_ipython().config:
    load_highcharts()



def PlotHCts(df, x, cols=[], div=None, title='', subtitle='', yTitle='',xTitle='', num=1000000,
          onClick='function(){g=this;console.log(g.index, g.y, g.x)}',
            animation='true'):
    TS='''
<script>
Highcharts.chart('CHART_DIV', {
    chart: { type: 'line' ,  zoomType: 'x'},
    title: { text: 'CHART_TITLE' , zoomType:'xy' },
    subtitle: { text: 'CHART_SUB_TITLE' },
    xAxis: {type: 'datetime'
    },
    yAxis: {
        title: { text: 'CHART_Y_AXIS_TITLE'}
    },
    plotOptions: {
        line: {
            animation: CHART_ANIMATION,
            dataLabels: {  enabled: false  },
            enableMouseTracking: true,
            lineWidth: 0.5,
            marker: {radius: 3}
            },
            
            series: {
                point: {
                    events: {
                        click: CLICK_FUNCTION
                    }
                }
            }
        },
        DATA

});
</script>
'''
    
    ts ="";
    if ( div is None ):
        div = 'chart_' + str(np.random.randint(1000000))
        ts = '<div id="{}" style="height:200px"></div>\n'.format(div)
        
    if (type(x) == str):
        xa = df[x]
    elif (type(x) == int):
        xa = df[df.columns[x]]
    else: #(type(x) == pd.core.series.Series)
        xa = x
        
    if (len(xa) <=0 ): return;
    if (xa.astype(int)[0] > 1000000000000000000):
        dt=(xa.astype(int)/1000000)[0:num]
    elif (xa.astype(int)[0] > 1000000000000000):
        dt=(xa.astype(int)/1000)[0:num]
    else:
        dt = xa;
        
    dt = [int(c) for c in dt]
    dd=[]
    
    
    for c in cols:
        if ( type(c) == str):
            d=list(df[c].values[0:num])
            cn=c
        elif( type(c) == int ):
            cn=df.columns[c]
            d=list(df[cn].values[0:num])
        else:
            cn="List"
            d=c;
            
        dat=list(zip(dt, d))
        dd.append({'name': cn, 'data': dat })

    s = 'series: ' + pd.io.json.dumps(dd) +""
    ts= ts + TS.replace('DATA',s)
    ts=ts.replace('CHART_DIV', div)
    ts=ts.replace('CHART_TITLE', title)
    ts=ts.replace('CHART_SUB_TITLE', subtitle)
    ts=ts.replace('CHART_Y_AXIS_TITLE', yTitle)
    ts=ts.replace('CLICK_FUNCTION', onClick)
    ts=ts.replace('CHART_ANIMATION', animation)

    display(HTML(ts))    
    return ts;

#ts=PlotHCts(df, x=df.sdttm, cols='so2_max precipitation_max'.split(), div='chart1',num=10)
#ts=plotTSHC(df, x=df.sdttm, cols=[23,21,df.temperature_diff, random.random(1999)], title="PEF Values", div='chart1',num=100000, onClick=onClick)
