import asyncio as aio
import traceback
import random
from concurrent import futures

from time import sleep
from asyncio import sleep as asleep
import pycurl
from contextlib import suppress, contextmanager

import re

import geoip2.database
from bs4 import BeautifulSoup
from loader.util.context import AOPWrapper
from tld import get_tld

from netboy.util.aop_wrapper import pre_process, post_process
from ..util.payload import Payload
from loader.function import load

import atexit

import aiohttp
import uvloop

from netboy.curl.result import Result
from netboy.curl.setup import Setup

import json

from netboy.util.grouper import grouper_it


class CurlBoy:
    def __init__(self):
        self.tld = []

    def run(self, payload=None):
        curl, result = self._setup_curl(payload)
        self.curl = curl

        try:
            curl.perform()
        except pycurl.error as e:
            resp = result.result(curl, 'error')
            resp['error_code'] = e.args[0]
            resp['error_desc'] = e.args[1]
        except Exception as e:
            return {
                'spider': 'pycurl',
                'state': 'critical',
                'error_code': -2,
                'error_desc': "{} - {}".format(type(e), str(e)),
            }
        else:
            resp = result.result(curl, 'normal', None)

        resp = self._update_response(payload, resp, result)
        curl.close()
        return resp

    def view(self, result, filters):
        return {key: result.get(key) for key in filters}

    def get(self, url, **kwargs):
        payload = kwargs
        payload['url'] = url
        return self.run(payload=payload)

    def post(self, url, payload, **kwargs):
        p = kwargs
        p['url'] = url
        p['postfields'] = payload
        return self.run(payload=p)

    async def _runs(self, payload=None, info=None, curl_loop=None):

        Payload.update(payload, info, ['max_workers, chunk_size'])
        payload = pre_process(payload)

        url = payload['url']
        if not url.startswith('http'):
            url = 'http://' + url

        pat = re.compile("^(https?://)?(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d{1,5})?$")
        ip_check = pat.match(url)
        if ip_check:
            ip = ip_check.groupdict()['ip']
            if ip in self.tld[-10:]:
                # print('sleep....')
                asleep(random.random() * 3)
            else:
                self.tld.append(ip)
                if len(self.tld) > 10:
                    self.tld = self.tld[-10:]
        else:
            try:
                res = get_tld(url, as_object=True)
            except Exception as e:
                pat = re.compile("^(https?://)?(?P<url>.*)(:\d{1,5})?$")
                part = pat.match(url)
                if part in self.tld[-10:]:
                    # print('sleep....')
                    asleep(random.random() * 3)
                else:
                    self.tld.append(part)
                    if len(self.tld) > 10:
                        self.tld = self.tld[-10:]
            else:
                if res.tld in self.tld[-10:]:
                    # print('sleep....')
                    asleep(random.random() * 3)
                else:
                    self.tld.append(res.tld)
                    if len(self.tld) > 10:
                        self.tld = self.tld[-10:]

        curl, result = self._setup_curl(payload)
        resp = await self.run_async(curl, payload.get('aiohttp_timeout', 60), curl_loop)
        resp = self._update_response(payload, resp, result)
        resp = post_process(payload, resp)

        return resp

    async def run_async(self, curl, aiohttp_timeout=60, curl_loop=None):
        with aiohttp.Timeout(aiohttp_timeout):
            # resp = await CurlLoop.handler_ready(curl)
            resp = await curl_loop.handler_ready(curl)
            # resp = await .handler_ready(curl)
        return resp

    def _setup_curl(self, payload):
        curl = pycurl.Curl()
        setup = Setup()
        result = Result(setup)
        if payload.get('postfields'):
            method = payload.get('method', 'post')
            if method == 'post':
                curl = setup.method_post(curl, payload)  #
        else:
            curl = setup.method_get(curl, payload)  #
        return curl, result

    def _update_response(self, payload, resp, result):
        resp['url'] = payload.get('url')
        resp['id'] = payload.get('id')
        resp['payload'] = payload
        if payload.get('postfields'):
            resp = result.response(payload, resp, json_data=True)
        else:
            resp = result.response(payload, resp)
        data = resp.get('data')
        if data:
            if len(data) > 10 and (resp['state'] == 'error' or resp['state'] == 'critical'):
                resp['state'] = 'normal'
                resp['http_code'] = 206

        geoip = payload.get('geoip')
        ip = resp.get('primary_ip')
        if geoip and len(ip) > 0:
            reader = geoip2.database.Reader(geoip)
            response = reader.city(ip)
            resp['geoip'] = response.raw
        return resp


