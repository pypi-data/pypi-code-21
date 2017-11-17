#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from . import defaults
import time
import logging
from scrapy.exceptions import IgnoreRequest


logger = logging.getLogger(__name__)


class node(object):

    def __init__(self, proxy, weight, params={}, next_node=None):
        self.proxy = proxy
        self.weight = weight
        self.params = params
        self._next = next_node


class Common_Middleware(object):

    def __init__(self,
                 PROXYFILE=defaults.PROXYFILE,
                 UPDATE_FREQ=defaults.UPDATE_FREQ,
                 UPDATE_INV=defaults.UPDATE_INV,
                 PROXY_THRESHOLD=defaults.PROXY_THRESHOLD,
                 PROXY_GETTER=defaults.PROXY_GETTER,
                 BAN_CODE=defaults.BAN_CODE,
                 IGNORE_CODE=defaults.IGNORE_CODE,
                 PROXY_URL=defaults.PROXY_URL
                 ):
        '''
        代理用环来表示
        proxy:代理信息
        weight:权值
        代理
        proxy_under_use 当前在用
        proxy_before 当前前一个

        '''

        # 代理文件
        self.filename = PROXYFILE
        # 更新代理频率
        self.freq = UPDATE_FREQ
        # 代理最小更新周期（代理更新频率太快，会导致获取不到新代理，浪费效率）
        self.min_update_period = UPDATE_INV
        # 代理的获取函数
        self.proxy_get_func = PROXY_GETTER
        self.proxy_url = PROXY_URL
        # 阈值，可用代理数小于这个值时获取新代理
        self.fetch_proxy_threshold = PROXY_THRESHOLD
        # 被反爬出现的status_code，根据不同code，使用不同过程处理
        self.ban_code = BAN_CODE
        self.ignore_code = IGNORE_CODE

        # 代理池相关变量
        self.proxy_pool = {}
        self.proxy_node_table = {}
        self.valid_proxyes_num = 0
        self.default_weight = 5

        # 上次更新代理时间
        self.proxy_update_time = time.time()

        # 错误计数器，输出日志相关
        self.exception_dict = {}

        # 初始化
        self.load_proxies()
        self.new_proxy_cycle()

    @classmethod
    def from_settings(cls, settings):
        kwargs = {
            'PROXYFILE': defaults.PROXYFILE,
            'UPDATE_FREQ': defaults.UPDATE_FREQ,
            'UPDATE_INV': defaults.UPDATE_INV,
            'PROXY_THRESHOLD': defaults.PROXY_THRESHOLD,
            'PROXY_GETTER': defaults.PROXY_GETTER,
            'BAN_CODE': defaults.BAN_CODE,
            'IGNORE_CODE': defaults.IGNORE_CODE,
            'PROXY_URL': defaults.PROXY_URL,
        }

        for name, setting_name in kwargs.items():
            val = settings.get(name)
            if val:
                kwargs[name] = val

        return cls(**kwargs)

    def load_proxies(self):
        # 读取proxy文件，若不存在则初始化，返回一个proxies的更新时间
        proxyfile = os.path.join(os.getcwd(), self.filename)

        # 查看是否存在proxy文件，若不存在，更新保存
        if os.path.exists(proxyfile):
            with open(proxyfile, 'r+') as f:
                self.proxy_pool = json.load(f)
        else:
            self.new_proxies()
        if time.time() - self.proxy_pool['time'] > self.freq:
            self.new_proxies()
        return self.proxy_pool['time']

    def new_proxies(self):
        # 更新代理池，并保存
        self.proxy_pool = {
            'time': time.time(),
            'proxy': self.proxy_get_func(proxy_url=self.proxy_url)
        }
        with open(os.path.join(os.getcwd(), self.filename), 'w+') as f:
            json.dump(self.proxy_pool, f)

    def new_proxy_cycle(self):
        # 环构建，由当前代理池构建一个环
        self.valid_proxyes_num = 0
        for proxy in self.proxy_pool['proxy']:
            new_node = node(
                proxy=proxy,
                weight=self.default_weight,
                params=self.proxy_pool['proxy'][proxy]
            )
            self.proxy_node_table[proxy] = new_node
            if not self.valid_proxyes_num:
                self.proxy_under_use = self.proxyes_nodes = temp = new_node
            else:
                temp._next = new_node
                temp = temp._next
            self.valid_proxyes_num += 1

        self.proxy_under_use = temp._next = self.proxyes_nodes
        self.proxy_before = temp
        self.proxy_update_time = time.time()

        logger.info("build proxyes num {}".format(self.valid_proxyes_num))

    def update_proxy_cycle(self, delay=20):
        # 更新环
        logger.info("extending proxyes")

        t = self.load_proxies()

        if self.proxy_update_time > t:
            self.new_proxies()

        np = []
        # 若有新代理，插入
        for proxy in self.proxy_pool['proxy']:
            if proxy not in self.proxy_node_table:
                np.append(proxy)

        # 将新代理插入环
        for proxy in np:
            temp = node(
                proxy=proxy,
                weight=self.default_weight,
                params=self.proxy_pool['proxy'][proxy]
            )

            self.proxy_node_table[proxy] = temp

            self.proxy_before._next = temp
            temp._next = self.proxy_under_use
            self.proxy_before = temp
            self.valid_proxyes_num += 1

        self.proxy_update_time = time.time()

    def use_next_proxy(self, request):
        request.meta["proxy"] = "https://" + self.proxy_under_use.proxy
        self.proxy_before = self.proxy_under_use
        self.proxy_under_use = self.proxy_under_use._next

    def build_request(self, request):
        pass

    def process_request(self, request, spider):

        # 主要错误为302 所以设置禁止跳转
        request.meta["dont_redirect"] = True
        request.meta["dont_merge_cookies"] = True

        # 代理定期更新
        if time.time() - self.proxy_update_time > self.freq:
            self.update_proxy_cycle()
            self.proxy_update_time = time.time()

        # 代理权值小于0 代理出队
        while self.proxy_under_use.weight < 0 and self.valid_proxyes_num > 1:
            self.proxy_under_use = self.proxy_under_use._next
            if self.proxy_under_use.proxy in self.proxy_node_table:
                self.proxy_node_table.pop(self.proxy_under_use.proxy)
            self.valid_proxyes_num -= 1
            while self.valid_proxyes_num < self.fetch_proxy_threshold:
                logger.error('only {} proxies left sleep for a while'.format(
                    self.valid_proxyes_num))
                time.sleep(300)
                self.new_proxies()
                self.new_proxy_cycle()
                self.proxy_update_time = time.time()

        while self.valid_proxyes_num < 2:
            time.sleep(120)
            self.update_proxy_cycle()

        self.proxy_before._next = self.proxy_under_use

        # 请求赋值，这个根据不同中间件各自编写
        self.build_request(request)

        # 使用下一个代理
        self.use_next_proxy(request)

        logger.info(
            "crawl  {} proxy {}".format(
                request.url,
                request.meta['proxy'],
            ))
        return

    def process_response(self, request, response, spider):
        # 根据不同响应码，修改代理权重代理
        if 'proxy' in request.meta:
            this_proxy = request.meta['proxy'].replace('https://', '')
        else:
            if response.status == 200:
                return response
            else:
                return

        if response.status != 200:
            if response.status in self.ban_code:
                # 在bancode里，权值快速下降
                self.proxy_node_table[this_proxy].weight = min(
                    self.proxy_node_table[this_proxy].weight // 3,
                    self.proxy_node_table[this_proxy].weight - 3
                )
            elif response.status in self.ignore_code:
                return response
            else:
                # 其他错误，权值下降
                self.proxy_node_table[this_proxy].weight = min(
                    self.proxy_node_table[this_proxy].weight // 2,
                    self.proxy_node_table[this_proxy].weight - 2
                )

        else:
            # 好用的代理，权值增加~
            if this_proxy in self.proxy_node_table:
                self.proxy_node_table[this_proxy].weight += 1
            logger.info('finish downloaded {}'.format(request.url))
            return response

    def process_exception(self, request, exception, spider):
        # 出现错误，权值下降，因为有可能proxy_node已被其他函数销毁，所以用个try..except..防止报错
        # logger.error(exception)
        # logger.error('url {}'.format(request.url))
        except_name = exception.__class__.__name__
        if 'proxy' in request.meta:
            this_proxy = request.meta['proxy'].replace('https://', '')
        else:
            return

        if not isinstance(exception, IgnoreRequest):
            if this_proxy in self.proxy_node_table:
                self.proxy_node_table[this_proxy].weight = min(
                    self.proxy_node_table[this_proxy].weight // 2,
                    self.proxy_node_table[this_proxy].weight - 2,
                )
            if except_name in self.exception_dict:
                self.exception_dict[except_name] += 1
                if self.exception_dict[except_name] % 50 == 0:
                    logger.error('{} happend 50 times total {} times'.format(
                        except_name, self.exception_dict[except_name]))
            else:
                self.exception_dict[except_name] = 1
            return
