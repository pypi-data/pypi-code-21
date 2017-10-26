# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time

import tornado.gen
import tornado.httpclient
from tornado.escape import utf8, json_decode, json_encode

from .compat import urlencode, iteritems, basestring
from .client import ClientBase
from .dsl import Query as _Query
from .exceptions import TimeoutError
from .result import AsyncResponse as _AsyncResponse, Result, Response


class PumpClient(ClientBase):
    def __init__(self, host, port):
        super(PumpClient, self).__init__(host, port)

        self._client = tornado.httpclient.AsyncHTTPClient()

    def _prepare_url(self, url, params):
        if url.endswith('/'):
            url = url.strip('/')
        return '%s?%s' % (url, self._encode_params(params))

    @staticmethod
    def _encode_params(data):
        result = []
        for k, vs in iteritems(data):
            if isinstance(vs, basestring) or not hasattr(vs, b'__iter__'):
                vs = [vs]
            for v in vs:
                if v is not None:
                    result.append((utf8(k), utf8(v)))
        return urlencode(result, doseq=True)

    @tornado.gen.coroutine
    def _get(self, url, params, **kwargs):
        full_url = self._prepare_url(url, params)
        resp = yield self._client.fetch(full_url, **kwargs)
        content = json_decode(resp.body)
        raise tornado.gen.Return(content)

    @tornado.gen.coroutine
    def _post(self, url, data, **kwargs):
        resp = yield self._client.fetch(url, method='POST', body=json_encode(data),
                                        headers={'Content-Type': 'application/json'}, **kwargs)
        content = json_decode(resp.body)
        raise tornado.gen.Return(content)


class AsyncResponse(_AsyncResponse):
    @tornado.gen.coroutine
    def status(self):
        resp = yield self._pump_client.query_async_status(self.task_id)
        raise tornado.gen.Return(resp['data']['status'])

    @tornado.gen.coroutine
    def info(self):
        resp = yield self._pump_client.query_async_info(self.task_id)
        raise tornado.gen.Return(resp['data'])

    @tornado.gen.coroutine
    def retry(self):
        """重试该查询"""
        resp = yield self._pump_client.query_async_retry(self.task_id)
        self.task_id = resp['data']['task_id']  # task_id 可能会发生变化
        raise tornado.gen.Return(self.task_id)

    @tornado.gen.coroutine
    def get_result(self):
        if self._result is self._MISSING:
            resp = yield self._pump_client.query_async_result(self.task_id)
            if resp['ok']:
                self._result = Result(resp['data'], self.query_body)
            else:
                self._result = None
        raise tornado.gen.Return(self._result)

    @tornado.gen.coroutine
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
            status = yield self.status()
            if status in self.COMPLETE_STATUS:
                break
            yield tornado.gen.sleep(interval)

        raise tornado.gen.Return(status == 'SUCCESS')

    @property
    def result(self):
        """如果异步查询任务已经成功完成, 把结果封装成 Result 对象"""
        raise NotImplementedError('Use get_result() to get result pandas DataFrame')


class Query(_Query):
    @tornado.gen.coroutine
    def execute(self, pump_client, cache_timeout=None, force=None):
        query_body = self.to_dict(cache_timeout=cache_timeout, force=force)
        json_resp = yield pump_client.query(**query_body)
        resp = self.response_class(json_resp, query_body)
        raise tornado.gen.Return(resp)


class AsyncQuery(_Query):
    response_class = AsyncResponse

    @tornado.gen.coroutine
    def execute(self, pump_client, cache_timeout=None, force=None):
        """执行查询, 需要传入 PumpClient 对象, 将调用 PumpClient.query_async 方法
        :param pump_client: PumpClient 对象
        :param cache_timeout: 结果缓存时间, 秒
        :param force: 是否强制查询, 忽略缓存
        :return: AsyncResponse 对象, 其 result 属性是查询结果
        """
        query_body = self.to_dict(cache_timeout=cache_timeout, force=force)
        json_resp = yield pump_client.query_async(**query_body)
        resp = self.response_class(json_resp, pump_client, query_body)
        raise tornado.gen.Return(resp)