class CurlLoop:
    def __init__(self):
        self._multi = pycurl.CurlMulti()
        self._multi.setopt(pycurl.M_PIPELINING, 1)
        # atexit.register(self._multi.close)
        self._futures = {}

    async def handler_ready(self, c):
        self._futures[c] = aio.Future()
        self._multi.add_handle(c)
        try:
            with suppress(aio.CancelledError):
                try:
                    curl_ret = await self._futures[c]
                # except concurrent.futures._base.CancelledError as e:
                #     return {
                #         'spider': 'pycurl',
                #         'state': 'error',
                #         'error_code': -1,
                #         'error_desc': "{} - {}: maybe timeout".format(type(e), str(e)),
                #     }
                except Exception as e:
                    print(e)
                    print(type(e))
                    # effective_url = c.getinfo(pycurl.EFFECTIVE_URL)
                    # print(effective_url, 'exception!')
                    return {
                        'spider': 'pycurl',
                        'state': 'critical',
                        'error_code': -2,
                        'error_desc': "{} -- {}".format(type(e), str(e)),
                    }
                return curl_ret
        finally:
            self._multi.remove_handle(c)
            # self._multi.close()

    def perform(self):
        if self._futures:
            res = Result()
            while True:
                status, num_active = self._multi.perform()
                if status != pycurl.E_CALL_MULTI_PERFORM:
                    break
            while True:
                num_ready, success, fail = self._multi.info_read()
                # print(len(success), len(fail), '!'*200)
                for c in success:
                    cc = self._futures.pop(c)
                    # effective_url = c.getinfo(pycurl.EFFECTIVE_URL)
                    # print(effective_url, 'normal')
                    result = res.result(c, 'normal')
                    if not cc.cancelled():
                        cc.set_result(result)
                for c, err_num, err_msg in fail:
                    cc = self._futures.pop(c)
                    # effective_url = c.getinfo(pycurl.EFFECTIVE_URL)
                    # print(effective_url, 'error', err_num, err_msg)  # , connect_timeout, timeout)
                    result = res.result(c, 'error')
                    result['error_code'] = err_num
                    result['error_desc'] = err_msg
                    if not cc.cancelled():
                        cc.set_result(result)
                if num_ready == 0:
                    break


