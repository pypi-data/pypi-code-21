#!/usr/bin/python

import json


class Entity(object):

    EntityResource = "Entities"

    def __init__(self):
        self.Id = ""
        pass

    def serialize(self):
        return json.dumps(self.__dict__)
