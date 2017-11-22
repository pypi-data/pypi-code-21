# -*- coding: UTF-8 -*-
from uuid import uuid4


class MockResult(object):
    """
    A fake object that mimics the result object.
    """
    def __init__(self, result):
        self.id = unicode(uuid4())
        self.result = result

    def get(self, *args, **kwargs):
        return self.result

    wait = get  # Deprecated old syntax