class ConcurrentBoy:
    def run(self, data):
        d = data.get('data')
        i = data.get('info')
        mode = i.get('mode', 'normal')
        if 'multi' in mode or 'process' in mode or 'thread' in mode:
            return self._run_multi(d, i, mode)
        return self._run_simple(d, i)

    def _run_multi(self, data, info, mode='process'):
        Executor = futures.ThreadPoolExecutor if 'thread' in mode else futures.ProcessPoolExecutor
        results = []
        chunk_size = info.get('chunk_size', 20)
        max_workers = info.get('max_workers', 4)
        for i, data_chunked in enumerate(grouper_it(data, chunk_size * max_workers)):
            with Executor(max_workers=max_workers) as executor:
                future_to_url = {}

                for i, payload in enumerate(grouper_it(data_chunked, chunk_size)):
                    future_to_url[executor.submit(self._run, payload, info)] = payload

                for future in futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        print('%r generated an exception: %s' % (url, exc))

                        traceback.print_tb(exc.__traceback__)
                    else:
                        results.extend(data)
        return results

    def _run_simple(self, data, info):
        results = []
        # self._curl_loop = CurlLoop()
        for payload in grouper_it(data, info.get('chunk_size', 20)):
            result = self._run(payload, info)
            results.extend(result)
            sleep_time = info.get('sleep_time', 0.5)
            if sleep_time > 0:
                sleep(sleep_time)
        return results

    def _run(self, payload, info):
        def exception_handler(context):
            print('context:', context)

        # if loop is None:
        loop = uvloop.new_event_loop()
        # loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        curl_loop = CurlLoop()
        loop.set_exception_handler(exception_handler)
        # Payload.update(payload, info, ['max_workers, chunk_size', 'mode'])
        response, _ = loop.run_until_complete(self._task(self._coro(payload, info, curl_loop), curl_loop))
        curl_loop._multi.close()
        loop.close()
        self._retry_run(response, info)
        return response

    def _retry_run(self, response, info):
        def exception_handler(context):
            print('context:', context)

        retry_config = info.get('retry')
        default_retry_config = {
            '28': ['with', 'Resolving'],
            'script': {
                'pattern': 'default',
                'minlen': 200
            },
            'refresh': {
                'pattern': 'default',
                'minlen': 200
            }
        }
        if not retry_config:
            return
        if retry_config == 'default':
            retry_config = default_retry_config

        retries = []
        default_script_patterns = [
            "\<script\>[\s\S]+\.location(.href)?=('|\")(?P<href>.+)('|\")[\s\S]+\</script\>",
        ]
        default_refresh_patterns = [
            "\<meta\s+http\-equiv=('|\")refresh('|\")\s+content=('|\").*url=(?P<refresh>.+)('|\")\>",
            # "\<meta[\s\S]+url=(?P<refresh>.+)('|\")[\s\S]*\>",
        ]

        for i, resp in enumerate(response):
            # print(rr['state'], rr['title'], i)
            state = resp['state']
            error_code = resp['error_code']
            error_desc = resp['error_desc']
            retry_keys = retry_config.keys()

            if '28' in retry_keys and error_code == 28:
                for text in retry_config['28']:
                    if text in error_desc:
                        retries.append((i, resp))
                        break

            if 'script' in retry_config.keys():
                patterns = retry_config['script'].get('pattern')
                if isinstance(patterns, str):
                    patterns = default_script_patterns

                raw_data = resp.get('data', '')
                soup = BeautifulSoup(raw_data, 'html.parser')
                scripts = [str(script) for script in soup.find_all('script', src=False)]
                for script in scripts:
                    for pattern in patterns:
                        matched = re.search(pattern, script)
                        if len(script) < retry_config['script'].get('minlen', 200) and matched:
                            effect = matched.group('href')
                            if effect.startswith('/'):
                                effect = effect[1:]
                            if not effect.startswith('http'):
                                effect = resp['effective_url'] + effect
                            print('retry effect: ', effect)
                            resp['effective_url'] = effect
                            retries.append((i, resp))
                            break
            if 'refresh' in retry_config.keys():
                patterns = retry_config['refresh'].get('pattern')
                if isinstance(patterns, str):
                    patterns = default_refresh_patterns
                raw_data = resp.get('data', '')
                for pattern in patterns:
                    matched = re.search(pattern, raw_data)
                    if len(raw_data) < retry_config['refresh'].get('minlen', 200) and matched:
                        effect = matched.group('refresh')
                        if effect.startswith('/'):
                            effect = effect[1:]
                        if not effect.startswith('http'):
                            effect = resp['effective_url'] + effect
                        print('retry effect: ', effect)
                        resp['effective_url'] = effect
                        retries.append((i, resp))
                        break

        if len(retries) > 0:
            # asleep(random.random() * 3)
            loop = uvloop.new_event_loop()
            # loop = aio.new_event_loop()
            aio.set_event_loop(loop)
            curl_loop = CurlLoop()
            loop.set_exception_handler(exception_handler)
            # Payload.update(payload, info, ['max_workers, chunk_size', 'mode'])
            coro_params = []
            for e in retries:
                a = e[1]
                payload = a.get('payload')
                job_name = payload.get('job_name') if isinstance(payload, dict) else 'default'
                job_id = payload.get('job_id') if isinstance(payload, dict) else 'default'
                task_id = payload.get('task_id') if isinstance(payload, dict) else 'default'
                a['job_name'] = job_name
                a['job_id'] = job_id
                a['task_id'] = task_id
                a['keep'] = {'retried': True,
                             'job_name': job_name,
                             'job_id': job_id,
                             'task_id': task_id,
                             }
                a['cookies'] = [self.cookie_kv(cookie) for cookie in e[1]['cookies']]
                coro_params.append(a)
            # coro_params = [{
            #     'url': e[1]['url'],
            #     'effective_url': e[1]['effective_url'],
            #     'keep': {'retried': True},
            #     'cookies': [self.cookie_kv(cookie) for cookie in e[1]['cookies']],
            #     # 'timeout': 60,
            #     # 'connecttimeout': 60
            # } for e in retries]
            # print(coro_param)
            ra, _ = loop.run_until_complete(
                self._task(self._coro(coro_params, info, curl_loop), curl_loop))
            curl_loop._multi.close()
            loop.close()
            #
            for i, rre in enumerate(ra):
                response[retries[i][0]] = rre

    async def _coro(self, payload, info, curl_loop=None):
        targets = []
        boy = CurlBoy()
        for p in payload:
            d = {'url': p} if type(p) is str else p
            targets.append(boy._runs(d, info, curl_loop))
        res = await aio.gather(
            *targets, return_exceptions=False
        )
        return res

    async def _task(self, coro, curl_loop=None):
        pycurl_task = aio.ensure_future(self._loop(curl_loop))
        try:
            r = await coro
        finally:
            pycurl_task.cancel()
            with suppress(aio.CancelledError):
                await pycurl_task
        return r, pycurl_task

    async def _loop(self, curl_loop=None, wait=0):
        while True:
            await aio.sleep(wait)
            # CurlLoop.perform()
            curl_loop.perform()

    def view(self, results, filters):
        scene = []
        for result in results:
            updated = {key: result.get(key) for key in filters}
            scene.append(updated)
        return scene

    def cookie_kv(self, cookie):
        # print('cookies'*10)
        index_equal = cookie.find('=')
        index_semcol = cookie.find(';')
        key = cookie[:index_equal]
        value = cookie[index_equal + 1:index_semcol]
        return (key, value)


