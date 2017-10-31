# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/8
import logging
import threading

from hunters.constant import Regex
# try:
#     eval(str, {}, {'s': s})
# except Exception as e:
#     data = traceback.format_exc()
#     print("err %s" % data)
from hunters.utils import md5hex

logger = logging.getLogger("defaults")


class DefaultFilter(object):
    """ 定义一些默认的 Filter """

    def __init__(self):
        # URL 排重集合
        self.all_url_sets = set()
        self.lock = threading.Lock()

    def url_duplicate_filter(self, url, task_meta):
        """
        URL排重过滤器方法
        这东西要求高可以考虑用BloomFilter实现, 但是鉴于每个任务就是一个URL, 分布式独立部署, 先不优化
        """
        prefix = ""
        key = url
        if task_meta:
            prefix = task_meta.task_id
            key = "%s:%s" % (prefix, url)  #: 排重的KEY

        key = md5hex(key)
        with self.lock:
            if key not in self.all_url_sets:
                self.all_url_sets.add(key)
                return True
            logger.info("%s URL SAME =>%s" % (prefix, url))
            return False

    @staticmethod
    def url_schema_filter(url):
        """
        URL schema 过滤器, 过滤不符合指定协议的URL
        类似的有如下,  都不考虑
        href="javascript:;"
        href="ftp://...
        href="ws://....
        href="about:blank"

        特殊的图片格式, base64可以考虑
        src="data:image/png;base64

        src="blob:xxxxx"  blob协议不考虑, 属于内存二进制映射方案

        :param url:string:
        :return:
        """
        logger.debug("_url_schema_filter=>%s", url)
        return url.startswith("http") or url.startswith("data:image/png;base64")  # http , https or base64img

    def url_raw_filter(self, url):
        """ 二进制文件过滤 """
        if Regex.RE_RAW_LINK.search(url):
            return False
        return True


class DefaultOutput(object):
    def __init__(self, spider):
        self.spider = spider

    def url_output_handler(self, tab=None, deep=0, headers=None, extra=None, task_meta=None):
        """ 默认的一个输出控制器, 这个控制器抓取页面的URL重新压入url抓取队列 """
        match = Regex.RE_LINK.findall(tab.text)
        for url in match:
            logger.debug("_url_output_handler => %s, deep=>%s, base=>%s" % (url, deep + 1, tab.url))
            print(url)
            result = self.spider.add_url(url, base_url=tab.url, deep=deep + 1, extra=extra, task_meta=task_meta, headers=headers)
            if result == 0:
                # 如果队列满了, 不再加入
                return
