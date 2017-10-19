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


def task_meta_parser(item):
    if "task_meta" in item:
        item['task_meta'] = TaskMeta.from_dict(item.get("task_meta"))
    return item


class RedisQueue(Queue):
    """"""

    def __init__(self, redis, namespace):
        """

        :param redis: redis.Redis()
        :param namespace: str, Distinguish different queues
        """
        self.redis = redis
        self.namespace = namespace

    def _get_key(self):
        return "hunter-queue:" + self.namespace

    def qsize(self):
        self.redis.llen(self._get_key())

    def put(self, item, block=True, timeout=None):
        self.redis.rpush(self._get_key(), json.dumps(item, ensure_ascii=False, cls=TaskMetaJsonEncoder))
        return True

    def get(self, block=True, timeout=None):
        start = time()
        while True:
            item = self.redis.lpop(self._get_key())
            if item:
                start = time()
                return json.loads(item, encoding="utf-8", object_hook=task_meta_parser)
            sleep(0.2)
            if timeout and time() - start > timeout:
                raise TimeoutError("queue block get timeout")


if __name__ == "__main__":
    d = json.dumps(TaskMeta(), ensure_ascii=False, cls=TaskMetaJsonEncoder)
    print(d)
    item = json.loads(r"""{"task_meta": %s }""" % d, object_hook=task_meta_parser)
    print(item)
