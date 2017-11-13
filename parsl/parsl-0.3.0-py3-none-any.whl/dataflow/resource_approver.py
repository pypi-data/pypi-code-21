#!/usr/bin/env python3

import time
import threading
import logging

logger = logging.getLogger(__name__)

class Cron (object):

    def __init__ (self, fn, interval, freq_fn=None, *args, **kwargs):

        self.fn = fn

        # If freq_fn is given use it, else use a lambda that returns the interval
        self.freq_fn = freq_fn if freq_fn else lambda x: x

        self.interval = interval
        self.fn_args = args
        self.fn_kwargs = kwargs
        self.timer = None
        self.caller()


    def caller(self):

        print("At caller at time : ", time.time())
        rtn = self.fn(*self.fn_args, **self.fn_kwargs)
        self.interval = self.freq_fn(self.interval)
        self.timer = threading.Timer( self.interval,
                                      self.caller )
        self.timer.start()

    def cancel(self):
        self.timer.cancel()


def foo ( ):
    print("Hi")

runner = Cron(foo, 1)
