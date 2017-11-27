# -*- coding: utf-8 -*-
from __future__ import absolute_import

import calendar
import datetime
import decimal
import logging
import copy

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.template import loader
from django.utils.encoding import smart_unicode, smart_str, smart_bytes
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _, ugettext
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.util import lookup_field, label_for_field, force_unicode, json
from xadmin.views import BaseAdminPlugin, ListAdminView
from xadmin.views.base import filter_hook, csrf_protect_m
from xadmin.views.dashboard import ModelBaseWidget, widget_manager

from pyecharts import (
    Bar,
    Line,
    Line3D,
    Pie,
    Gauge,
    Geo,
    Graph,
    Liquid,
    Radar,
    Scatter,
    EffectScatter,
    WordCloud,
    Funnel,
    Map,
    Parallel,
    Polar,
    HeatMap,
    TreeMap,
    Kline,
    Boxplot,

    Style,
    Page,
    Overlap,
    Grid,
    Timeline,
)


from .constants import *


__all__ = [
    "EChartsPlugin",
    "EChartsView",
    "EChartsWidget",
]

logger = logging.getLogger(__name__)


@widget_manager.register
class EChartsWidget(ModelBaseWidget):
    widget_type = 'echarts'
    description = _('Show models echarts chart.')
    template = 'xadmin/widgets/echarts.html'
    widget_icon = 'fa fa-bar-chart-o'

    def convert(self, data):
        self.list_params = data.pop('params', {})
        self.chart = data.pop('chart', None)

    def setup(self):
        super(EChartsWidget, self).setup()

        self.charts = {}
        self.one_chart = False
        model_admin = self.admin_site._registry[self.model]
        chart = self.chart

        if hasattr(model_admin, 'echarts_charts'):
            if chart and chart in model_admin.echarts_charts:
                self.charts = {chart: model_admin.echarts_charts[chart]}
                self.one_chart = True
                if self.title is None:
                    self.title = model_admin.echarts_charts[chart].get('title')
            else:
                self.charts = model_admin.echarts_charts
                if self.title is None:
                    self.title = ugettext("%s Charts") % self.model._meta.verbose_name_plural

    def filte_choices_model(self, model, modeladmin):
        return bool(getattr(modeladmin, 'echarts_charts', None)) and \
            super(EChartsWidget, self).filte_choices_model(model, modeladmin)

    def get_chart_url(self, name, v):
        return self.model_admin_url('echarts', name) + "?" + urlencode(self.list_params)

    def get_chart_height(self, v):
        return v.get("height", "300px")

    def context(self, context):
        context.update({
            'charts': [{
                "name": name,
                "title": v['title'],
                "url": self.get_chart_url(name, v),
                "height": self.get_chart_height(v),
            } for name, v in self.charts.items()],
        })

    # Media
    def media(self):
        return self.vendor('xadmin.echarts.min.js', 'xadmin.echarts.theme.vintage.js', 'xadmin.plugin.widget.echarts.js')


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return calendar.timegm(o.timetuple()) * 1000
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            try:
                return super(JSONEncoder, self).default(o)
            except Exception:
                return smart_unicode(o)


class EChartsPlugin(BaseAdminPlugin):
    echarts_charts = {}

    def init_request(self, *args, **kwargs):
        return bool(self.echarts_charts)

    def get_chart_url(self, name, v):
        return self.admin_view.model_admin_url('echarts', name) + self.admin_view.get_query_string()

    def get_chart_height(self, v):
        return v.get("height", "300px")

    # Media
    def get_media(self, media):
        return media + self.vendor('xadmin.echarts.min.js', 'xadmin.echarts.theme.vintage.js', 'xadmin.plugin.echarts.js')

    # Block Views
    def block_results_top(self, context, nodes):
        context.update({
            'charts': [{
                "name": name,
                "title": v['title'],
                "url": self.get_chart_url(name, v),
            } for name, v in self.echarts_charts.items()],
        })
        nodes.append(loader.render_to_string(
            'xadmin/blocks/model_list.results_top.echarts.html',
            context=get_context_dict(context))
        )


