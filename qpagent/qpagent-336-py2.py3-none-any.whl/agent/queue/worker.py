#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from apscheduler.schedulers.blocking import BlockingScheduler

import agent.qualityplatform.api as server_api
from agent.consts import AgentStatus
from agent.queue import (
    macaca_q,
    selenium_q,
    appcrawler_q,
    androidmonkey_q,
    crawlerTask_q,
    iosmonkey_q
)
from agent.worker.android_monkey import AndroidMonkey
from agent.worker.appcrawler import Appcrawler
from agent.worker.appstore import AppStoreCrawler
from agent.worker.compatibility import Compatibility
from agent.worker.ios_monkey import iosmonkey
from agent.worker.macaca import Macaca
from agent.worker.xiaomi import XiaomiCrawler

logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
scheduler = BlockingScheduler()


def handle_macaca_task():
    while True:
        data = macaca_q.get(True)
        if data:
            Macaca(data).run()


def handle_selenium_task():
    while True:
        data = selenium_q.get(True)
        if data:
            Compatibility(data).run()


def handle_appcrawler_task():
    while True:
        data = appcrawler_q.get(True)
        if data:
            Appcrawler(data).run()


def handle_androidmonkey_task():
    while True:
        data = androidmonkey_q.get(True)
        if data:
            AndroidMonkey(data).run()


def handle_iosmonkey_task():
    while True:
        data = iosmonkey_q.get(True)
        if data:
            iosmonkey(data).run()


def handle_crawler_task():
    while True:
        data = crawlerTask_q.get(True)
        if data:
            crawler_type = data.get('crawler_type')
            if crawler_type == 'appstore':
                AppStoreCrawler(data).crawl()
            elif crawler_type == 'xiaomi':
                XiaomiCrawler(data).crawl()


def check_devices():
    server_api.register_agent(AgentStatus.online.value)


def handle_schedulers():
    scheduler.add_job(check_devices, 'interval', seconds=15)
    scheduler.start()
