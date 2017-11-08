#!/usr/bin/env python
# -*- coding: utf-8 -*-

from agent.worker.ios_monkey import iosmonkey
# from agent.worker.ios_appcrawler import Appcrawler

if __name__ == '__main__':
    data = {999:{"worker_type":5,"ip":"10.12.38.246","port":9099,"device_id":"199ce7e631ef60de8b6702e8142c1f8af3073205","notice_account":"['tianchen.zhang@ele.me']","app_version":"7.20","grand_id":"me.ele.ios.eleme","platform":"iOS","packtype":"Debug","throttle":300,"pct_touch":30,"pct_motion":30,"pct_syskeys":5}}

    # data = {"params":{'task_id':999,'notice_account':'tianchen.zhang@ele.me','device_id':'32575086c794e341f59e03799f5d8164ad157c1d','app_url':'http://download.ele.me/ios_864c0e2a6dc234c2900a05bb490e6e79.ipa','port':'9096'}}
    # print data
    #
    # crawler = Appcrawler(data)
    # crawler.start_worker()

    monkey = iosmonkey(data)
    monkey.data = data




    # monkey.data = data
    # monkey.udid = '32575086c794e341f59e03799f5d8164ad157c1d'
    # monkey.search_key = 'Integration'
    # monkey.notice_account = 'tianchen.zhang@ele.me'
    # monkey.get_deviceName()
    # monkey.start_WDATest()
    # monkey.deal_report()