class EChartsView(ListAdminView):
    echarts_charts = {}

    def get_ordering(self):
        if 'order' in self.chart:
            return self.chart['order']
        else:
            return super(EChartsView, self).get_ordering()

    def get_echarts_type(self, chart):
        if isinstance(chart, dict):
            return chart.get("echarts_type", ECHARTS_TYPE_LINE)
        return ECHARTS_TYPE_LINE

    def get_echarts_xfield(self, x_field=None, obj=None, x_format="%Y-%m-%d %H:%M:%S"):
        xf, attrs, value = lookup_field(x_field, obj, self)
        xfield = self.opts.get_field(x_field)
        if x_format and type(xfield) in (models.DateTimeField, models.DateField, models.TimeField):
            if type(xfield) is models.DateField:
                x_format = x_format
            elif type(xfield) is models.TimeField:
                x_format = x_format
            else:
                x_format = x_format
            value = value.strftime(x_format)
        return xf, attrs, value

    def get_echarts_datas(self, echarts_type=FLOT_TYPE_DEFAULT):
        page = Page()
        title = self.chart.get("title", "")
        subtitle = self.chart.get("subtitle", "")
        option = self.chart.get("option", {})
        x_option = option.get(self.x_field, {})
        x_format = x_option.pop("x-format", None)

        style = Style(title=title, subtitle=subtitle, **x_option)
        echart = ""
        if echarts_type == ECHARTS_TYPE_LINE:
            echart = Line(**style.init_style)
            for i, yfname in enumerate(self.y_fields):
                e_label = force_unicode(label_for_field(yfname, self.model, model_admin=self))
                e_attrs = []
                e_values = []
                for index, obj in enumerate(self.result_list, start=1):
                    xf, attrs, value = self.get_echarts_xfield(self.x_field, obj, x_format)
                    yf, yattrs, yv = lookup_field(yfname, obj, self)
                    e_attrs.append(value)
                    e_values.append(yv)
                kwargs = option.get(yfname, {})
                echart.add(e_label, e_attrs, e_values, **kwargs)
        elif echarts_type == ECHARTS_TYPE_BAR:
            echart = Bar(**style.init_style)
            for i, yfname in enumerate(self.y_fields):
                e_label = force_unicode(label_for_field(yfname, self.model, model_admin=self))
                e_attrs = []
                e_values = []
                for index, obj in enumerate(self.result_list, start=1):
                    xf, attrs, value = self.get_echarts_xfield(self.x_field, obj, x_format)
                    yf, yattrs, yv = lookup_field(yfname, obj, self)
                    e_attrs.append(value)
                    e_values.append(yv)
                kwargs = option.get(yfname, {})
                echart.add(e_label, e_attrs, e_values, **kwargs)
        elif echarts_type == ECHARTS_TYPE_PIE:
            echart = Pie(**style.init_style)
            for i, yfname in enumerate(self.y_fields):
                e_label = force_unicode(label_for_field(yfname, self.model, model_admin=self))
                e_attrs = []
                e_values = []
                for index, obj in enumerate(self.result_list, start=1):
                    xf, attrs, value = self.get_echarts_xfield(self.x_field, obj, x_format)
                    yf, yattrs, yv = lookup_field(yfname, obj, self)
                    e_attrs.append(value)
                    e_values.append(yv)
                kwargs = option.get(yfname, {})
                echart.add(e_label, e_attrs, e_values, **kwargs)
        elif echarts_type == ECHARTS_TYPE_LIQUID:
            echart = Liquid(**style.init_style)
            chart = Liquid(u"水球图-单数据", **style.init_style)
            chart.add(u"Liquid", [0.6])

        elif echarts_type == ECHARTS_TYPE_LINE3D:
            echart = Line3D(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_GAUGE:
            echart = Gauge(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_GEO:
            echart = Geo(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_GRAPH:
            echart = Graph(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_RADAR:
            echart = Radar(**style.init_style)
            config = self.chart.get("config", {})
            echart.config(**config)

        elif echarts_type == ECHARTS_TYPE_SCATTER:
            echart = Scatter(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_WORDCLOUD:
            echart = WordCloud(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_FUNNEL:
            echart = Funnel(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_MAP:
            echart = Map(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_PARALLEL:
            echart = Parallel(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_POLAR:
            echart = Polar(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_HEATMAP:
            echart = HeatMap(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_TREEMAP:
            echart = TreeMap(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_BOXPLOT:
            echart = Boxplot(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_KLINE:
            echart = Kline(**style.init_style)

        elif echarts_type == ECHARTS_TYPE_TIMELINE:
            echart = Timeline(**x_option)

        elif echarts_type == ECHARTS_TYPE_OVERLAp:
            echart = Overlap(**option)

        elif echarts_type == ECHARTS_TYPE_GRID:
            echart = Grid(**option)

        elif echarts_type == ECHARTS_TYPE_PAGE:
            echart = Page()

        if not echart:
            return copy.deepcopy(DEMO)
            # return ""
        # page.add(echart)
        return echart.options

    @csrf_protect_m
    @filter_hook
    def get(self, request, name):
        if name not in self.echarts_charts:
            return HttpResponseNotFound()

        self.chart = self.echarts_charts[name]
        echarts_type = self.get_echarts_type(self.chart)
        logger.info(u"name:{} echarts_type:{} chart:{}".format(name, echarts_type, self.chart))

        self.x_field = self.chart['x-field']
        y_fields = self.chart['y-field']
        self.y_fields = (y_fields,) if type(y_fields) not in (list, tuple) else y_fields

        self.make_result_list()
        content = self.get_echarts_datas(echarts_type)
        result = json.dumps(content, cls=JSONEncoder, ensure_ascii=False)

        logger.info(u"option:{}".format(result))
        return HttpResponse(result)


site.register_plugin(EChartsPlugin, ListAdminView)
site.register_modelview(r'^echarts/(.+)/$', EChartsView, name='%s_%s_echarts')

