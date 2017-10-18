"""
An asynchronous queue for Google Appengine Task Queues
"""
import asyncio
import datetime
import json
import logging

import ujson
from gcloud.aio.auth import Token
from gcloud.aio.core.http import delete
from gcloud.aio.core.http import get
from gcloud.aio.core.http import HttpError
from gcloud.aio.core.http import patch
from gcloud.aio.core.http import post
from gcloud.aio.core.utils.aio import call_later
from gcloud.aio.core.utils.b64 import clean_b64encode


API_ROOT = 'https://www.googleapis.com/taskqueue/v1beta2/projects'
SCOPES = [
    'https://www.googleapis.com/auth/taskqueue',
    'https://www.googleapis.com/auth/taskqueue.consumer',
    'https://www.googleapis.com/auth/cloud-taskqueue',
    'https://www.googleapis.com/auth/cloud-taskqueue.consumer',
]
TASK_QUEUE_URL = '{api_root}/s~{project_name}/taskqueues/{queue_name}/tasks'

log = logging.getLogger(__name__)


def make_insert_body(queue_name: str, payload: dict):

    delta = datetime.datetime.now() - datetime.datetime(1970, 1, 1)
    micro_sec_since_epock = int(delta.total_seconds() * 1000000)
    encoded_payload = clean_b64encode(ujson.dumps(payload))

    return {
        'kind': 'taskqueues#task',
        'queueName': queue_name,
        'payloadBase64': encoded_payload,
        'enqueueTimestamp': micro_sec_since_epock,
        'leaseTimestamp': 0,
        'retry_count': 0
    }


def make_renew_body(queue_name: str, id_: str):

    return {
        'kind': 'taskqueues#task',
        'id': id_,
        'queueName': queue_name
    }


class TaskQueue(object):

    """
    An asynchronous Google Task Queue
    """

    def __init__(self, project, service_file, task_queue, session=None,
                 token=None):
        # pylint: disable=too-many-arguments

        self.task_queue = task_queue
        self.service_file = service_file
        self.session = session
        self.token = token or Token(
            project,
            self.service_file,
            session=self.session,
            scopes=SCOPES
        )
        self.url = TASK_QUEUE_URL.format(
            api_root=API_ROOT,
            project_name=project,
            queue_name=task_queue
        )

    async def insert_task(self, payload, tag='', session=None):

        session = session or self.session

        if tag:
            payload['tag'] = tag

        body = make_insert_body(self.task_queue, payload)

        token = await self.token.get()

        status, content = await post(
            self.url,
            payload=body,
            session=session,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )

        success = status >= 200 and status < 300

        if not success:
            log.error('Could not insert task into %s: %s', self.task_queue,
                      content)

        return success

    async def get_stats(self, session=None):

        """
        get the task queue statistics
        """

        session = session or self.session

        token = await self.token.get()

        status, content = await get(
            '/'.join(self.url.split('/')[:-1]),
            params={'getStats': 'true'},
            headers={'Authorization': 'Bearer {}'.format(token)},
            session=session
        )

        if 200 <= status < 300:
            return content

        raise HttpError('Could not get stats for {} -> {}: {}'.format(
            self.task_queue,
            status,
            content
        ))

    async def delete_task(self, id_, session=None):

        session = session or self.session

        token = await self.token.get()

        url = '{}/{}'.format(self.url, id_)

        status, phrase = await delete(
            url,
            headers={'Authorization': 'Bearer {}'.format(token)},
            session=session
        )

        if 200 <= status < 300:
            return True

        log.error('Error deleting task %s -> %s: %s', id_, status, phrase)

    async def lease_task(self, lease_seconds=60, num_tasks=1, tag=None,
                         session=None):

        """
        lease a task or tasks from the task queue
        """

        session = session or self.session

        token = await self.token.get()

        url = '{}/{}'.format(self.url, 'lease')

        params = {
            'alt': 'json',
            'leaseSecs': lease_seconds,
            'numTasks': num_tasks
        }

        if tag:
            params.update({
                'groupByTag': 'true',
                'tag': tag
            })

        status, content = await post(
            url,
            headers={'Authorization': 'Bearer {}'.format(token)},
            params=params,
            session=session
        )

        if status < 200 or status >= 300:

            raise Exception('Could not lease a task from {} -> {}: {}'.format(
                self.task_queue,
                status,
                content
            ))

        items = content.get('items', [])

        return items[:num_tasks]

    async def renew_task(self, id_, lease_seconds=60, session=None):

        """
        extend a task lease on the task queue
        """

        session = session or self.session

        token = await self.token.get()

        url = '{}/{}'.format(self.url, id_)

        body = make_renew_body(self.task_queue, id_)

        status, phrase = await patch(
            url,
            payload=body,
            params={'alt': 'json', 'newLeaseSeconds': lease_seconds},
            headers={'Authorization': 'Bearer {}'.format(token)},
            session=session
        )

        was_renewed = status == 200

        if not was_renewed:
            log.error('Could not renew task %s in %s: %s', id_,
                      self.task_queue, phrase)

        return was_renewed


