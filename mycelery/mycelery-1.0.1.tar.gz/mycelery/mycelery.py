#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

from bson import Binary
from celery.backends.mongodb import MongoBackend


__all__ = ['MongoCustomBackend']


class MongoCustomBackend(MongoBackend):

    def _store_result(self, task_id, result, status, traceback=None, request=None, **kwargs):
        """Store return value and status of an executed task."""
        meta = {'_id': task_id,
                'task_name': request.task if request else None,
                'status': status,
                'result': str(result),
                'date_done': datetime.now(),
                'args': request.args if request else None,
                'traceback': str(traceback),
                'children': Binary(self.encode(self.current_task_children(request), )),
                }
        self.collection.save(meta)

        return result

    def _save_group(self, group_id, result):
        """Save the group result."""
        meta = {
            '_id': group_id,
            'result': [{'id': i.id, 'status': i.status, 'result': i.result} for i in result.results],
            'date_done': datetime.now()
        }
        self.collection.save(meta)

        return result
