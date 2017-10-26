# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time

import pandas as pd

from .compat import string_types
from .exceptions import TimeoutError
from .utils import extract_func_field, map_udf, make_alias


class Response(object):
    def __init__(self, response, query_body):
        """封装查询请求的结果

        :param response: PumpClient.query_async 返回的结果, 是个 json 对象
        :type response: dict
        :param query_body: 执行查询的 json 参数
        :type query_body: dict
        """
        self._json_response = response
        self._query_body = query_body

    @property
    def ok(self):
        """查询API是否调用成功"""
        return self._json_response['ok']

    @property
    def data(self):
        """调用成功时的结果"""
        return self._json_response['data']

    @property
    def reason(self):
        """调用失败的原因"""
        return self._json_response['reason']

    @property
    def result(self):
        """如果调用成功, 把结果封装成 Result 对象"""
        if self.ok:
            return Result(self.data, self._query_body)
        return None


class AsyncResponse(object):
    _MISSING = object()
    COMPLETE_STATUS = ['SUCCESS', 'FAILURE', 'REVOKED']

    def __init__(self, response_or_task_id, pump_client, query_body=None):
        """封装异步查询请求的结果, 及相应的方法调用

        :param response_or_task_id: PumpClient.query_async 返回的结果, 是个 json 对象; 或 task_id
        :type response_or_task_id: dict or str or unicode
        :param pump_client: `PumpClient` 对象
        :type pump_client: pypump.PumpClient
        """
        self._pump_client = pump_client

        if isinstance(response_or_task_id, dict):
            self.task_id = response_or_task_id['data']['task_id']
        else:
            self.task_id = response_or_task_id

        self._query_body = query_body

        self._result = self._MISSING

    @property
    def query_body(self):
        if not self._query_body:
            self._query_body = self.info()['args']
        return self._query_body

    def status(self):
        """异步查询任务的状态"""
        resp = self._pump_client.query_async_status(self.task_id)
        return resp['data']['status']

    def success(self):
        """异步查询任务是否成功"""
        return self.status() == 'SUCCESS'

    def failed(self):
        """异步查询任务是否失败"""
        return self.status() == 'FAILURE'

    def info(self):
        """该异步查询的元信息, 包括参数、状态、失败原因等"""
        resp = self._pump_client.query_async_info(self.task_id)
        return resp['data']

    def retry(self):
        """重试该查询"""
        resp = self._pump_client.query_async_retry(self.task_id)
        self.task_id = resp['data']['task_id']  # task_id 可能会发生变化
        return self.task_id

    def get_result(self):
        if self._result is self._MISSING:
            resp = self._pump_client.query_async_result(self.task_id)
            if resp['ok']:
                self._result = Result(resp['data'], self.query_body)
            else:
                self._result = None

        return self._result

    def wait_until_complete(self, interval=1, timeout=None):
        """轮询任务状态，直到执行完成。

        任务完成的状态：
        1. SUCCESS 成功，当且仅当这种状态下，才可以通过 `get_result` 获取结果
        2. FAILURE 失败，可以通过 `info` 查看失败原因，`get_result` 将返回 None
        3. REVOKED 被取消

        :param interval: 轮询间隔的秒数
        :param timeout: 超时秒数，0 或 None 表示没有限制
        :return 返回任务是否执行成功
        :rtype bool
        """
        status = None
        start = time.time()
        if timeout:
            timeout = float(timeout)
        while True:
            if timeout and (time.time() - start) >= timeout:
                raise TimeoutError
            status = self.status()
            if status in self.COMPLETE_STATUS:
                break
            time.sleep(interval)

        return status == 'SUCCESS'

    @property
    def result(self):
        """如果异步查询任务已经成功完成, 把结果封装成 Result 对象"""
        return self.get_result()


