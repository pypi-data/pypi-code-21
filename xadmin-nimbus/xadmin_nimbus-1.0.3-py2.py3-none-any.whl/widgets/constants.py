# -*- coding: utf-8 -*-


FLOT_TYPE_LINE = "line"
FLOT_TYPE_AREA = "area"
FLOT_TYPE_BAR = "bar"
FLOT_TYPE_STEPS = "steps"
FLOT_TYPE_LINE_STACK = "line_stack"
FLOT_TYPE_AREA_STACK = "area_stack"
FLOT_TYPE_BAR_STACK = "bar_stack"
FLOT_TYPE_STEPS_STACK = "steps_stack"

FLOT_TYPE_PIE = "pie"
FLOT_TYPE_DONUT = "donut"
FLOT_TYPE_PIE_COMBINE = "pie_combine"
FLOT_TYPE_DONUT_COMBINE = "donut_combine"

FLOT_TYPE_DEFAULT = FLOT_TYPE_LINE
FLOT_SER_LINE = [
    FLOT_TYPE_LINE,
    FLOT_TYPE_AREA,
    FLOT_TYPE_BAR,
    FLOT_TYPE_STEPS,
    FLOT_TYPE_LINE_STACK,
    FLOT_TYPE_AREA_STACK,
    FLOT_TYPE_BAR_STACK,
    FLOT_TYPE_STEPS_STACK,
]
FLOT_SER_PIE = [
    FLOT_TYPE_PIE,
    FLOT_TYPE_DONUT,
    FLOT_TYPE_PIE_COMBINE,
    FLOT_TYPE_DONUT_COMBINE,
]

FLOT_BAR_WIDTH = 0.5

FLOT_TYPE_OPTIONS = {
    FLOT_TYPE_LINE: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'lines': {
            'show': True,
            'fill': False,
        },
        'points': {
            'show': True,
        },
    },
    FLOT_TYPE_AREA: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'lines': {
            'show': True,
            'fill': True,
        },
        'points': {
            'show': True,
        },
    },
    FLOT_TYPE_BAR: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'xaxis': {
            'mode': "categories",
            'tickLength': 0,
        },
        'series': {
            'bars': {
                'show': True,
                'barWidth': FLOT_BAR_WIDTH,
                'align': 'center',
            },
        },
    },

    FLOT_TYPE_STEPS: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
            # 'margin': {
            #     'top': 20,
            #     'left': 20,
            #     'bottom': 20,
            #     'right': 20,
            # },
        },
        'series': {
            'stack': False,
            'lines': {
                'show': True,
                'fill': False,
                'steps': True,
            },
            'bars': {
                'show': False,
                'barWidth': FLOT_BAR_WIDTH,
                'align': 'center',
            },
        },
    },

    FLOT_TYPE_PIE: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'pie': {
                'show': True,
                'label': {
                    'show': True,
                },
            },
        },
    },
    FLOT_TYPE_DONUT: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'pie': {
                'show': True,
                'radius': 0.8,
                'innerRadius': 0.4,
                # 'tilt': 0.5,
                'label': {
                    'show': True,
                    'radius': 1,
                    # 'threshold': 0.1,
                },
                # "combine": {
                #     'color': '#999',
                #     'threshold': 0.1,
                # },
            },
        },
    },

    FLOT_TYPE_PIE_COMBINE: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'pie': {
                'show': True,
                'label': {
                    'show': True,
                },
                "combine": {
                    'color': '#999',
                    'threshold': 0.1,
                },
            },
        },
    },

    FLOT_TYPE_DONUT_COMBINE: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'pie': {
                'show': True,
                'radius': 0.8,
                'innerRadius': 0.4,
                # 'tilt': 0.5,
                'label': {
                    'show': True,
                    'radius': 1,
                    # 'threshold': 0.1,
                },
                "combine": {
                    'color': '#999',
                    'threshold': 0.1,
                },
            },
        },
    },

    FLOT_TYPE_LINE_STACK: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'stack': True,
            'lines': {
                'show': True,
                'fill': False,
                'steps': False,
            },
            'bars': {
                'show': False,
                'barWidth': FLOT_BAR_WIDTH,
                'align': 'center',
            },
        },
    },

    FLOT_TYPE_AREA_STACK: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'stack': True,
            'lines': {
                'show': True,
                'fill': True,
                'steps': False,
            },
            'bars': {
                'show': False,
                'barWidth': FLOT_BAR_WIDTH,
                'align': 'center',
            },
        },
    },

    FLOT_TYPE_BAR_STACK: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'stack': True,
            'lines': {
                'show': False,
                'fill': True,
                'steps': False,
            },
            'bars': {
                'show': True,
                'barWidth': FLOT_BAR_WIDTH,
                'align': 'center',
            },
        },
    },

    FLOT_TYPE_STEPS_STACK: {
        'grid': {
            'borderWidth': 1,
            'hoverable': True,
            'clickable': True,
            'autoHighlight': True,
        },
        'series': {
            'stack': True,
            'lines': {
                'show': True,
                'fill': True,
                'steps': True,
            },
            'bars': {
                'show': False,
                'barWidth': FLOT_BAR_WIDTH,
                'align': 'center',
            },
        },
    },
}

DEMO = {
    "title": {
        "text": '异步数据加载示例 '
    },
    "tooltip": {},
    "legend": {
        "data": ['销量']
    },
    "xAxis": {
        "data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
    },
    "yAxis": {},
    "series": [{
        "name": '销量',
        "type": 'bar',
        "data": [5, 20, 36, 10, 10, 20]
    }]
}

ECHARTS_TYPE_LINE = "line"
ECHARTS_TYPE_BAR = "bar"
ECHARTS_TYPE_PIE = "pie"
ECHARTS_TYPE_LIQUID = "liquid"
ECHARTS_TYPE_LINE3D = "line3d"
ECHARTS_TYPE_GAUGE = "gauge"
ECHARTS_TYPE_GEO = "geo"
ECHARTS_TYPE_GEOLINES = "geolines"
ECHARTS_TYPE_GRAPH = "graph"
ECHARTS_TYPE_RADAR = "radar"
ECHARTS_TYPE_SCATTER = "scatter"
ECHARTS_TYPE_WORDCLOUD = "wordcloud"
ECHARTS_TYPE_MAP = "map"
ECHARTS_TYPE_FUNNEL = "funnel"
ECHARTS_TYPE_PARALLEL = "parallel"
ECHARTS_TYPE_POLAR = "polar"
ECHARTS_TYPE_HEATMAP = "heatmap"
ECHARTS_TYPE_TREEMAP = "treemap"
ECHARTS_TYPE_BOXPLOT = "boxplot"
ECHARTS_TYPE_KLINE = "kline"
ECHARTS_TYPE_TIMELINE = "timeline"
ECHARTS_TYPE_OVERLAp = "overlap"
ECHARTS_TYPE_GRID = "grid"
ECHARTS_TYPE_PAGE = "page"

