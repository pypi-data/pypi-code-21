# -*- coding:utf-8 -*-
from collections import OrderedDict

from django.db.models import Count

from . import modelutils
from . import datautils

__author__ = 'denishuang'


class Measure(object):
    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, verbose_name, cond={}, exclude=False, agg=Count("id"), default=0):
        self.verbose_name = verbose_name
        self.cond = cond
        self.exclude = exclude
        self.agg = agg
        self.default = default
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Measure.creation_counter
        Measure.creation_counter += 1


class Parameter(object):
    def __init__(self, name):
        self.name = name


class DeclarativeColumnsMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Measure):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_fields)
        return super(DeclarativeColumnsMetaclass, mcs).__new__(mcs, name, bases, attrs)


class StatResult(object):
    def __init__(self, fields, verbose_names, data):
        self.fields = fields
        self.verbose_names = verbose_names
        self.data = data

    def as_csv(self, show_header=True, line_spliter=u"\n", field_spliter=u"\t"):
        data = self.data
        if show_header:
            data = [self.verbose_names] + data
        return datautils.list2csv(self.data, line_spliter=line_spliter, field_spliter=field_spliter)

    def __str__(self):
        return self.as_csv()

    def as_html(self, attrs="class='table table-striped table-hover'", row_attrs=""):
        tpl = u"""<table %s>
<thead>
<tr>
<th>%s</th>
<tr>
</thead>
<tbody>
<tr %s>
<td>%s</td>
</tr>
</tbody></table>"""
        return tpl % (attrs,
                      u"</th>\n<th>".join(self.verbose_names),
                      row_attrs,
                      datautils.list2csv(self.data, line_spliter=u"</td>\n</tr>\n<tr %s>\n<td>" % row_attrs,
                               field_spliter=u"</td>\n<td>")
                      )


class StatTableBase(object):
    measure_params_dict = {}

    def __init__(self, query_set):
        self.query_set = query_set

    def stat(self, group):
        r = OrderedDict()
        names = [group]
        verbose_names = [modelutils.get_related_field(self.query_set.model, group).verbose_name]
        for name, field in self.declared_fields.items():
            cond = self.format_measure_condition(name, field)
            if field.exclude == True:
                qset = self.query_set.exclude(**cond)
            else:
                qset = self.query_set.filter(**cond)
            qset = qset.distinct()
            for d in qset.order_by(group).values(group).annotate(measure_value=field.agg):
                g = d[group]
                r.setdefault(g, OrderedDict())
                value = d.get("measure_value")
                r[g][name] = value
            names.append(name)
            verbose_names.append(field.verbose_name)
        data = []
        for k, v in r.items():
            line = [k] + [v.get(name, field.default) for name, field in self.declared_fields.items()]
            data.append(line)
        return StatResult(names, verbose_names, data)

    def format_measure_condition(self, name, measure):
        r = {}
        for k, v in measure.cond.items():
            if isinstance(v, Parameter):
                v = self.measure_params_dict.get(name, {}).get(v.name)
            if callable(v):
                v = v()
            r[k] = v
        return r

    def set_measure_params(self, measure_name, **kwargs):
        self.measure_params_dict[measure_name] = kwargs


StatTable = DeclarativeColumnsMetaclass(str('StatTable'), (StatTableBase,), {})


class StatObject(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, item):
        obj = self.obj
        meta = obj._meta
        fs = item.split("__")
        f = fs[0]
        field = meta.get_field(f)
        if not hasattr(field, "related_model"):
            raise Exception("%s is not a related_model", f)

        relate = getattr(obj, f)
        meta = field.related_model._meta
        f = fs[1]
        field = meta.get_field(f)
        value = self._get_choice(field.choices, fs[2])
        return relate.filter(**{f: value}).count()

    def _get_choice(self, choices, value):
        for k, t in choices:
            if unicode(k) == value or t == value:
                return k
        return value


class StructorStat(object):
    def __init__(self, query_set, fields):
        self.query_set = query_set
        self.fields = fields
        self.model = self.query_set.model

    def stat(self):
        r = OrderedDict()
        for fn in self.fields:
            field = self.model._meta.get_field(fn)
            vname = field.verbose_name
            choices = dict(field.choices)
            data = self.query_set.values(fn).order_by(fn).annotate(count=Count("id"))
            d = OrderedDict()
            for g in data:
                k = g[fn]
                k = choices.get(k, k)
                v = g["count"]
                d[k] = v
            r[vname] = d
        return r


class TimeStat(object):
    def __init__(self, query_set, timeField):
        self.query_set = query_set
        self.timeField = timeField
        self.model = self.query_set.model

    def get_times(self, date_range="今天"):
        from .dateutils import get_next_date, format_the_date
        from datetime import datetime, timedelta
        if date_range == u"今天":
            beginTime = format_the_date()
            endTime = get_next_date(beginTime)
        elif date_range == u"昨天":
            endTime = format_the_date()
            beginTime = get_next_date(endTime, -1)
        elif date_range.startswith(u"近") and date_range.endswith(u"分钟"):
            endTime = datetime.now()
            beginTime = endTime + timedelta(minutes=-int(date_range[1:-2]))
        elif date_range.startswith(u"近") and date_range.endswith(u"小时"):
            endTime = datetime.now()
            beginTime = endTime + timedelta(hours=-int(date_range[1:-2]))
        elif date_range.startswith(u"近") and date_range.endswith(u"天"):
            endTime = get_next_date()
            beginTime = get_next_date(endTime, -int(date_range[1:-1]))
        elif u"至" in date_range:
            drs = date_range.split(u"至")
            beginTime = format_the_date(drs[0])
            endTime = get_next_date(drs[1])
        else:
            raise ValueError(u"日期范围格式不正确:%s" % date_range)

        return beginTime, endTime

    def get_step(self, beginTime, endTime):
        dt = endTime-beginTime
        print dt.seconds,dt.days

        if dt.days>7:
            return 3600*24
        elif dt.days>=1:
            return 3600
        elif dt.seconds <= 36000:
            return 60
        else:
            return 3600

    def stat(self, dateRange=u"今天", funcMap={}):
        r = OrderedDict()
        tfn = "time"
        beginTime, endTime = self.get_times(dateRange)
        step = self.get_step(beginTime, endTime)
        print beginTime, endTime, step
        fn = self.timeField
        qset = self.query_set.filter(**{"%s__gte" % fn: beginTime, "%s__lt" % fn: endTime})
        time_field = {tfn : "floor(unix_timestamp(%s)/%d)*%d" % (fn, step, step)}
        if not funcMap:
            funcMap={"id_count":Count("id")}
        for k,v in funcMap.items():
            qset = qset.extra(time_field).values(tfn).order_by(tfn).annotate(count=v).values_list(tfn, "count")
            data = list(qset) #[[a.strftime("%Y/%m/%d %H:%M:%S"), b] for a, b in qset]
            r[k] = data
        return r
