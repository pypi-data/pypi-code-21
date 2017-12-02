# -*- coding: utf-8 -*-

import inspect

import enum
from django.test import Client
import json


class ChoiceEnum(enum.Enum):
    """
    封装enum，可以在Model中的choice中使用
    """
    @classmethod
    def choices(cls):
        user_members = inspect.getmembers(object=cls, predicate=lambda m: not inspect.isroutine(m))
        props = [m for m in user_members if not (m[0][:2] == '__')]
        choices = tuple((m[1].name, m[1].value) for m in props)
        return choices


class CustomClient(Client):
    """
    继承了Django中的Client，添加两种json的方法
    """
    def json_get(self, path, data=None):
        data = data or {}
        if '?' not in path:
            path += '?'
        response = self.get(path, data)
        return json.loads(response.content)

    def json_post(self, path, data=None):
        data = data or {}
        response = self.post(path, data)
        return json.loads(response.content)
