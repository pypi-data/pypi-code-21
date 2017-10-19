# -*- coding: utf-8 -*-
from sqlalchemy.types import UserDefinedType, Text
from diandao.djson import JSON


class JSONSerializer(Text):
    """JSON序列化数据格式.

    """
    __visit_name__ = 'text'

    def bind_processor(self, dialect):
        def process(value):
            return JSON.stringify(value)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return JSON.parse(value)

        return process
