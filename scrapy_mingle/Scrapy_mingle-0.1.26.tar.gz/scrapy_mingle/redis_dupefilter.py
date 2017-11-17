#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-06 09:28:59
# @Author  : xuhaomin
# @Version : python3.6

import logging

from scrapy_redis.dupefilter import RFPDupeFilter


logger = logging.getLogger(__name__)


class CFWSDupeFilter(RFPDupeFilter):
    """
    重写scrapy_redis的去重组件
        1.去重判断使用来自request.meta的一个关键字duplicater
        2.如果meta不含有dupefilter这个key，我们可以认为该请求不参与去重
        3.去重队列使用SCHEDULER_DUPEFILTER_KEY设置的key名

    """

    logger = logger


    def request_seen(self, request):
        """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
        fp = request.meta.get('dupefilter', 0)
        if fp:
            added = self.server.sadd(self.key, fp)
            return added == 0
        else:
            return False