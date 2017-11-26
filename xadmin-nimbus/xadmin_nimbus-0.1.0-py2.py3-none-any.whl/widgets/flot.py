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

from .constants import *


__all__ = [
    "FlotPlugin",
    "FlotView",
    "FlotWidget",
]

logger = logging.getLogger(__name__)


@widget_manager.register
class FlotWidget(ModelBaseWidget):
    widget_type = 'flot'
    description = _('Show models simple chart.')
    template = 'xadmin/widgets/chart.html'
    widget_icon = 'fa fa-bar-chart-o'

    def convert(self, data):
        self.list_params = data.pop('params', {})
        self.chart = data.pop('chart', None)

    def setup(self):
        super(FlotWidget, self).setup()

        self.charts = {}
        self.one_chart = False
        model_admin = self.admin_site._registry[self.model]
        chart = self.chart

        if hasattr(model_admin, 'flot_charts'):
            if chart and chart in model_admin.flot_charts:
                self.charts = {chart: model_admin.flot_charts[chart]}
                self.one_chart = True
                if self.title is None:
                    self.title = model_admin.flot_charts[chart].get('title')
            else:
                self.charts = model_admin.flot_charts
                if self.title is None:
                    self.title = ugettext(
                        "%s Charts") % self.model._meta.verbose_name_plural

    def filte_choices_model(self, model, modeladmin):
        return bool(getattr(modeladmin, 'flot_charts', None)) and \
            super(FlotWidget, self).filte_choices_model(model, modeladmin)

    def get_chart_url(self, name, v):
        return self.model_admin_url('flot', name) + "?" + urlencode(self.list_params)

    def context(self, context):
        context.update({
            'charts': [{"name": name, "title": v['title'], 'url': self.get_chart_url(name, v)} for name, v in self.charts.items()],
        })

    # Media
    def media(self):
        return self.vendor('flot.js', 'xadmin.jquery.flot.stack.js', 'xadmin.plugin.charts.js')


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


class FlotPlugin(BaseAdminPlugin):
    flot_charts = {}

    def init_request(self, *args, **kwargs):
        return bool(self.flot_charts)

    def get_chart_url(self, name, v):
        return self.admin_view.model_admin_url('flot', name) + self.admin_view.get_query_string()

    # Media
    def get_media(self, media):
        return media + self.vendor('flot.js', 'xadmin.jquery.flot.stack.js', 'xadmin.plugin.charts.js')

    # Block Views
    def block_results_top(self, context, nodes):
        context.update({
            'charts': [{"name": name, "title": v['title'], 'url': self.get_chart_url(name, v)} for name, v in self.flot_charts.items()],
        })
        nodes.append(loader.render_to_string('xadmin/blocks/model_list.results_top.charts.html',
                                             context=get_context_dict(context)))


class FlotView(ListAdminView):
    flot_charts = {}

    def get_ordering(self):
        if 'order' in self.chart:
            return self.chart['order']
        else:
            return super(FlotView, self).get_ordering()

    def get_flot_type(self, chart):
        if isinstance(chart, dict):
            flot_type = chart.get("flot_type", FLOT_TYPE_DEFAULT)
            return flot_type if flot_type in FLOT_TYPE_OPTIONS else FLOT_TYPE_DEFAULT
        return FLOT_TYPE_DEFAULT

    def get_flot_ticks(self, flot_type=FLOT_TYPE_DEFAULT):
        ticks = None
        if not self.x_ticks:
            return ticks
        if flot_type in FLOT_SER_LINE:
            ticks = []
            for i, obj in enumerate(self.result_list, start=1):
                xf, attrs, value = lookup_field(self.x_field, obj, self)
                ticks.append((i, smart_unicode(value)))
        return ticks

    def get_flot_datas(self, flot_type=FLOT_TYPE_DEFAULT):
        if flot_type in FLOT_SER_LINE:
            datas = [{"data": [], "label": force_unicode(label_for_field(
                i, self.model, model_admin=self))} for i in self.y_fields]
            for index, obj in enumerate(self.result_list, start=1):
                xf, attrs, value = lookup_field(self.x_field, obj, self)
                for i, yfname in enumerate(self.y_fields):
                    yf, yattrs, yv = lookup_field(yfname, obj, self)
                    if self.x_ticks:
                        value = index
                    datas[i]["data"].append((value, yv))
            return datas
        elif flot_type in FLOT_SER_PIE:
            datas = []
            y_fields = self.y_fields[:1]
            for obj in self.result_list:
                xf, attrs, value = lookup_field(self.x_field, obj, self)
                for i, yfname in enumerate(y_fields):
                    yf, yattrs, yv = lookup_field(yfname, obj, self)
                    # logger.info(u"xf:{} value:{} yf:{} yv:{}".format(xf, value, yf, yv))
                    datas.append(dict(label=value, data=yv))
            return datas
        else:
            return []

    def get_flot_option(self, flot_type=FLOT_TYPE_DEFAULT):
        option = FLOT_TYPE_OPTIONS.get(flot_type, {})
        option = copy.deepcopy(option)
        if flot_type in FLOT_SER_LINE:
            try:
                xfield = self.opts.get_field(self.x_field)
                if type(xfield) in (models.DateTimeField, models.DateField, models.TimeField):
                    option['xaxis'] = {'mode': "time", 'tickLength': 5}
                    if type(xfield) is models.DateField:
                        option['xaxis']['timeformat'] = "%y/%m/%d"
                    elif type(xfield) is models.TimeField:
                        option['xaxis']['timeformat'] = "%H:%M:%S"
                    else:
                        option['xaxis']['timeformat'] = "%y/%m/%d %H:%M:%S"
            except Exception:
                pass

        return option

    @csrf_protect_m
    @filter_hook
    def get(self, request, name):
        if name not in self.flot_charts:
            return HttpResponseNotFound()

        self.chart = self.flot_charts[name]
        flot_type = self.get_flot_type(self.chart)
        logger.info(u"name:{} flot_type:{} chart:{}".format(name, flot_type, self.chart))

        self.x_field = self.chart['x-field']
        y_fields = self.chart['y-field']
        self.y_fields = (y_fields,) if type(y_fields) not in (list, tuple) else y_fields
        self.x_ticks = self.chart.get("x-ticks", False)

        self.make_result_list()
        datas = self.get_flot_datas(flot_type)
        ticks = self.get_flot_ticks(flot_type)
        option = self.get_flot_option(flot_type)

        option.update(self.chart.get('option', {}))
        if 'xaxis' in option:
            option['xaxis']['ticks'] = ticks
        else:
            option['xaxis'] = {'ticks': ticks}
        logger.info(u"option:{}".format(option))

        content = {'data': datas, 'option': option}
        result = json.dumps(content, cls=JSONEncoder, ensure_ascii=False)

        return HttpResponse(result)


site.register_plugin(FlotPlugin, ListAdminView)
site.register_modelview(r'^flot/(.+)/$', FlotView, name='%s_%s_flot')

