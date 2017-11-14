#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import logging
import datetime
from operator import itemgetter
from bs4 import BeautifulSoup as bsp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from baseCrawler import BaseCrawler
from agent.qualityplatform.api import (
    add_user_comment,
    update_task_status,
    add_crawler_history
)
from agent.consts import (
    TaskStatus
)

logger = logging.getLogger(__name__)


class AppStoreCrawler(BaseCrawler):
    def __init__(self, data):
        super(AppStoreCrawler, self).__init__(data)
        self.username = data.get('username')
        self.password = data.get('password')

    def crawl(self):
        browser = None
        try:
            logger.info('start to crawl ios appstore user comments...')
            comments = []
            browser = webdriver.Firefox()
            wait = WebDriverWait(browser, 120)
            logger.info("start to login itunes")
            browser.get('https://itunesconnect.apple.com/login')
            wait.until(EC.presence_of_element_located((By.ID, 'aid-auth-widget-iFrame')))
            browser.switch_to.frame(browser.find_element_by_id('aid-auth-widget-iFrame'))
            username = wait.until(EC.visibility_of_element_located((By.ID, "appleId")))
            username.send_keys(self.username)
            password = wait.until(EC.visibility_of_element_located((By.ID, "pwd")))
            password.send_keys(self.password)
            login = wait.until(EC.element_to_be_clickable((By.ID, "sign-in")))
            login.click()
            time.sleep(3)
            logger.info("login successfully")
            browser.switch_to.default_content()
            browser.get(self.app_channel_url)
            content = bsp(browser.page_source).find_all(id="json")[0].get_text().encode('utf-8')
            contents = json.loads(content)
            total_count = contents.get('data', []).get('reviewCount', 1000)
            for i in range(0, total_count / 100):
                stop_flag = False
                if i == 0:
                    browser.get(self.app_channel_url)
                else:
                    browser.get(self.app_channel_url + '?index=%s' % (i * 100))
                content = bsp(browser.page_source).find_all(id="json")[0].get_text().encode('utf-8')
                content = json.loads(content)
                data = content.get('data', []).get('reviews', [])
                for comment in data:
                    comment_at = datetime.datetime.strptime(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                            float(str(comment.get('value', {}).get('lastModified', ''))[0:-3]))),
                        '%Y-%m-%d %H:%M:%S')
                    if self.last_crawl_at < comment_at:
                        comments.append({
                            'content': comment.get('value', {}).get('review', ''),
                            'comment_at': comment_at,
                            'device_name': 'iphone',
                            'user': comment.get('value', {}).get('nickname', ''),
                            'rating': float(comment.get('value', {}).get('rating', -1)) * 2
                        })
                    else:
                        stop_flag = True
                        break
                if stop_flag:
                    break
            if len(comments) == 0:
                update_task_status(self.task_id, TaskStatus.success.value)
                logger.info("end of crawl ios appstore comments...")
                return
            sorted_comments = sorted(comments, key=itemgetter('comment_at'))
            logger.info("start to save comment ...")
            self.save(sorted_comments)
            logger.info("start to update crawler history ...")
            add_crawler_history({
                "app_channel_id": self.app_channel_id,
                "last_crawl_at": int(time.mktime(sorted_comments[-1].get('comment_at').timetuple()))
            })
            update_task_status(self.task_id, TaskStatus.success.value)
            logger.info("end of crawl ios appstore comments...")
        except Exception as e:
            print 'appstore got exception : {}'.format(e)
            update_task_status(self.task_id, TaskStatus.failed.value)
        finally:
            if browser:
                browser.close()