class Result(object):
    def __init__(self, data, query_body):
        self._data = data
        self._query_body = query_body

    @property
    def stats(self):
        """查询的统计信息"""
        return self._data['stats']

    def __iter__(self):
        for item in self.data:
            yield item

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    @property
    def data(self):
        """查询结果, list 类型, 每个元素是一条记录"""
        return self._data['data']

    @property
    def columns(self):
        return self._data['columns']

    @property
    def df(self):
        """将查询结果(list of records)转换成 DataFrame"""
        if not hasattr(self, '_df'):
            self._df = pd.DataFrame(self.data)
            if self._df.empty:
                self._df = pd.DataFrame(self.data, columns=self.columns)
        return self._df

    def get_series(self, metric_or_groupby, silent=True):
        """从结果中获取一组值(一列), 返回 pandas.Series 类型

        :param metric_or_groupby: metric 字典或 groupby 字段(可以是单个字符串, 或者 (field, udf) 格式的 tuple)
        :param silent: 如果为True，当在数据中找不到对应列，则返回空的Series对象；否则抛出ValueError异常
        """
        col = self.get_col_name(metric_or_groupby)
        return self._get_series(col, silent)

    def get_series_by_field_and_func(self, field, func=None, silent=True):
        """从结果中获取一组值(一列), 返回 pandas.Series 类型

        :param field: field 值(metric 中的 field 或 groupby 的 field)
        :type field: str
        :param func: 函数名(metric 中的 aggregation, groupby 中的 udf (daily...))
        :type func: str
        :param silent: 如果为True，当在数据中找不到对应列，则返回空的Series对象；否则抛出ValueError异常
        :type silent: bool
        """
        col = field
        if col not in self.df:
            col = self._find_possible_col_name(field, func)

        return self._get_series(col, silent)

    def _get_series(self, col, silent=True):
        if col not in self.df:
            if not silent:
                raise ValueError('cannot derive possible key by giving parameters')
            else:
                return pd.Series(name=col)
        return self.df[col]

    def get_col_name(self, metric_or_groupby):
        """ 根据metric_or_groupby参数计算结果集中的列名

        :param metric_or_groupby: metric 字典或 groupby 字段(可以是单个字符串, 或者 (field, udf) 格式的 tuple)
        """
        if isinstance(metric_or_groupby, string_types):
            # metric: field or alias
            # groupby: field or udf(field)
            col = metric_or_groupby
            if col not in self.df:
                col = self._find_possible_col_name(metric_or_groupby)
        elif isinstance(metric_or_groupby, tuple):
            # metric: (field, aggregation)
            # groupby: (field, udf)
            col = self._find_possible_col_name(metric_or_groupby[0], metric_or_groupby[1])
        elif isinstance(metric_or_groupby, dict):
            # metric: {"field": field, "aggregation": agg, "alias": alias}
            col = metric_or_groupby.get('alias')
            if not col or col not in self.df:
                col = self._find_possible_col_name(metric_or_groupby['field'], metric_or_groupby.get('aggregation'))
        else:
            raise ValueError('unsupport parameter type "%s", expected are string, tuple or dict')
        return col

    def _find_possible_col_name(self, field=None, func=None):
        udf, field = extract_func_field(field)
        if udf:
            func = map_udf(udf)
        else:
            func = map_udf(func) or ''
        alias = self._col_names_mapping().get((field, func))
        return alias

    def _col_names_mapping(self):
        if not hasattr(self, '__col_names_mapping'):
            mapping = {}
            for m in self._query_body.get('metrics', []):
                agg = m.get('aggregation', '')
                val = m['field']
                if m.get('alias'):
                    val = m['alias']
                elif agg:
                    val = make_alias(m['aggregation'], m['field'])
                mapping[(m['field'], agg)] = val

            for g in self._query_body.get('groupby', []):
                func, field = extract_func_field(g)
                if func:
                    val = make_alias(func, field)
                else:
                    val = field
                    func = ''
                mapping[(field, func)] = val

            self.__col_names_mapping = mapping
        return self.__col_names_mapping
