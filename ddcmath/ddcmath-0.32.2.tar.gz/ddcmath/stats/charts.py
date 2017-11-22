#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.

# References : https://www.deming.org/
# http://www.contesolutions.com/Western_Electric_SQC_Handbook.pdf
# http://www.fr-deming.org/WECSQ.pdf

import pandas as pd
import numpy as np
from math import fabs
from bokeh.plotting import figure
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool, BoxAnnotation
from bokeh.models.layouts import Column, Row

from collections import OrderedDict

class XandRChart():
    def build_chart(self, chart = 'r'):
        if chart is 'r':
            title = 'R Chart'
            df = self._df_R.reset_index()
        else:
            title = 'Xb Chart'
            df = self._df_X.reset_index()
        TOOLS = "resize,pan,box_zoom,wheel_zoom,reset"
        hover = HoverTool(names=["x", "values"])
        p = figure(plot_width=400, plot_height=300, title=title, tools = [hover,TOOLS])
        # add a line renderer
        src = ColumnDataSource(
            data=dict(
            x = df['index'],
            val = df['values'],
            up = df['upper limit'],
            low = df['lower limit'],
            mean = df['mean'],
            sigma1 = df['sigma1'],
            sigma2 = df['sigma2'],
            minus_sigma1 = df['sigma-1'],
            minus_sigma2 = df['sigma-2'],
            time = df['index'].apply(str)
            ))
        x_src = ColumnDataSource(
            data=dict(
            x = df['index'][df['x'] == True],
            val = df['values'][df['x'] == True],
            time = df['index'].apply(str)
            ))

        strat_src = ColumnDataSource(
            data=dict(
            x = df['index'][df['x'] == True],
            val = df['values'][df['stratification'] == True],
            time = df['index'].apply(str)
            ))        

        mix_src = ColumnDataSource(
            data=dict(
            x = df['index'][df['x'] == True],
            val = df['values'][df['mixture'] == True],
            time = df['index'].apply(str)
            ))
            
        hover = p.select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ('timestamp', '@time'),
            ('value', '@val'),
        ]) 
        
        zone_c_1 = BoxAnnotation(plot=p, bottom=df['sigma2'][0], top=df['sigma3'][0], fill_alpha=0.1, fill_color='red')
        zone_b_1 = BoxAnnotation(plot=p, bottom=df['sigma1'][0], top=df['sigma2'][0], fill_alpha=0.1, fill_color='yellow')        
        zone_a_1 = BoxAnnotation(plot=p, bottom=df['mean'][0], top=df['sigma1'][0], fill_alpha=0.1, fill_color='green')        
        zone_a_2 = BoxAnnotation(plot=p, bottom=df['sigma-1'][0], top=df['mean'][0], fill_alpha=0.1, fill_color='green')        
        zone_b_2 = BoxAnnotation(plot=p, bottom=df['sigma-2'][0], top=df['sigma-1'][0], fill_alpha=0.1, fill_color='yellow')        
        zone_c_2 = BoxAnnotation(plot=p, bottom=df['sigma-3'][0], top=df['sigma-2'][0], fill_alpha=0.1, fill_color='red')
        
        p.renderers.extend([zone_c_1, zone_b_1, zone_a_1, zone_a_2, zone_b_2, zone_c_2])
        
        p.line('x', 'up', source = src, line_width=2, line_color='red')
        p.line('x', 'low', source = src, line_width=2, line_color='red')
        p.line('x', 'mean', source = src, line_width=2)
        # x
        p.line('x', 'sigma1', source = src, line_dash=[4, 4], line_color="green", line_width=2, alpha=0.5)
        p.line('x', 'sigma2', source = src, line_dash=[4, 4], line_color="orange", line_width=2, alpha=0.5)
        p.line('x', 'minus_sigma1', source = src, line_dash=[4, 4], line_color="green", line_width=2, alpha=0.5)
        p.line('x', 'minus_sigma2', source = src, line_dash=[4, 4], line_color="orange", line_width=2, alpha=0.5)
        p.x('x', 'val', source = x_src, name = "x", size=25, line_width=5, color="red")
        p.triangle('x', 'val', source = strat_src, size = 25, line_width=5, color="black")        
        p.triangle('x', 'val', source = mix_src, size = 25, line_width=5, color="black")        
                
        #p.line('x', 'val', source = src, name = "values", line_width=2, line_color='blue')
        p.circle('x', 'val', source = src, size=10, color='blue')
        
        #show(p) 
        return p
  

