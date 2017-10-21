# -*- coding: utf-8 -*-
import os

BOT_NAME = 'geocrawl'

SPIDER_MODULES = ['geocrawl.spiders']
NEWSPIDER_MODULE = 'geocrawl.spiders'

USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 32

LOG_STDOUT = False

GC_USERNAME = os.environ.get('GC_USERNAME')
GC_PASSWORD = os.environ.get('GC_PASSWORD')
