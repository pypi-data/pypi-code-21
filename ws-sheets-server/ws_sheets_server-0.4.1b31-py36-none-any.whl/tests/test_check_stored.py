import asyncio
import io
import pickle
import time
import os
import sys
import json
import logging
import logging.config
import subprocess
import traceback

import pytest

import modconf
import ws_storage.impl.filesystem
import ws_sheets

conf_dir = os.path.join(os.environ['HOME'], 'config')
conf_mod = 'ws_sheets_server.tests.conf.simple'

class Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        print('  {:32} {}'.format(module, name))
        return pickle.Unpickler.find_class(self, module, name)

def unpickle(b):
    return Unpickler(io.BytesIO(b)).load()

@pytest.fixture
def fail_on_deserialize_error():
    return False

@pytest.mark.asyncio
async def test(event_loop, storage_server, fail_on_deserialize_error):
    _, addr_storage = storage_server
    conf = modconf.import_class(conf_mod, 'Conf', tuple(), {
        'dev': True,
        #'console': True,
        }, folder=conf_dir)
    logging.config.dictConfig(conf.LOGGING)

    s = await ws_storage.impl.client.Storage.create(
            event_loop, addr_storage[0], addr_storage[1])
   
    print('storage={}'.format(s))

    lst = await s.list_files()
    
    print('files =',lst)

    fail = False
    for f in lst:
        if f == '_counter': continue

        try:
            print('file=',f)
            b = await s.read_binary(f)
            
            o = pickle.loads(b)
            
            #print(repr(o))
            #print(dir(o))
        except Exception as e:
            print(e)
            fail = True
            print('  use unpickler')
            try:
                o = unpickle(b)
            except: pass
            
            if False:
                print('  deleting')
                await s.delete(f)
                print('  deleted')
                continue
            
            fail=True

    if fail_on_deserialize_error:
        assert not fail



