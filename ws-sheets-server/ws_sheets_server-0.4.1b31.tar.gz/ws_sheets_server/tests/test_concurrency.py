import argparse
import asyncio
import functools
import os
import sys
import json
import unittest
import time
import subprocess

import pytest

import modconf
import async_patterns.protocol
import ws_sheets
import ws_sheets_server.client_aio

conf_mod = 'ws_sheets_server.tests.conf.simple'

@pytest.mark.asyncio
async def test(event_loop, compute_client):
    conf = modconf.import_class(conf_mod, 'Conf', tuple(), {'dev': True})
    
    proto = compute_client

    print('connected')
    
    await proto.request_new()

    res = await proto.request_sheet_data('0')

    futures = []

    for r in range(10):
        proto.set_cell('0', r, 0, 'sum(range(100))')
        
        fut = proto.request_sheet_data('0')

        futures.append(fut)
        #self.assertEqual(
        #        proto['0'][r, 0],

    print(futures)

    def func():
        done, pending = yield from asyncio.wait(futures)

        print('done =',done)
        print('pending =', pending)

        return None

    ret = asyncio.wait(futures)

    ret = await ret

    #ret = func()
    print('ret =', ret)

    print('complete')