class IndividualChart():
    def build_chart(self):
        TOOLS = "resize,pan,box_zoom,wheel_zoom,reset"
        hover = HoverTool(names=["x", "values"])
        p = figure(plot_width=400, plot_height=300, x_axis_type="datetime", title='Moving Range', tools = [hover,TOOLS])
        df = self.result.reset_index()
        # add a line renderer
        src = ColumnDataSource(
            data=dict(
            x = df['index'],
            val = df['values'],
            up = df['upper limit'],
            low = df['lower limit'],
            mean = df['mean'],
            sigma1 = df['sigma1'],
            sigma2 = df['sigma2'],
            minus_sigma1 = df['sigma-1'],
            minus_sigma2 = df['sigma-2'],
            time = df['index'].apply(str)
            ))
        x_src = ColumnDataSource(
            data=dict(
            x = df['index'][df['x'] == True],
            val = df['values'][df['x'] == True],
            time = df['index'].apply(str)
            ))

        strat_src = ColumnDataSource(
            data=dict(
            x = df['index'][df['x'] == True],
            val = df['values'][df['stratification'] == True],
            time = df['index'].apply(str)
            ))        

        mix_src = ColumnDataSource(
            data=dict(
            x = df['index'][df['x'] == True],
            val = df['values'][df['mixture'] == True],
            time = df['index'].apply(str)
            ))
            
        hover = p.select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ('timestamp', '@time'),
            ('value', '@val'),
        ]) 
        
        zone_c_1 = BoxAnnotation(plot=p, bottom=df['sigma2'][0], top=df['sigma3'][0], fill_alpha=0.1, fill_color='red')
        zone_b_1 = BoxAnnotation(plot=p, bottom=df['sigma1'][0], top=df['sigma2'][0], fill_alpha=0.1, fill_color='yellow')        
        zone_a_1 = BoxAnnotation(plot=p, bottom=df['mean'][0], top=df['sigma1'][0], fill_alpha=0.1, fill_color='green')        
        zone_a_2 = BoxAnnotation(plot=p, bottom=df['sigma-1'][0], top=df['mean'][0], fill_alpha=0.1, fill_color='green')        
        zone_b_2 = BoxAnnotation(plot=p, bottom=df['sigma-2'][0], top=df['sigma-1'][0], fill_alpha=0.1, fill_color='yellow')        
        zone_c_2 = BoxAnnotation(plot=p, bottom=df['sigma-3'][0], top=df['sigma-2'][0], fill_alpha=0.1, fill_color='red')
        
        p.renderers.extend([zone_c_1, zone_b_1, zone_a_1, zone_a_2, zone_b_2, zone_c_2])
        
        p.line('x', 'up', source = src, line_width=2, line_color='red')
        p.line('x', 'low', source = src, line_width=2, line_color='red')
        p.line('x', 'mean', source = src, line_width=2)
        # x
        p.line('x', 'sigma1', source = src, line_dash=[4, 4], line_color="green", line_width=2, alpha=0.5)
        p.line('x', 'sigma2', source = src, line_dash=[4, 4], line_color="orange", line_width=2, alpha=0.5)
        p.line('x', 'minus_sigma1', source = src, line_dash=[4, 4], line_color="green", line_width=2, alpha=0.5)
        p.line('x', 'minus_sigma2', source = src, line_dash=[4, 4], line_color="orange", line_width=2, alpha=0.5)
        p.x('x', 'val', source = x_src, name = "x", size=25, line_width=5, color="red")
        p.triangle('x', 'val', source = strat_src, size = 25, line_width=5, color="black")        
        p.triangle('x', 'val', source = mix_src, size = 25, line_width=5, color="black")        
                
        #p.line('x', 'val', source = src, name = "values", line_width=2, line_color='blue')
        p.circle('x', 'val', source = src, size=10, color='blue')
        
        #show(p) 
        return p

class DistributionChart():
    def build_chart(serie):
        TOOLS = "resize,hover,pan,box_zoom,wheel_zoom,reset"
        p = figure(plot_width=400, plot_height=300, title='Distribution', tools = TOOLS)
        records = serie.dropna()
        min_val = np.min(records)
        max_val = np.max(records)
        bins = max(int(fabs((max_val-min_val)/0.1)),1)
        hist, edges = np.histogram(records, density=False, bins=20)
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
                fill_color="#036564", line_color="#033649", alpha=0.5)
        p.line(edges,hist, line_width=2, line_color='blue')
        return p

class Dashboard():        
    def build_dashboard(r_chart, x_chart, ind_chart, dist_chart):
        #r = rchart
        #Xb = XbChart
        #mr = MovingRange(serie)
        #show()
        return (Column(Row(r_chart, x_chart), Row(ind_chart,dist_chart)))