import json
import datetime
import logging
import time
from operator import itemgetter

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


class XiaomiCrawler(BaseCrawler):
    def __init__(self, data):
        super(XiaomiCrawler, self).__init__(data)
        self.username = data.get('username')
        self.password = data.get('password')

    def crawl(self):
        logger.info('start to crawl xiaomi user comments...')
        try:
            self.browser = webdriver.Firefox()
            wait = WebDriverWait(self.browser, 120)
            logger.info("start to login qq")
            self.browser.get('http://wetest.qq.com/auth/login/?next=/')
            self.browser.switch_to.frame(self.browser.find_element_by_id('qq_frame'))
            wait.until(EC.visibility_of_element_located((By.ID, "switcher_plogin"))).click()
            time.sleep(2)
            username = wait.until(EC.visibility_of_element_located((By.ID, "u")))
            username.send_keys(self.username)
            password = wait.until(EC.visibility_of_element_located((By.ID, "p")))
            password.send_keys(self.password)
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.ID, "login_button"))).click()
            time.sleep(2)
            logger.info("login qq successfully")

            pagenum = 0
            self.browser.switch_to.default_content()
            self.browser.get(self.app_channel_url +
                        '&startDate=' + self.last_crawl_at.strftime('%Y-%m-%d') +
                        '+00%3A00%3A00&endDate=' + datetime.datetime.now().strftime('%Y-%m-%d') +
                        '+23%%3A29%%3A00&nextPage=%s' % pagenum)
            wait = WebDriverWait(self.browser, 120)
            content = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
            contents = json.loads(content)
            total = contents.get('ret', {}).get('total', 30)
            pagesize = contents.get('ret', {}).get('pagesize', 30)
            comments = []
            for i in range(0, total/pagesize + 1):
                stop_flag = False
                url = self.app_channel_url +\
                        '&startDate=' + self.last_crawl_at.strftime('%Y-%m-%d') +\
                        '+00%3A00%3A00&endDate=' + datetime.datetime.now().strftime('%Y-%m-%d') +\
                        '+23%%3A29%%3A00&nextPage=%s' % i
                self.browser.get(url)
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
                update_task_status(self.task_id, TaskStatus.success.value)
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
            update_task_status(self.task_id, TaskStatus.success.value)
            logger.info("end of crawl andorid xiaomi comments...")
        except Exception as e:
            update_task_status(self.task_id, TaskStatus.failed.value)
            logger.exception(e)
        finally:
            try:
                if self.browser is not None:
                    self.browser.quit()
            except Exception as e1:
                logger.exception(e1)
