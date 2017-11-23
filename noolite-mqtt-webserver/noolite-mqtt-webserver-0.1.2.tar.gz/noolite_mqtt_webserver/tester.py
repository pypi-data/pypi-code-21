import time

import asyncio
from aiohttp import ClientSession

on_url = 'http://192.168.1.34:8080/api.htm?ch=0&cmd=6&fmt=3&d0=0&d1=255&d2=0'
off_url = 'http://192.168.1.34:8080/api.htm?ch=0&cmd=6&fmt=3&d0=255&d1=0&d2=0'


async def fetch(url, session, index):
    async with session.get(url) as response:
        before = time.time()
        response = await response.read()
        print('#{} - Time for request: {}'.format(index, time.time() - before))
        print('{}\n'.format(response))
        return response


async def run(r):
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for x in range(r):
            url = on_url if x % 2 == 0 else off_url
            task = asyncio.ensure_future(fetch(url, session, x))
            tasks.append(task)
            await asyncio.sleep(0.09)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable
        # print(responses)

total_before = time.time()
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(20))
loop.run_until_complete(future)
print('Total time: {}'.format(time.time() - total_before))
