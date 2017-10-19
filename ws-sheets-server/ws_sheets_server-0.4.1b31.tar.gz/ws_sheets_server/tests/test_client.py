import argparse
import asyncio
import functools
import json
import os
import subprocess
import sys
import time

import pytest

import modconf
import ws_sheets
import ws_sheets_server.client_aio
import async_patterns.protocol

conf_mod = 'ws_sheets_server.tests.conf.simple'

@pytest.mark.asyncio
async def test(event_loop, compute_client):

    protocol = compute_client

    print(protocol)
    
    await protocol.request_new()

    res = await protocol.request_sheet_data('0')

    print('future result')
    print(repr(res))






