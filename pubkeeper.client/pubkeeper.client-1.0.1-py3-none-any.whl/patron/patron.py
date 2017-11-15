"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.topic import Topic


class Patron(Topic):
    def new_brewers(self, brewers):
        raise NotImplementedError()

    def remove_brewer(self, brewer_id):
        raise NotImplementedError()

    def _handle_callback(self, brewer_id, data):
        raise NotImplementedError()