class LocalTaskQueue(object):

    """
    An asynchronous in-memory Task Queue
    """

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument

        self.queue = asyncio.Queue()
        self.leased = {}
        self.ready = {}
        self.deleted = {}

        self.task_queue = kwargs.get('task_queue') or 'q:{}'.format(
            self.next_id()
        )

    @classmethod
    def next_id(cls, name='tqid'):

        name = '_id_{}'.format(name)
        val = getattr(cls, name, 0) + 1
        setattr(cls, name, val)

        return val

    @staticmethod
    def make_task(payload, retry_count=0):

        task = {
            'id': LocalTaskQueue.next_id('tid'),
            'retry_count': retry_count,
            'payloadBase64': clean_b64encode(
                json.dumps(payload).encode('utf-8')
            )
        }

        return task

    async def _make_ready(self, task, bump=False):

        if bump:
            task['retry_count'] = task.get('retry_count', 0) + 1

        self.ready[task['id']] = task

        await self.queue.put(task)

    async def _unlease(self, task):

        if task['id'] not in self.leased:
            return

        del self.leased[task['id']]

        await self._make_ready(task, bump=True)

    async def get_stats(self):

        return {
            'qsize': self.queue.qsize(),
            'ready': len(self.ready),
            'leased': len(self.leased),
            'deleted': len(self.deleted)
        }

    async def insert_task(self, payload):

        task = LocalTaskQueue.make_task(payload)

        await self._make_ready(task)

        log.info('Inserted task.')

    async def delete_task(self, id_):

        if id_ in self.leased:
            del self.leased[id_]

        if id_ in self.ready:
            task = self.ready[id_]
            del self.ready[id_]
            self.deleted[id_] = task

        await asyncio.sleep(0)

    async def lease_task(self, lease_seconds=60, num_tasks=1):

        await asyncio.sleep(0)

        tasks = []

        while len(tasks) < num_tasks:

            try:
                task = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            if task['id'] in self.deleted:
                del self.deleted[task['id']]
                continue

            del self.ready[task['id']]

            self.leased[task['id']] = (
                call_later(
                    lease_seconds,
                    self._unlease,
                    task
                ),
                task
            )

            tasks.append(task)

        return tasks

    async def renew_task(self, id_, lease_seconds=60):

        if id_ not in self.leased:
            return False

        asyncio_task, task = self.leased[id_]
        asyncio_task.cancel()

        self.leased[id_] = (
            call_later(
                lease_seconds,
                self._unlease,
                task
            ),
            task
        )

        return True


# async def smoke(project, service_file, task_queue):

#     import pprint

#     from utils.b64 import clean_b64decode
#     import aiohttp

#     def deserialize(task):

#         data = clean_b64decode(task['payloadBase64']).decode('utf-8')
#         return json.loads(data)

#     with aiohttp.ClientSession() as session:

#         tq = TaskQueue(
#             project,
#             service_file,
#             task_queue,
#             session=session
#         )
#         payload = {'this': {'is': {'a': {'test': uuid.uuid4().hex}}}}
#         tag = 'smoke-test'

#         # INSERT

#         result = await tq.insert_task(payload, tag=tag)
#         print('insert success: {}'.format(result))

#         # STATS

#         stats = await tq.get_stats()
#         print('stats: {}'.format(len(stats['items'])))

#         # LEASE

#         tasks = await tq.lease_task(lease_seconds=10, num_tasks=1)
#         if tasks:
#             print('leased: {}'.format(pprint.pformat(tasks[0])))
#             payload = deserialize(tasks[0])
#             print('payload: {}'.format(payload))

#         # RENEW

#         task_id = tasks[0]['id']
#         result = await tq.renew_task(task_id, lease_seconds=10)
#         print('renew result: {}'.format(result))

#         # DELETE

#         result = await tq.delete_task(task_id)
#         print('delete result: {}'.format(result))


# if __name__ == '__main__':

#     import sys
#     import uuid

#     from utils.aio import fire

#     args = sys.argv[1:]

#     if not args or args[0] != 'smoke':
#         exit(1)

#     project = 'talkiq-integration'
#     service_file = 'service-integration.json'
#     task_queue = 'test-pull'
#     loop = asyncio.get_event_loop()

#     task = fire(
#         smoke,
#         project,
#         service_file,
#         task_queue
#     )

#     loop.run_until_complete(task)
