import asyncio
import argparse
import functools
import logging
import logging.config
import os
import sys
import json
import subprocess
import time

import pytest

import modconf
import ws_sheets
import ws_sheets.tests.test_demos
import ws_sheets_server.client_aio
import async_patterns.protocol

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
@pytest.mark.parametrize("cls", ws_sheets.tests.test_demos.DEMOS.values())
async def test(compute_client, cls):
    
    o = cls()
    
    print('------------------ {} -----------------'.format(cls))
    
    await compute_client.request_new()
    
    print('got new book')
    
    o.book = compute_client
    
    print('call atest')
    await o.atest()

    # sync with server?
    resp = await compute_client.request_sheet_data('0')
    print(resp)


