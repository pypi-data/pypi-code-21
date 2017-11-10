import plotly.graph_objs as graphs
from clarusui.chart import Chart


class WorldMap(Chart):
    def __init__(self, response, **options):
        super(WorldMap, self).__init__(response, **options)
        # self.layout['geo'] = dict(showframe=False, resolution=50, projection=dict(type=self.options.pop('projection', 'equirectangular')))
        self.layout['geo'] = dict(bgcolor='rgba(0,0,0,0)', showframe=False,
                                  projection=dict(type=self.options.pop('projection', 'equirectangular')))
        self.layout['margin'] = dict(l=0, r=0, t=0, b=0)

    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers():
            if (self.colFilter == None or colHeader in self.colFilter):
                data.append(graphs.Choropleth(locations=self._get_xaxis(colHeader), z=self._get_yaxis(colHeader),
                                              **self._get_options()))
        return data
    
    def set_font(self, style):
        super().set_font(style)
        self.layout.update({'geo' : dict(bgcolor='rgba(0,0,0,0)', showframe=False,
                                  projection=dict(type=self.options.pop('projection', 'equirectangular')))})
        
    
    def _get_options(self):
        options = super(WorldMap, self)._get_options()
        options['locationmode'] = 'country names'
        return options
