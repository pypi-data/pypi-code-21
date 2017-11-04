#!/usr/bin/env python
# -*- coding: utf-8 -*-
from blinker import signal, Namespace, NamedSignal
from yosaipy2.core.event.abcs import EventBus
from typing import Dict
from functools import wraps


class BlinkerEventBus(EventBus):
    def __init__(self):
        # type: (str) -> None
        self.AUTO_TOPIC = "blinker_eventbus_auto_topic"
        self._signals = {}  # type: Dict[NamedSignal]

    def send_message(self, topic_name, **kwargs):
        if topic_name not in self._signals:
            sig = signal(topic_name)
            self._signals[topic_name] = sig
        else:
            sig = self._signals[topic_name]
        sig.send(None, **kwargs)

    def subscribe(self, func, topic_name):
        if topic_name not in self._signals:
            sig = signal(topic_name)
            self._signals[topic_name] = sig
        else:
            sig = self._signals[topic_name]
        callback = self._adapter(func, topic_name)
        sig.connect(callback)

    def unsubscribe(self, listener, topic_name):
        pass

    @staticmethod
    def _adapter(func, topic_name):
        @wraps(func)
        def callback(sender, **kwargs):
            func(topic=topic_name, **kwargs)

        return callback

    def isSubscribed(self, listener, topic_name):
        if topic_name not in self._signals:
            return False
        return True


event_bus = BlinkerEventBus()
