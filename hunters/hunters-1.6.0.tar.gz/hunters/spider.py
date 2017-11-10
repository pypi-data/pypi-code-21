# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/8

#############################################
import logging
import threading
from queue import Queue

from hunters.browser import BrowserConfig
from hunters.core import Spider
from hunters.defaults import DefaultFilter, DefaultOutput
from hunters.exceptions import spider_exception_listener
from hunters.utils import ForeverThreadPool

logger = logging.getLogger("spider")


class AutoSpider(Spider):
    """
    一个默认的自动化爬虫实例
    该实例有一个默认URL排重过滤器
    AddURL ->  Filter(URL过滤器) --> URLQUEUE --> GET PAGE --> Output(URL解析输出器) --> AddURL -->Loop
    也有一个默认的输出(抓取页面URL并返插入抓取队列
    循环往复, 所以会不断的抓取URL不断爬
    """

    def __init__(self, browser_config=BrowserConfig(), queue=Queue()):
        Spider.__init__(self, browser_config=browser_config, queue=queue)

        self.max_deep(3)  # 默认深度 3
        self.max_urls(10)  # 默认URL连接10个

        self.init_default_filter()  # 初始化默认filter
        self.init_default_output()  # 指定一个默认输出控制器

    def init_default_filter(self):
        """ 初始化一些默认过滤器  注意过滤器的顺序, 可以更好的过滤效果 """
        filters = DefaultFilter()
        self.add_filter(filters.url_schema_filter)  # 默认添加http协议过滤器
        self.add_filter(filters.url_duplicate_filter)  # 默认添加排重过滤器

    def init_default_output(self):
        outputs = DefaultOutput(spider=self)
        # 这里因为要正则解析所有文本类型的路径, 包括JS的, 所以输出控制器类型是文本类型都可以经过url_output控制器
        self.add_output(content_type="text|javascript", output=outputs.url_output_handler)


class SpiderServer(Spider):
    """
    Spider以服务的形式存在.
    服务型的Spider不会停机运转, 外部不断add_url,  会不断的从队列中取内容执行.
    配合其他监听接口服务(http, tcp)等可以从外部add_url
    因此, 各项max_url和深度计数器可能每个任务默认的计数器
    如果想针对每个URL当成一个任务请求去调用.在add_url的时候需要添加task_meta=TaskMeta() 描述每个任务的信息
    """

    def __init__(self, browser_config=BrowserConfig(), queue=Queue()):
        super(SpiderServer, self).__init__(browser_config=browser_config, queue=queue)

    def _mutli_thread_run(self, num, wait=True):
        def wrap():
            try:
                self._loop_run()
            except Exception as e:
                logger.error("Thread[%s] run error %s " % (threading.currentThread().name, e))
                spider_exception_listener.handle_exception(e)

        fx = ForeverThreadPool(num)
        fx.submit(target=wrap, args=())
