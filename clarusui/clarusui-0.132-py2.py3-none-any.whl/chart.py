import plotly.graph_objs as graphs
import plotly.offline as py
from clarusui.layout import Element
from abc import ABCMeta, abstractmethod

class Chart(Element):

    __metaclass__ = ABCMeta
    
    def __init__(self, response, **options):
        super(Chart, self).__init__(response, **options)
        self.layout     = dict()
        self.layout['height'] = 'auto'
        #self.options    = dict(options)
        self.colFilter  = self.options.pop('colFilter', None)
        if self.colFilter is not None:
            self.colFilter  = self.colFilter.split(',')
        
    def set_font(self, style):
        font = dict()
        axis = dict()
        if style is not None:
            font['color'] = style.getFontColour()
            font['family'] = style.getFontFamily()
            self.layout['font'] = font
            
            #axis['linecolor'] = style.getFontColour()
            #axis['zerolinecolor'] = style.getFontColour()
            #self.layout['xaxis'] = axis
            #self.layout['yaxis'] = axis
    
    def _get_layout(self):
        return self.layout
    
    def set_layout(self, layout):
        self.layout = layout
        
    def set_title(self, title):
        self.layout.update({'title' : title})
        
    def set_xaxis(self, axis):
        if axis is not None:
            self.layout.update({'xaxis' : dict(title = axis)})
        
    def set_yaxis(self, axis):
        if axis is not None:
            self.layout.update({'yaxis' : dict(title = axis)})

    def set_bgcolour(self, colour):
        self.layout.update({'paper_bgcolor' : colour})
        self.layout.update({'plot_bgcolor' : colour})

    def toDiv(self):
        return self._plot('div')

#    def toFile(self):
#        return self._plot('file')

    def _plot(self, output_type):
        figure = graphs.Figure(data=self._get_plot_data(), layout=self._get_layout())
        includeJS = True if output_type=='file' else False
        return py.offline.plot(figure_or_data=figure, show_link=False, output_type=output_type, include_plotlyjs=includeJS, config={'displayModeBar':False})
    
    def _get_xaxis(self, col):
        return self.response.get(col) if self.isHorizontal() else self.response.get_row_headers()

    def _get_yaxis(self, col):
        return self.response.get_row_headers() if self.isHorizontal() else self.response.get(col)

    def isHorizontal(self):
        return self.options.get('orientation')=='h'
    
    def _get_options(self):
        chart_options = dict(self.options)
        self.set_title(chart_options.pop('title', None))
        self.set_xaxis(chart_options.pop('xlabel', None))
        self.set_yaxis(chart_options.pop('ylabel', None))
        bgcolour = chart_options.pop('bgcolour', None)
        if (bgcolour is not None):
            self.set_bgcolour(bgcolour)
        #self.add_custom_css({"background-color":bgcolour})
        return chart_options
               
    @abstractmethod        
    def _get_plot_data(self):
        pass

class PieChart(Chart):

    def __init__(self, response, **options):
        super(PieChart, self).__init__(response, **options)
        
    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers():
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Pie(labels=self._get_xaxis(colHeader), values=self._get_yaxis(colHeader), name=colHeader, **self._get_options()))                    
        return data
        
class DonutChart(PieChart):
        
    def __init__(self, response, **options):
        super(DonutChart, self).__init__(response, **options)
        
    def _get_options(self):
        options = super(PieChart, self)._get_options()     
        options['hole'] = options.pop('hole', .5)
        return options
            
    def _get_layout(self):
        layout =  super(DonutChart, self)._get_layout()        
        layout['annotations'] = [dict(text=layout.pop('title', None), showarrow=False, font={'size':15})]
        return layout
   
class BarChart(Chart):

    def __init__(self, response, **options):
        super(BarChart, self).__init__(response, **options)
        
    def _get_options(self):
        bar_options =  super(BarChart, self)._get_options()
        colour = self._get_rgbcolour(bar_options.pop('colour', None))
        lineColour = self._get_rgbcolour(bar_options.pop('lineColour', colour))
        lineWidth = bar_options.pop('lineWidth', '1')
        if (colour is not None):
            bar_options['marker'] = dict(color=colour, line=dict(color=lineColour, width=lineWidth))
        return bar_options
        
    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers():
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Bar(x=self._get_xaxis(colHeader), y=self._get_yaxis(colHeader), name=colHeader, **self._get_options()))                 
        return data
        
class StackedBarChart(BarChart):

    def __init__(self, response, **options):
        super(StackedBarChart, self).__init__(response, **options)
        
    def _get_layout(self):
        bar_layout =  super(StackedBarChart, self)._get_layout()
        bar_layout['barmode'] = 'stack'
        return bar_layout
    
class LineChart(Chart):

    def __init__(self, response, **options):
        super(LineChart, self).__init__(response, **options)

    def _get_options(self):
        line_options = super(LineChart, self)._get_options()
        lineColour = self._get_rgbcolour(line_options.pop('lineColour', None))
        lineWidth = line_options.pop('lineWidth', '1')
        interpolate = line_options.pop('interpolate', 'linear')
        line = line_options.pop('line', 'solid')
        if (line!='solid') or (lineColour is not None) or (lineWidth!='1') or (interpolate!='linear'):
            line_options['line'] = dict(color=lineColour, width=lineWidth, dash=line, shape=interpolate);
        return line_options        

    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers():
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Scatter(x=self._get_xaxis(colHeader), y=self._get_yaxis(colHeader), name=colHeader, **self._get_options()))                 
        return data
    
class AreaChart(LineChart):

    def __init__(self, response, **options):
        super(AreaChart, self).__init__(response, **options)
    
    def _get_options(self):
        line_options =  super(AreaChart, self)._get_options()
        line_options['fill'] = 'tonexty'
        colour = self._get_rgbcolour(line_options.pop('colour', None))
        if colour is not None:
            line_options['fillcolor'] = colour
        return line_options
    
