import os
import asyncio
import functools
import pickle
import logging
import logging.config

import pytest

import modconf
import ws_storage.impl.filesystem
import ws_storage.impl.as3
import ws_storage.impl.client

class Foo: pass

@pytest.mark.asyncio
async def test(storage_default):
    await _test(storage_default)

@pytest.mark.asyncio
async def test_client(storage_client):
    await _test(storage_client)

@pytest.mark.asyncio
async def test_list(storage_default):
    await _test_list(storage_default)

@pytest.mark.asyncio
async def test_list_client(storage_client):
    await _test_list(storage_client)

async def _test(s):
    f = Foo()

    b = pickle.dumps(f)
    
    id_ = await s.next_id()
    
    print('id =',id_)

    await s.write_binary(id_, b)

    b = await s.read_binary(id_)

    f = pickle.loads(b)

    print(f)
    
    await asyncio.sleep(1)

    await s.delete(id_)
    
    with pytest.raises(ws_storage.exceptions.FileNotFound):
        await s.read_binary('doesnt_exist')

    with pytest.raises(ws_storage.exceptions.FileNotFound):
        await s.delete('doesnt_exist')

async def _test_list(s):
    # TODO appears to be bug cause by combination of botocore and aiobotocore
    if isinstance(s, ws_storage.impl.as3.Storage):
        if s._use_botocore:
            with pytest.raises(NotImplementedError):
                await s.list_files()
            return
    await s.list_files()






