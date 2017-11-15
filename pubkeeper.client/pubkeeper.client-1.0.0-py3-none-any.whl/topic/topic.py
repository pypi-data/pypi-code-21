"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.logging import get_logger
from threading import RLock


class Topic(object):
    def __init__(self, topic, crypto=True):
        self.logger = get_logger(self.__class__.__name__)
        self.topic = topic
        self.topic_lock = RLock()
        self.crypto = crypto

        self.brews = []
        self.brew_alias = {}

    def add_brew_alias(self, alias, brew):
        with self.topic_lock:
            self.brew_alias[alias] = brew

    def remove_brew_alias(self, alias):
        with self.topic_lock:
            if alias in self.brew_alias:
                del(self.brew_alias[alias])

    def get_brew(self, name):
        with self.topic_lock:
            if name in self.brew_alias:
                return self.brew_alias[name]
            else:
                for brew in self.brews:
                    if brew.name == name:
                        return brew
