#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import datetime
import time

from agent.qualityplatform.api import (
    add_user_comment,
    update_task_status,
    add_crawler_history
)

logger = logging.getLogger(__name__)


class BaseCrawler(object):
    def __init__(self, data):
        self.task_id = data.get('task_id')[0]
        self.app_channel_url = data.get('app_channel_url')
        self.last_crawl_at = datetime.datetime.fromtimestamp(float(data.get('last_crawl_at')))
        self.app_channel_id = data.get('app_channel_id')

    def crawl(self):
        raise NotImplementedError

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