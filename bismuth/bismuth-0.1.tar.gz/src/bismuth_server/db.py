# coding=utf-8
from asyncio import CancelledError, ensure_future, wait

import aioredis
from aioredis.pubsub import Receiver
import asyncpg
from sanic.log import log

from bismuth_server.crypto import Keyset


redis = None  # redis and redis pubsub
pubsub = None
redis_listener_task = None
subscriptions = {}  # {channel: listeners subscribed}
listeners = {}  # {listener: channels subscribed to}
pgpool: asyncpg.pool.Pool = None  # read/write connection pool


async def setup_dbconn(conn):
    await conn.execute('SET SESSION synchronous_commit TO OFF;')


async def initialize_db(app, loop):

    async def connect_redis():
        global redis, pubsub, redis_listener_task
        try:
            log.debug('setting up redis')
            redis = await aioredis.create_redis_pool(
                (
                    app.config.get('REDIS', '127.0.0.1'),
                    int(app.config.get('REDISPORT', 6379))
                ),
                loop=loop,
                minsize=2,  # one for pubsub, one for cache
                maxsize=int(app.config.get('MAX_REDIS_POOL', 10)),
            )
            pubsub = Receiver(loop=loop)
            # suppress inspection: pubsub has magic iteration
            # noinspection PyTypeChecker
            redis_listener_task = loop.create_task(redis_listener(pubsub))
            app.add_task(redis_listener_task)
            # configure key eviction in redis on connection
            await redis.config_set('maxmemory-policy', 'allkeys-lru')
        except Exception as ex:
            log.error(f"could not set up redis: {type(ex)} {ex}")
            raise

    async def connect_postgres():
        global pgpool
        try:
            log.debug('connecting to postgres')
            pgpool = await asyncpg.create_pool(
                app.config.DB_URL,
                loop=loop,
                min_size=1,
                max_size=int(app.config.get('MAX_DB_POOL', 10)),
                setup=setup_dbconn,
            )
        except Exception as ex:
            log.error(f"could not set up postgres: {type(ex)} {ex}")
            raise

    await wait([
        connect_redis(),
        connect_postgres(),
    ])


async def cleanup_db(app, loop):
    log.debug('shutting down redis listener')
    redis_listener_task.cancel()

    log.debug('shutting down postgres connection pool')
    await pgpool.close()
    log.debug('postgres connection pool shut down')

    log.debug('shutting down redis connection pool')
    redis.close()
    await redis.wait_closed()
    log.debug('redis connection pool shut down')


def subscribe_channel(topic):
    """Accepts a topic (bytes) and returns the corresponding database channel"""
    return b"t:" + topic


def keys_cache_key(topic):
    return b"keys:" + topic


def message_cache_key(message_id):
    return b"msg:" + message_id


async def notify(topic, message):
    channel = subscribe_channel(topic)
    await redis.publish(channel, message)


async def listen(topic, listener):
    # update listeners on topic
    channel = subscribe_channel(topic)
    if channel in subscriptions:
        subscriptions[channel].add(listener)
    else:
        await redis.subscribe(pubsub.channel(channel))
        subscriptions[channel] = {listener}
    # update topics listened to
    if listener in listeners:
        listeners[listener].add(channel)
    else:
        listeners[listener] = {channel}


async def unlisten(topic, listener):
    channel = subscribe_channel(topic)
    if channel in listeners.get(listener, ()):  # listener is subbed to this topic
        subscriptions[channel].remove(listener)
        if not subscriptions[channel]:
            await redis.unsubscribe(channel)
            del subscriptions[channel]
        listeners[listener].remove(channel)
        if not listeners[listener]:
            del listeners[listener]


async def unlisten_all(listener):
    if listener in listeners:
        for channel in listeners[listener]:
            subscriptions[channel].remove(listener)
            if not subscriptions[channel]:
                await redis.unsubscribe(channel)
                del subscriptions[channel]
        del listeners[listener]


async def redis_listener(redis_pubsub):
    """Handle all messages received from redis pubsub"""
    try:
        log.debug('listening for redis pubsub')
        # wait for redis to start moving
        if not await redis_pubsub.wait_message():
            log.debug('redis listener waited for nothing')
            return False
        async for channel, data in redis_pubsub.iter():
            channel = channel.name
            # publish to all subscribers of this channel
            if subscriptions.get(channel):
                for listener in subscriptions[channel]:
                    ensure_future(listener(channel, data))
    except CancelledError:
        pass
    except Exception as ex:
        log.error(f"redis_listener crashed: {type(ex)} {repr(ex)}")
        raise
    finally:
        log.debug('redis listener stopped')


async def get_message_content(message_id):  # TODO: iron out semantics, redis and in-app caching
    async with pgpool.acquire() as conn:
        return await conn.fetchrow(
            '''SELECT topic, topic_serial, signature, message_body(data) FROM message WHERE id = $1;''',
            message_id
        )


async def get_message_length(message_id):  # TODO: iron out semantics
    async with pgpool.acquire() as conn:
        return await conn.fetchval(
            '''SELECT length(message_body(data)) FROM message WHERE id = $1;''',
            message_id
        )


async def post_message(topic, data, signature):
    async with pgpool.acquire() as conn:
        result = await conn.fetchrow(
            '''SELECT * FROM post_message_raw($1, $2, $3);''',
            topic, data, signature
        )
        if topic and result['status'] == 'success':
            ensure_future(notify(topic, result['message_id']))
        return result['status']


async def get_topic_keys(topic):  # TODO: implement keys, iron out semantics, in-app caching
    """Get the (write, control) keys for a topic, or None if the topic does not exist."""
    # check redis cache
    cache_key = keys_cache_key(topic)
    cached = redis and await redis.get(cache_key)
    if cached:
        return Keyset.from_redis(cached)
    else:
        async with pgpool.acquire() as conn:
            body = await conn.fetchval('''SELECT message_body(data) FROM message WHERE id = $1;''', topic)
            if body:
                # extract keys from
                keys = Keyset.from_message(body)
                redis and await redis.set(cache_key, keys.serialize_to_redis())
                return keys
            else:
                return None
