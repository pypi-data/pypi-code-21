#!/usr/bin/python

import json


class Facet(object):

    def __init__(self):
        pass

    def serialize(self):
        return json.dumps(self.__dict__)
