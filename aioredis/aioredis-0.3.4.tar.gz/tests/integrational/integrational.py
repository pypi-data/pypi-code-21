import asyncio
import aioredis

from functools import partial
from timeit import timeit


async def old_pool_or_redis(maxsize=10):
    return await aioredis.create_pool(('localhost', 6379),
                                      maxsize=maxsize)


async def new_redis_pool(maxsize=10):
    return await aioredis.create_redis_pool(('localhost', 6379),
                                            maxsize=maxsize)


async def simple_get_set(pool, val):
    val = 'val:{}'.format(val)
    with await pool as redis:
        assert await redis.set('key', val)
        await redis.get('key', encoding='utf-8')


async def pipeline(pool, val):
    val = 'val:{}'.format(val)
    with await pool as redis:
        f1 = redis.set('key', val)
        f2 = redis.get('key', encoding='utf-8')
        ok, res = await asyncio.gather(f1, f2)


async def transaction(pool, val):
    val = 'val:{}'.format(val)
    with await pool as redis:
        tr = redis.multi_exec()
        tr.set('key', val)
        tr.get('key', encoding='utf-8')
        ok, res = await tr.execute()
        assert ok, ok
        assert res == val


# NOTE: blocking operations (ex: BLPOP) will probably use
#   same connection in new pool so blocking it for long time.
#   This must be fixed.
async def blocking_pop(pool, val):

    async def lpush():
        with await pool as redis:
            # here v0.3 has bound connection, v1.0 does not;
            await asyncio.sleep(.1)
            await redis.lpush('list-key', 'val')

    @asyncio.coroutine
    def blpop():
        with (yield from pool) as redis:
            # here v0.3 has bound connection, v1.0 does not;
            res = yield from redis.blpop(
                'list-key', timeout=1, encoding='utf-8')
            assert res == ['list-key', 'val'], res
    await asyncio.gather(blpop(), lpush())


async def repeat(runnable, n=1):
    done, pending = await asyncio.wait([asyncio.ensure_future(runnable(i))
                                        for i in range(n)])
    assert not pending
    done = [f.exception() for f in done]
    a = b = 0
    for rv in done:
        if rv is None:
            a += 1
        else:
            b += 1

    print("success/failure: {G}{success}{C}/{R}{failure}{C}"
          .format(success=a, failure=b,
                  G='\033[0;32m', R='\033[0;31m', C='\033[0m'))


if __name__ == '__main__':
    run = asyncio.get_event_loop().run_until_complete

    print("aioredis v{}".format(aioredis.__version__))
    if hasattr(aioredis, 'create_redis_pool'):
        print("Testing new Redis pool")
        pool = run(new_redis_pool(maxsize=5))
    else:
        print("Testing old Pool of Redis clients")
        pool = run(old_pool_or_redis(maxsize=5))

    async def cleanup():
        with await pool as client:
            await client.flushdb()
    run(cleanup())
    try:
        print("running simple get/set test…", end=' ')
        t = timeit(lambda: run(repeat(partial(simple_get_set, pool), n=100)),
                   number=1)
        print("took:", t)
        print("running pipeline test…", end=' ')
        t = timeit(lambda: run(repeat(partial(pipeline, pool), n=100)),
                   number=1)
        print("took:", t)
        print("running multi-exec test…", end=' ')
        t = timeit(lambda: run(repeat(partial(transaction, pool), n=100)),
                   number=1)
        print("took:", t)
        print("running blpop test…", end=' ', flush=True)
        t = timeit(lambda: run(repeat(partial(blocking_pop, pool), n=100)),
                   number=1)
        print("took:", t)
    finally:
        pool.close()
        run(pool.wait_closed())
