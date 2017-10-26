# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

from .exceptions import ParameterError
from .result import Response, AsyncResponse
from .utils import map_udf, map_order_dir, check_string_type, cast, \
    make_alias, ensure_list, guess_ds_type


class DataSource(object):
    def __init__(self, ds_type=None, ds_dsn=None, table=None):
        if ds_dsn is None or table is None:
            raise TypeError('ds_dsn and table is required')

        self.ds_dsn = ds_dsn
        self.table = table

        self.ds_type = ds_type
        if not self.ds_type:
            self.ds_type = guess_ds_type(self.ds_dsn)

    @classmethod
    def from_scene_ds(cls, ds_obj):
        """传入 Scene 的 datasource 构造一个 DataSource"""
        return cls(ds_type=ds_obj.data_source_type,
                   ds_dsn=ds_obj.data_source_database.dsn,
                   table=ds_obj.data_source_name)

    @classmethod
    def from_dict(cls, d):
        return cls(d.get('ds_type'), d['ds_dsn'], d['table'])

    def to_dict(self):
        return {
            'ds_type': self.ds_type,
            'ds_dsn': self.ds_dsn,
            'table': self.table
        }

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{}<{}, {}>'.format(self.__class__.__name__, self.ds_dsn, self.table)


class Query(object):
    response_class = Response

    def __init__(self, ds):
        """构建一个实时/同步查询

        :param ds: pypump 里的 `DataSource` 对象或 Scene 里的 DataSourceMixin 对象
        """
        if not isinstance(ds, DataSource):
            try:
                ds = DataSource.from_scene_ds(ds)
            except Exception as e:
                raise ValueError('ds should be "DataSource" object or "DataSourceMixin" object')

        self._ds = ds
        self._metrics = []
        self._filters = []
        self._groupby = []
        self._orderby = []
        self._splitby = {}
        self._limit = None

    def metrics(self, metrics_list):
        """添加多个 metric

        :param metrics_list: 每个 metric 是 {"field": "a", "aggregation": "max", "alias": "max_a"} 结构的 dict
            如果 `aggregation` 字段不为空, `alias` 字段不存在或为空, 将自动添加为 `max__a`
        :type metrics_list: list
        """
        for metric in ensure_list(metrics_list):
            self._add_metric(metric)
        return self

    def metric(self, field, aggregation='', alias=''):
        """添加一个 metric, 至少需要指定 field 字段

        :param field: 字段名, 必需
        :param aggregation: 聚合函数, 可为空, 支持 max, min, count, sum, avg, cummax, cummin, cumcount, cumsum 等
        :param alias: 别名, 用于返回值字典的 key, 如果 `aggregation` 不为空且 `alias` 为空, 将自动设置为 `agg__field` 的格式
        """
        self._add_metric({'field': field, 'aggregation': aggregation, 'alias': alias})
        return self

    def max(self, field, alias=''):
        """添加一个 MAX 查询"""
        return self.metric(field, 'max', alias)

    def min(self, field, alias=''):
        """添加一个 MIN 查询"""
        return self.metric(field, 'min', alias)

    def sum(self, field, alias=''):
        """添加一个 SUM 查询"""
        return self.metric(field, 'sum', alias)

    def avg(self, field, alias=''):
        """添加一个 AVG 查询"""
        return self.metric(field, 'avg', alias)

    def count(self, field, alias=''):
        """添加一个 COUNT 查询"""
        return self.metric(field, 'count', alias)

    def count_distinct(self, field, alias=''):
        """添加一个 COUNT DISTINCT 聚合查询"""
        return self.metric(field, 'count(distinct)', alias)

    def distinct(self, field, alias=''):
        """添加 DISTINCT 查询"""
        return self.metric('distinct({})'.format(field), '', alias or field)

    def cumsum(self, field, alias=''):
        """添加一个 cumsum 聚合查询"""
        return self.metric(field, 'cumsum', alias)

    def cummax(self, field, alias=''):
        """添加一个 cummax 聚合查询"""
        return self.metric(field, 'cummax', alias)

    def cummin(self, field, alias=''):
        """添加一个 cummin 聚合查询"""
        return self.metric(field, 'cummin', alias)

    def cumcount(self, field, alias=''):
        """添加一个 cumcount 聚合查询"""
        return self.metric(field, 'cumcount', alias)

    def _add_metric(self, metric):
        if not metric.get('alias'):
            if metric.get('aggregation'):
                metric['alias'] = make_alias(metric.get('aggregation'), metric['field'])
            else:
                metric['alias'] = metric['field']
        if metric not in self._metrics:
            self._metrics.append(metric)

    def filters(self, filters_list):
        """添加一个或多个 filters

        :param filters_list: dict(一个) 或 list(多个) 类型, 每个 filter 用 dict 表示, 格式:
            {
                "field": "created_at",
                "operator": ">=",
                "value": "2016-07-01",
                "type": "date"
            }
        """
        for flt in ensure_list(filters_list):
            self._add_filter(**flt)
        return self

    def filter(self, field, operator, value, type=None, cast_func=None):
        """添加一个 filter

        :param field: 字段名, 必需
        :param operator: 操作符, 必需
        :param value: 值, 必需; 多值情况用 list 表示
        :param type: 字段类型, 可空, 将用于类型转换。只接受这些值: int, long, float, double, str, string, date, datetime, timestamp
        :param cast_func: 类型转换函数, 如果传了一个 callable 的函数, 将用于类型转换, 函数签名: def func(x), 其中 x 是单值(非 list 等集合类型)
        """
        self._add_filter(field, operator, value, type, cast_func)
        return self

    def flt_or(self, filters):
        """
        添加一个 或(or) 条件
        :param filters: 过滤列表， 值格式为[[filters], ..., [filters]]
        """
        return self.filter('_', 'or', value=filters)

    def flt_equal(self, field, value, type=None, cast_func=None):
        """添加一个 等于(==) 条件"""
        return self.filter(field, '==', value, type, cast_func)

    def flt_not_equal(self, field, value, type=None, cast_func=None):
        """添加一个 不等于(!=) 条件"""
        return self.filter(field, '!=', value, type, cast_func)

    def flt_gt(self, field, value, type=None, cast_func=None):
        """添加一个 大于(>) 条件"""
        return self.filter(field, '>', value, type, cast_func)

    def flt_gte(self, field, value, type=None, cast_func=None):
        """添加一个 大于或等于(>=) 条件"""
        return self.filter(field, '>=', value, type, cast_func)

    def flt_lt(self, field, value, type=None, cast_func=None):
        """添加一个 小于(<) 条件"""
        return self.filter(field, '<', value, type, cast_func)

    def flt_lte(self, field, value, type=None, cast_func=None):
        """添加一个 小于或等于(<=) 条件"""
        return self.filter(field, '<=', value, type, cast_func)

    def flt_range(self, field, value, type=None, cast_func=None):
        """添加一个 范围(range)(闭区间) 条件"""
        if not isinstance(value, (list, tuple, set)) or len(value) != 2:
            raise ParameterError('value must contain 2 element')
        return self.filter(field, 'range', value, type, cast_func)

    def flt_in(self, field, value, type=None, cast_func=None):
        """添加一个 in (in) 条件"""
        if not isinstance(value, (list, tuple, set)):
            raise ParameterError('value must be instance of list')
        return self.filter(field, 'in', value, type, cast_func)

    def flt_not_in(self, field, value, type=None, cast_func=None):
        """添加一个 not in (~in) 条件"""
        if not isinstance(value, (list, tuple, set)):
            raise ParameterError('value must be list type')
        return self.filter(field, '~in', value, type, cast_func)

    def flt_startswith(self, field, value, type=None, cast_func=None):
        """添加一个 startswith(^) 查询"""
        check_string_type(value)
        return self.filter(field, '^', value, type, cast_func)

    def flt_istartswith(self, field, value, type=None, cast_func=None):
        """添加一个 istartswith(^) 查询"""
        check_string_type(value)
        return self.filter(field, 'i^', value, type, cast_func)

    def flt_not_startswith(self, field, value, type=None, cast_func=None):
        """添加一个 not startswith(~^) 查询"""
        check_string_type(value)
        return self.filter(field, '~^', value, type, cast_func)

    def flt_not_istartswith(self, field, value, type=None, cast_func=None):
        """添加一个 not istartswith(~^) 查询"""
        check_string_type(value)
        return self.filter(field, '~i^', value, type, cast_func)

    def flt_contains(self, field, value, type=None, cast_func=None):
        """添加一个 contains(has) 查询"""
        check_string_type(value)
        return self.filter(field, 'has', value, type, cast_func)

    def flt_icontains(self, field, value, type=None, cast_func=None):
        """添加一个 icontains(has) 查询"""
        check_string_type(value)
        return self.filter(field, 'ihas', value, type, cast_func)

    def flt_not_contains(self, field, value, type=None, cast_func=None):
        """添加一个 not contains(~has) 查询"""
        check_string_type(value)
        return self.filter(field, '~has', value, type, cast_func)

    def flt_not_icontains(self, field, value, type=None, cast_func=None):
        """添加一个 not icontains(~has) 查询"""
        check_string_type(value)
        return self.filter(field, '~ihas', value, type, cast_func)

    def flt_endswith(self, field, value, type=None, cast_func=None):
        """添加一个 endswith($) 查询"""
        check_string_type(value)
        return self.filter(field, '$', value, type, cast_func)

    def flt_iendswith(self, field, value, type=None, cast_func=None):
        """添加一个 iendswith($) 查询"""
        check_string_type(value)
        return self.filter(field, 'i$', value, type, cast_func)

    def flt_not_endswith(self, field, value, type=None, cast_func=None):
        """添加一个 not endswith(~$) 查询"""
        check_string_type(value)
        return self.filter(field, '~$', value, type, cast_func)

    def flt_not_iendswith(self, field, value, type=None, cast_func=None):
        """添加一个 not iendswith(~$) 查询"""
        check_string_type(value)
        return self.filter(field, '~i$', value, type, cast_func)

    def _add_filter(self, field, operator, value, type=None, cast_func=None):
        if cast_func is not None and callable(cast_func):
            if isinstance(value, (list, tuple)):
                value = map(cast_func, value)
            else:
                value = cast_func(value)
        elif type is not None:
            if isinstance(value, (list, tuple)):
                value = [cast(x, type) for x in value]
            else:
                value = cast(value, type)
        flt = {'field': field, 'operator': operator, 'value': value}
        if type:
            flt['type'] = type
        if flt not in self._filters:
            self._filters.append(flt)

    def groupby(self, *fields):
        """添加 (一个或多个) group by 字段, 支持链式调用

        :param fields: 每个 group by 字段可以是字符串(字段名), 或 (field, udf) 格式的二元组,
            udf 支持 day, daily, week, weekly, month, monthly, year, yearly
            如果有多个 group by 字段, 则放到 list 里一起传入
        """
        for field in fields:
            if isinstance(field, tuple) and len(field) >= 2:
                udf = map_udf(field[1])
                field = '{}({})'.format(udf, field[0])
            if field not in self._groupby:
                self._groupby.append(field)
        return self

    def orderby(self, *fields):
        """添加一个或多个 order by 字段, 支持链式调用

        :param fields: 每个字段可一个单个字符串(字段名, 允许第一个字符用 '+', '-' 表示排序方向), 或 (field, direction) 格式的二元组
            direction 支持 `asc`, `+`, `desc`, `-` 四种情况。如果传入了有效的 direction, 且 field 第一个字符是 '+' 或 '-',
            仍然使用 direction 作为排序方向。
        """
        for field in fields:
            if isinstance(field, tuple) and len(field) >= 2:
                direction = map_order_dir(field[1])
                field = '{}{}'.format(direction, field[0].lstrip('+-'))
            if field not in self._orderby:
                self._orderby.append(field)
        return self

    def limit(self, count):
        self._limit = count
        return self

    def splitby_range(self, field, values):
        """添加一个 range 的切分查询，适用于多个区间（如价格区间）的结果集"""
        return self.splitby(field, 'range', values)

    def splitby_term(self, field, values):
        """添加一个 term 的切分查询"""
        return self.splitby(field, 'term', values)

    def splitby(self, field, operator, values):
        if self._splitby:
            raise ParameterError('only one split by field is supported')
        self._splitby = {
            'field': field,
            'operator': operator,
            'values': values
        }
        return self

    def execute(self, pump_client, cache_timeout=None, force=None):
        """执行查询, 需要传入 PumpClient 对象, 将调用 PumpClient.query 方法
        :param pump_client: PumpClient 对象
        :param cache_timeout: 结果缓存时间, 秒
        :param force: 是否强制查询, 忽略缓存
        :return: Response 对象, 其 result 属性是查询结果
        """
        query_body = self.to_dict(cache_timeout=cache_timeout, force=force)
        json_resp = pump_client.query(**query_body)
        return self.response_class(json_resp, query_body)

    @classmethod
    def from_dict(cls, d, ds=None):
        if ds is None:
            try:
                ds = DataSource.from_dict(d)
            except KeyError:
                raise ParameterError('ds is required')
        q = cls(ds)
        q.update_from_dict(d)
        return q

    def update_from_dict(self, d):
        if 'metrics' in d:
            self._metrics = d['metrics'] or []
        if 'filters' in d:
            self._filters = d['filters'] or []
        if 'groupby' in d:
            self._groupby = d['groupby'] or []
        if 'orderby' in d:
            self._orderby = d['orderby'] or []
        if d.get('limit'):
            self._limit = d['limit']
        if 'splitby' in d:
            self._splitby = d['splitby'] or {}
        return self

    def to_dict(self, **kwargs):
        d = self._ds.to_dict()
        if self._metrics:
            d['metrics'] = self._metrics
        if self._filters:
            d['filters'] = self._filters
        if self._groupby:
            d['groupby'] = self._groupby
        if self._orderby:
            d['orderby'] = self._orderby
        if self._limit:
            d['limit'] = self._limit
        if self._splitby:
            d['splitby'] = self._splitby
        d.update(kwargs)
        return d

    def clone(self):
        q = self.__class__(ds=self._ds)
        q._metrics = self._metrics[:]
        q._filters = self._filters[:]
        q._groupby = self._groupby[:]
        q._orderby = self._orderby[:]
        q._splitby = deepcopy(self._splitby)
        q._limit = self._limit
        return q

    copy = clone


class AsyncQuery(Query):
    response_class = AsyncResponse

    def execute(self, pump_client, cache_timeout=None, force=None):
        """执行查询, 需要传入 PumpClient 对象, 将调用 PumpClient.query_async 方法
        :param pump_client: PumpClient 对象
        :param cache_timeout: 结果缓存时间, 秒
        :param force: 是否强制查询, 忽略缓存
        :return: AsyncResponse 对象, 其 result 属性是查询结果
        """
        query_body = self.to_dict(cache_timeout=cache_timeout, force=force)
        json_resp = pump_client.query_async(**query_body)
        return self.response_class(json_resp, pump_client, query_body)
