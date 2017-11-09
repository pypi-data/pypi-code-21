#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging
import time

from agent.qualityplatform.api import (
    add_user_comment
)
from base import BaseWorker

logger = logging.getLogger(__name__)


class Crawler(BaseWorker):
    def __init__(self, data):
        super(Crawler, self).__init__(data)
        self.task_id = data.get('task_id')[0]
        self.app_channel_url = data.get('app_channel_url')
        self.last_crawl_at = datetime.datetime.fromtimestamp(float(data.get('last_crawl_at')))
        self.app_channel_id = data.get('app_channel_id')

    def start_worker(self):
        pass

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
