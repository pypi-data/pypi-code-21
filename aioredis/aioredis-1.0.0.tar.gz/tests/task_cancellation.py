import unittest
import asyncio

from ._testutil import BaseTest, run_until_complete


class CancellationTest(BaseTest):

    @run_until_complete
    @unittest.expectedFailure
    def test_future_cancellation_but_blocks_connection(self):
        conn1 = yield from self.create_connection(
            ('localhost', 6379), loop=self.loop)
        conn2 = yield from self.create_connection(
            ('localhost', 6379), loop=self.loop)

        @asyncio.coroutine
        def task1():
            yield from asyncio.sleep(2, loop=self.loop)
            yield from conn1.execute('LPUSH', 'a_list', 'value')

        sec1, ms = yield from conn2.execute('TIME')
        fut = conn2.execute('BLPOP', 'a_list', 3)
        asyncio.async(task1(), loop=self.loop)
        try:
            yield from asyncio.wait_for(fut, .1, loop=self.loop)
        except asyncio.TimeoutError:
            pass
        self.assertTrue(fut.cancelled())
        # Future is cancelled but connection is blocked
        # with BLPOP timeout

        sec2, ms = yield from conn2.execute('TIME')
        self.assertEqual(int(sec2) - int(sec1), 1)
