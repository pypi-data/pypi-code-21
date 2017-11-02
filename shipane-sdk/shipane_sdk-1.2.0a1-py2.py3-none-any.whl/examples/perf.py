# -*- coding: utf-8 -*-

import logging

import shipane_sdk

logging.basicConfig(level=logging.DEBUG)

client = shipane_sdk.Client(host='localhost', port=8888, key='')
try:
    client.buy('title:moni', type='LIMIT', symbol='732113', price=13.37, amountProportion='ALL')
except Exception as e:
    pass
try:
    client.buy('title:wangshang', type='LIMIT', symbol='732113', price=13.37, amountProportion='ALL')
except Exception as e:
    pass
try:
    client.buy('title:yinhe', type='LIMIT', symbol='732113', price=13.37, amountProportion='ALL')
except Exception as e:
    pass
