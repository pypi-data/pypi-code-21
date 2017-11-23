import asyncio
import logging
import time
from asyncio import Event, Queue, QueueEmpty, Task, TimeoutError, sleep
from typing import Mapping, Optional, Union

import aiohttp

SEND_QUEUE_MAX_SIZE = 16384
SEND_MIN_CHUNK_SIZE = 16
SEND_MAX_CHUNK_SIZE = 1024
SEND_MAX_INTERVAL = 1.0
SEND_MIN_INTERVAL = 0.25


FieldValue = Union[float, int, str, bool]
FieldsType = Union[FieldValue, Mapping[str, FieldValue]]


class InfluxDbPusherBase:

    def __init__(self):
        pass

    def __call__(self,
                 metric: str,
                 fields: FieldsType,
                 tags: Optional[Mapping[str, str]]):
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError


class NullInfluxDbPusher(InfluxDbPusherBase):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("influxdbpusher")

    def __call__(self,
                 metric: str,
                 fields: FieldsType,
                 tags: Optional[Mapping[str, str]]):
        self.logger.debug("NullInfluxDbPusher: %s %s = %r",
                          metric, tags, fields)

    async def close(self):
        pass


def _escape_tag(tag: str) -> str:
    if not isinstance(tag, str):
        raise TypeError
    return tag.replace(
        "\\", "\\\\"
    ).replace(
        " ", "\\ "
    ).replace(
        ",", "\\,"
    ).replace(
        "=", "\\="
    )


def _format_field_value(value):
    if isinstance(value, (float, bool, int)):
        return str(value)
    if isinstance(value, str):
        return '"' + value.replace('"', '\\"') + '"'
    raise TypeError("unsupported field value type: {!r}".format(value))


def _format_sample(item):
    ts, metric, tags, fields = item
    timestamp = int(ts * 1e9)

    if tags:
        escaped = {_escape_tag(k): _escape_tag(v)
                   for k, v in tags.items()}
        formatted_tags = (',' + ','.join("{}={}".format(k, v)
                                         for k, v in escaped.items()))
    else:
        formatted_tags = ''
    if not isinstance(fields, Mapping):
        fields = {'value': fields}
    formatted_fields = ",".join(
        "{name}={val}".format(name=name, val=_format_field_value(val))
        for name, val in fields.items())
    line = ("{metric}{formatted_tags} {formatted_fields} {timestamp}"
            .format(metric=metric, formatted_tags=formatted_tags,
                    formatted_fields=formatted_fields, timestamp=timestamp))
    # print(line)
    return line


class InfluxDbPusher(InfluxDbPusherBase):

    def __init__(self, url, dbname, *, loop=None):
        super().__init__()
        self.url = url
        self.dbname = dbname
        self._loop = loop
        self._http_session = aiohttp.ClientSession()
        self._queue = Queue(SEND_QUEUE_MAX_SIZE, loop=loop)
        self.logger = logging.getLogger("influxdbpusher")
        self._min_size_reached = Event()
        self._max_size_reached = Event()
        self._push_task = Task(self._push_data_loop(), loop=loop)

    def __call__(self,
                 metric: str,
                 fields: FieldsType,
                 tags: Optional[Mapping[str, str]]=None):
        self.logger.debug("InfluxDbPusher: %s %s = %r",
                          metric, tags, fields)
        if not isinstance(metric, str):
            raise TypeError
        if not isinstance(fields, (Mapping, int, bool, float, str)):
            raise TypeError
        if tags:
            for tag_name, tag_value in tags.items():
                if not isinstance(tag_name, str):
                    raise TypeError
                if not isinstance(tag_value, str):
                    raise TypeError
        self._queue.put_nowait((time.time(), metric, tags, fields))
        qsize = self._queue.qsize()
        if qsize >= SEND_MAX_CHUNK_SIZE:
            self._max_size_reached.set()
        if qsize >= SEND_MIN_CHUNK_SIZE:
            self._min_size_reached.set()

    async def _push_data_loop(self):
        while True:
            try:
                try:
                    await asyncio.wait_for(self._max_size_reached.wait(),
                                           SEND_MIN_INTERVAL,
                                           loop=self._loop)
                except TimeoutError:
                    if self._queue.qsize() < SEND_MIN_CHUNK_SIZE:
                        try:
                            await asyncio.wait_for(
                                self._min_size_reached.wait(),
                                SEND_MAX_INTERVAL - SEND_MIN_INTERVAL,
                                loop=self._loop)
                        except TimeoutError:
                            pass
                quit = await self._transmit_samples()
                if quit:
                    return
            except Exception:
                self.logger.exception("Error in push task")

    async def _transmit_samples(self):
        self._max_size_reached.clear()
        self._min_size_reached.clear()
        send_list = []
        quit = False
        while len(send_list) < SEND_MAX_CHUNK_SIZE:
            try:
                item = self._queue.get_nowait()
            except QueueEmpty:
                break
            if item == 'quit':
                quit = True
                break
            send_list.append(_format_sample(item))
        if not send_list:
            return quit
        # print("to send: {}; quit={}".format(send_list, quit))
        # send it
        url = "{url}/write?db={dbname}".format(url=self.url,
                                               dbname=self.dbname)
        data = '\n'.join(send_list)
        for _ in range(100):
            async with self._http_session.post(url, data=data) as resp:
                if 200 <= resp.status < 300:
                    # self.logger.debug("Successfully sent data to url %s:\n%s",
                    #                   url, data)
                    break
                self.logger.warning("Error sending data to url %s: %s",
                                    url, await resp.text())
                await sleep(1)
        return quit

    async def close(self):
        """
        Waits for all the samples to be flushed to carbon, then finishes the
        task and returns.
        """
        self.logger.debug("Shutting down influxdb pusher %r", self)
        await self._queue.put('quit')
        await self._push_task
        self._http_session.close()


async def test():
    logging.basicConfig(level=logging.DEBUG)
    influx = InfluxDbPusher("http://influxdb:8086", "playground")
    while True:
        for dummy in range(10):
            await sleep(0.02)
            influx("test", dummy, {"foo": "bar"})
            influx("measurement1",
                   {"fieldname1": 'hello "world"', "value": 2.0},
                   {"foo": "bar"})
        await sleep(5)
    await influx.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(test())
