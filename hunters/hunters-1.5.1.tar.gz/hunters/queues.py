# -*- coding:utf-8 -*-
# Created by qinwei on 2017/9/8
import json
from queue import Queue
from time import sleep, time

from hunters.core import TaskMeta


class TaskMetaJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TaskMeta):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


class Serializer(object):
    """ 队列的序列化接口, 需要实现 """

    def serialize(self, obj):
        raise NotImplementedError("Must implements by subclass")

    def deserialize(self, obj):
        raise NotImplementedError("Must implements by subclass")


class JsonSerializer(Serializer):
    """JSON序列化实现"""

    def serialize(self, obj):
        return json.dumps(obj, ensure_ascii=False, cls=TaskMetaJsonEncoder)

    def deserialize(self, obj):
        return json.loads(obj, encoding="utf-8", object_hook=self.task_meta_parser)

    @staticmethod
    def task_meta_parser(item_):
        if "task_meta" in item_:
            item_['task_meta'] = TaskMeta.from_dict(item_.get("task_meta"))
        return item_


class RedisQueue(Queue):
    """"""

    def __init__(self, redis, namespace, serializer=JsonSerializer()):
        """

        :param redis: redis.Redis()
        :param namespace: str, Distinguish different queues
        """
        self.redis = redis
        self.namespace = namespace
        self.serializer = serializer

    def _get_key(self):
        return "hunter-queue:" + self.namespace

    def qsize(self):
        return self.redis.llen(self._get_key())

    def put(self, data, block=True, timeout=None):
        self.redis.rpush(self._get_key(), self.serializer.serialize(data))
        return True

    def get(self, block=True, timeout=None):
        start = time()
        while True:
            item = self.redis.lpop(self._get_key())
            if item:
                start = time()
                return self.serializer.deserialize(item)
            sleep(0.2)
            if timeout and time() - start > timeout:
                raise TimeoutError("queue block get timeout")


if __name__ == "__main__":
    d = json.dumps(TaskMeta(), ensure_ascii=False, cls=TaskMetaJsonEncoder)
    print(d)
    item = json.loads(r"""{"task_meta": %s }""" % d, object_hook=JsonSerializer.task_meta_parser)
    print(item)
