import asyncio
import concurrent
import pytest

import ws_sheets_server

def test():
    ret = ws_sheets_server.main([''])
    print(ret)

@pytest.mark.asyncio
async def test_runserver(event_loop, storage_server):
    _, storage_addr = storage_server

    argv = ['', 'runserver', 'ws_sheets_server.tests.conf.simple', '--dev', '--console', 
            '--addr_storage', storage_addr[0], str(storage_addr[1]), '--test_timeout', '2']

    event_loop.set_default_executor(concurrent.futures.ProcessPoolExecutor())

    future = event_loop.run_in_executor(None, ws_sheets_server.main, argv)
    
    await future

    # TODO future says its cancelled but process seems unaffected, doesnt exit until keyboard interrupt
    #await asyncio.sleep(2)
    
    #res = future.cancel()

    #print('cancel res', res)
    
    #with pytest.raises(concurrent.futures.CancelledError):
    #    await future

    #print(future)


