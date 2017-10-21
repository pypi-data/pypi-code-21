# coding=utf-8

import logging
import socket
import time
import requests


class Fetcher(object):
    def __init__(self):
        pass

    def rnd(self):
        return str(int(time.time() * 100))

    def get_next_user_agent(self):
        """
        更换 user-agent 有利于反抓取
        :return:
        """

        return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'

    def http_request_impl(self, method, target, headers, payload, charset, timeout):
        if method == 'GET':
            r = requests.get(target, headers=headers, data=payload, timeout=timeout)
        else:
            r = requests.post(target, headers=headers, data=payload, timeout=timeout)

        if charset is not None:
            r.encoding = charset
        return r.status_code, r.text

    def http_request(self,
                     method,
                     target,
                     headers,
                     inputs=None,
                     charset=None,
                     timeout=60,
                     retry_times=9,
                     retry_sleep_factor=5000
                     ):

        if inputs is None:
            inputs = {}

        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.get_next_user_agent()

        # 超时重试
        retried = -1
        while True:
            retried = retried + 1
            try:
                status, content = self.http_request_impl(method, target, headers, inputs, charset, timeout)
                break
            except (socket.gaierror, socket.timeout) as e:
                if retried > 0:
                    log = logging.getLogger(__name__)
                    log.warning("Warning: %s socket timeout. retried %d times." % (target, retried))
                if retried > retry_times:
                    raise e
                time.sleep(retry_sleep_factor * (retried + 1) * 0.001)

        if status not in (200, 201, 456):
            log = logging.getLogger(__name__)
            log.warning(content)

        return self.http_request_handle(target, status, content)

    def http_request_handle(self, target, status, content):
        return status, content

    def http_get_js(self, target,
                    charset='utf-8', timeout=60, retry_times=9, retry_sleep_factor=5000):
        headers = {'Content-type': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate',
                   'Cache-Control': 'max-age=0',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5'
                   }
        return self.http_request('GET',
                                 target,
                                 headers,
                                 charset=charset,
                                 timeout=timeout,
                                 retry_times=retry_times,
                                 retry_sleep_factor=retry_sleep_factor
                                 )

    def http_get_html(self, target,
                      charset='gbk', timeout=60, retry_times=9, retry_sleep_factor=5000):
        headers = {'Content-type': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate',
                   'Cache-Control': 'max-age=0',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5'
                   }
        return self.http_request('GET',
                                 target,
                                 headers,
                                 charset=charset,
                                 timeout=timeout,
                                 retry_times=retry_times,
                                 retry_sleep_factor=retry_sleep_factor
                                 )

    def http_get_json(self, target,
                      charset='gbk', timeout=60, retry_times=9, retry_sleep_factor=5000):
        headers = {'Content-type': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate',
                   'Cache-Control': 'max-age=0',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5'
                   }
        return self.http_request('GET',
                                 target,
                                 headers,
                                 charset=charset,
                                 timeout=timeout,
                                 retry_times=retry_times,
                                 retry_sleep_factor=retry_sleep_factor
                                 )

    def http_get_text(self, target,
                      charset='utf-8', timeout=60, retry_times=9, retry_sleep_factor=5000):
        headers = {'Content-type': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate',
                   'Cache-Control': 'max-age=0',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'en-US,en;q=0.5'
                   }
        return self.http_request('GET',
                                 target,
                                 headers,
                                 charset=charset,
                                 timeout=timeout,
                                 retry_times=retry_times,
                                 retry_sleep_factor=retry_sleep_factor
                                 )


fetcher = Fetcher()