def post_test(payload, resp):
    print('haha')
    return resp


if __name__ == '__main__':
    boy = CurlBoy()
    r = boy.get('http://www.google.com',
                proxytype='socks5',
                proxy='127.0.0.1',
                proxyport=1081,
                useragent='Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0')
    print(json.dumps(boy.view(r, ['state']), indent=2, ensure_ascii=False))

    # boy = CurlBoy()
    # r = boy.post('http://192.168.199.212:8006/v1/spider_query',
    #              payload={
    #                  "charset": "UTF-8",
    #                  "filters": [
    #                      "title"
    #                  ],
    #                  "pagenum": 1,
    #                  "pagesize": 10,
    #                  "state": "normal"
    #
    #              })
    # print(json.dumps(boy.view(r, ['data']), indent=2, ensure_ascii=False))
    boy = ConcurrentBoy()
    data = {
        "data": [
            # {'url': 'http://www.sohu.com',
            #  'post_func': 'netboy.curl.boy.post_test'},
            {"url": "http://www.baidu.com",
             'post_func': 'netboy.curl.boy.post_test',
             "followlocation": 1},
            # "http://www.douban.com",
            # {
            #     'url': 'http://192.168.199.212:8006/v1/spider_query',
            #     'postfields': {
            #         "charset": "UTF-8",
            #         "filters": [
            #             "title"
            #         ],
            #         "pagenum": 1,
            #         "pagesize": 10,
            #         "state": "normal"
            #     }
            # },
            # 'http://www.sohu.com',
            # {'url': 'http://www.bing.com'},
            # {'url': 'http://www.baidu.com'},
            # {'url': 'http://www.facebook.com'},
            # {'url': 'http://www.google.com'},
            # {'url': 'http://www.youtube.com'}, {'url': 'http://www.github.com'},
        ],
        "info": {
            "chunk_size": 2,
            "max_workers": 2,
            "useragent": 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            # "mode": 'threaded'
        }
    }
    r = boy.run(data)
    # print(r)
    print(
        json.dumps(
            boy.view(r, ["title", "url", "state", "error_desc", "error_code", "total_time", "mode", "charset", "keep"]),
            indent=2,
            ensure_ascii=False))
    print(len(r))
