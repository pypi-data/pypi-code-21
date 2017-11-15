#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import logging
import time
from operator import itemgetter

from bs4 import BeautifulSoup as bsp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from agent.exc import WorkerException
from agent.qualityplatform.api import (
    add_user_comment,
    add_crawler_history,
    get_app_channel_crawler_history
)
from agent.worker.base import BaseWorker

logger = logging.getLogger(__name__)


class Crawler(BaseWorker):
    def __init__(self, data):
        super(Crawler, self).__init__(data)
        self.app_channel_url = self.data.get('app_channel_url')
        self.crawler_type = self.data.get('crawler_type')
        self.app_channel_id = self.data.get('app_channel_id')
        self.last_crawl_at = self.get_last_crawl_at()
        print self.task_id
        print self.app_channel_url
        print self.crawler_type
        print self.last_crawl_at
        print self.app_channel_id

    def start_worker(self):
        if self.crawler_type == 'appstore':
            self.__appstore_crawl()
        elif self.crawler_type == 'xiaomi':
            self.__xiaomi_crawl()
        self.complete()

    def save(self, comments):
        for comment in comments:
            try:
                add_user_comment({
                    'app_channel_id': self.app_channel_id,
                    'device_name': comment.get('device_name', ''),
                    'content': comment.get('content', ''),
                    'rating': comment.get('rating', -1),
                    'user': comment.get('user', ''),
                    'comment_at': int(time.mktime(comment.get('comment_at', None).timetuple()))
                })
                time.sleep(0.01)
            except Exception as e:
                logger.warning('add user comment error: {}'.format(repr(e)))

    def get_last_crawl_at(self):
        last_crawl_at = get_app_channel_crawler_history(self.app_channel_id)
        last_crawl_time = last_crawl_at.get('data')[0].get('last_crawl_at')
        return datetime.datetime.strptime(last_crawl_time, '%Y-%m-%dT%H:%M:%S')

    def __appstore_crawl(self):
        appstore_username = self.data.get('username')
        appstore_password = self.data.get('password')
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
            username.send_keys(appstore_username)
            password = wait.until(EC.visibility_of_element_located((By.ID, "pwd")))
            password.send_keys(appstore_password)
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
            logger.info("end of crawl ios appstore comments...")
        except Exception as e:
            browser.quit()
            raise WorkerException(e)

    def __xiaomi_crawl(self):
        xiaomi_username = self.data.get('username')
        xiaomi_password = self.data.get('password')
        logger.info('start to crawl xiaomi user comments...')
        browser = webdriver.Firefox()
        try:

            wait = WebDriverWait(browser, 120)
            logger.info("start to login qq")
            browser.get('http://wetest.qq.com/auth/login/?next=/')
            browser.switch_to.frame(browser.find_element_by_id('qq_frame'))
            wait.until(EC.visibility_of_element_located((By.ID, "switcher_plogin"))).click()
            time.sleep(2)
            username = wait.until(EC.visibility_of_element_located((By.ID, "u")))
            username.send_keys(xiaomi_username)
            password = wait.until(EC.visibility_of_element_located((By.ID, "p")))
            password.send_keys(xiaomi_password)
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.ID, "login_button"))).click()
            time.sleep(2)
            logger.info("login qq successfully")

            pagenum = 0
            browser.switch_to.default_content()
            browser.get(self.app_channel_url +
                        '&startDate=' + self.last_crawl_at.strftime('%Y-%m-%d') +
                        '+00%3A00%3A00&endDate=' + datetime.datetime.now().strftime('%Y-%m-%d') +
                        '+23%%3A29%%3A00&nextPage=%s' % pagenum)
            wait = WebDriverWait(browser, 120)
            content = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
            contents = json.loads(content)
            total = contents.get('ret', {}).get('total', 30)
            pagesize = contents.get('ret', {}).get('pagesize', 30)
            comments = []
            for i in range(0, total / pagesize + 1):
                stop_flag = False
                url = self.app_channel_url + \
                      '&startDate=' + self.last_crawl_at.strftime('%Y-%m-%d') + \
                      '+00%3A00%3A00&endDate=' + datetime.datetime.now().strftime('%Y-%m-%d') + \
                      '+23%%3A29%%3A00&nextPage=%s' % i
                browser.get(url)
                content = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
                try:
                    content = json.loads(content)
                except ValueError as e:
                    logger.exception(e)
                    continue
                data = content.get('ret', {}).get('searchDatas', [])
                for comment in data:
                    comment_at = datetime.datetime.strptime(
                        comment.get('createtime'), '%Y-%m-%d %H:%M:%S')
                    if self.last_crawl_at < comment_at:
                        comments.append({
                            'content': comment.get('content', ''),
                            'comment_at': comment_at,
                            'rating': float(comment.get('rank', -1)) * 2,
                            'user': comment.get('author', ''),
                        })
                    else:
                        stop_flag = True
                        break
                if stop_flag:
                    break
            if len(comments) == 0:
                logger.info("end of crawl andorid xiaomi comments...")
                return
            sorted_comments = sorted(comments, key=itemgetter('comment_at'))
            logger.info("start to save comment ...")
            self.save(sorted_comments)
            logger.info("start to update crawler history ...")
            add_crawler_history({
                "app_channel_id": self.app_channel_id,
                "last_crawl_at": int(time.mktime(sorted_comments[-1].get('comment_at').timetuple()))
            })
            logger.info("end of crawl andorid xiaomi comments...")
        except Exception as e:
            browser.quit()
            raise WorkerException(e)
