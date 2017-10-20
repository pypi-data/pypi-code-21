import os
import functools
import logging

import pytest
import toml

import ws_storage.server
import ws_storage.impl.filesystem
import ws_storage.impl.as3
import ws_storage.impl.client

class_list = [
    ws_storage.impl.filesystem.Storage,
    ws_storage.impl.as3.Storage,
    functools.partial(ws_storage.impl.as3.Storage, use_botocore=True),
    ]

is_client_list = [False, False, False, True]

@pytest.fixture()
async def storage_server(request, event_loop):
    print('fixture storage_server')

    args = {
            'conf_mod': 'ws_storage.tests.conf.simple',
            'conf_dir': os.path.join(os.environ['HOME'], 'config'),
            'dev': True,
            'port': 0,
            }

    async with ws_storage.server.Application(event_loop, args) as (app, addr):
        yield app, addr

@pytest.fixture()
async def storage_client(event_loop, storage_server):
    print('fixture storage_client')
    _, addr = storage_server
    s = await ws_storage.impl.client.Storage.create(event_loop, addr[0], addr[1])
    assert not s.transport.is_closing()
    yield s

@pytest.fixture(params=class_list)
async def storage_default(request, event_loop):
    print('fixture storage_default')
    
    cls = request.param

    args = {
            'dev': True,
            'conf_dir': os.path.join(os.environ['HOME'], 'config'),
            'console': True,
            }
    
    #conf = modconf.import_class(
    #        'ws_storage.tests.conf.simple', 
    #        'Conf', 
    #        tuple(),
    #        args)
    with open('ws_storage.toml') as f:
        conf = toml.loads(f.read())
    
    logging.config.dictConfig(conf['logging'])

    s = cls(conf, event_loop)

    yield s



