# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import requests

from .compat import urlparse
from .exceptions import ParameterError
from .schema import query_schema
from .utils import ensure_list


class ClientBase(object):
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self._init_urls()

    def _init_urls(self):
        base = '{}://{}:{}'.format('http', self.host, self.port)
        self._query_url = urlparse.urljoin(base, '/query')
        self._query_async_url = urlparse.urljoin(base, '/query/async')
        self._query_async_status_url = urlparse.urljoin(base, '/query/status')
        self._query_async_result_url = urlparse.urljoin(base, '/query/result')
        self._query_async_info_url = urlparse.urljoin(base, '/query/info')
        self._query_async_retry_url = urlparse.urljoin(base, '/query/retry')

    def _get(self, url, params, **kwargs):
        raise NotImplementedError

    def _post(self, url, data, **kwargs):
        raise NotImplementedError

    def query(self, ds_type, ds_dsn, table, metrics=None, filters=None,
              groupby=None, orderby=None, limit=None, splitby=None, q=None, cache_timeout=None, force=None,
              async=False):
        """调用 /query 接口

        :param ds_type: data source type, 如 mongodb, sqla, elasticsearch 等
        :type ds_type: str
        :param ds_dsn: 连接字符串, 如 mongodb://localhost/mydb
        :type ds_dsn: str
        :param table: 表(SQL) 或 集合(MongoDB)
        :type table: str
        :param metrics: 计算/查询指标, 每个指标格式: {'field': 'field', 'aggregation': 'max'}
        :type metrics: list
        :param filters: 过滤条件, 每个条件格式: {'field': 'field', 'operator': '==', 'value': 1}
        :type filters: list
        :param groupby: 分组字段
        :type groupby: list
        :param orderby: 排序字段
        :type orderby: list
        :param limit: 限定返回结果数量
        :type limit: int
        :param splitby: 类似 Kibana 的 split by
        :type splitby: dict
        :param q: 自定义查询, SQL 或 json.dumps 的字符串
        :type q: str
        :param cache_timeout: 查询结果缓存秒数, > 0 时将会缓存
        :type cache_timeout: int
        :param force: 是否强制查询(忽略缓存)
        :type force: bool
        :param async: 是否异步查询
        :type async: bool
        """
        params = {
            'ds_type': ds_type,
            'ds_dsn': ds_dsn,
            'table': table,
            'metrics': ensure_list(metrics),
            'filters': ensure_list(filters),
            'groupby': ensure_list(groupby),
            'orderby': ensure_list(orderby),
            'limit': limit,
            'splitby': splitby,
            'q': q,
            'cache_timeout': cache_timeout,
            'force': force
        }
        params = {k: v for k, v in params.items() if v is not None}

        errors = query_schema.validate(params)
        if errors:
            raise ParameterError(errors)

        url = self._query_async_url if async else self._query_url
        return self._post(url, params)

    def query_async(self, *args, **kwargs):
        """调用 /query/async 接口, 参数和 :meth:`query` 一样"""
        return self.query(*args, async=True, **kwargs)

    def query_async_status(self, task_id):
        """调用 /query/status 接口获取异步查询状态"""
        return self._get(self._query_async_status_url, params={'task_id': task_id})

    def query_async_result(self, task_id):
        """调用 /query/result 接口获取异步查询结果"""
        return self._get(self._query_async_result_url, params={'task_id': task_id})

    def query_async_info(self, task_id):
        """调用 /query/info 接口获取查询参数"""
        return self._get(self._query_async_info_url, params={'task_id': task_id})

    def query_async_retry(self, task_id):
        """调用 /query/retry 接口获取查询参数"""
        return self._get(self._query_async_retry_url, params={'task_id': task_id})


class PumpClient(ClientBase):
    """PumpClient 用于调用 pump 服务的 API

    :param host: pump 服务部署的 IP 或域名
    :type host: str or unicode
    :param port: pump 服务部署的端口
    :type port: int
    """

    def __init__(self, host=None, port=None, app=None):
        super(PumpClient, self).__init__(host, port)

        self._session = requests.Session()

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """config from Flask application"""
        self.host = app.config.get('PUMP_HOST', 'localhost')
        self.port = app.config.get('PUMP_PORT', 8800)
        self._init_urls()

    def _get(self, url, params, **kwargs):
        resp = self._session.get(url, params=params, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def _post(self, url, data, **kwargs):
        resp = self._session.post(url, json=data, **kwargs)
        resp.raise_for_status()
        return resp.json()
