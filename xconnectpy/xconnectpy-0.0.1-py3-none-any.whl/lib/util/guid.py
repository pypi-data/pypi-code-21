#!/usr/bin/python

from uuid import uuid4


class Guid:

    def __init__(self):
        pass

    @staticmethod
    def generate():
        return str(uuid4())
