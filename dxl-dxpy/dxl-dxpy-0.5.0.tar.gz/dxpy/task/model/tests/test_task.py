import json
import unittest

from dxpy.task.model import task
from dxpy.time.timestamps import TaskStamp
from dxpy.time.utils import strp


class TestTask(unittest.TestCase):
    def test_to_json(self):
        t = task.Task(tid=10, desc='test', workdir='/tmp/test',
                      worker=task.Worker.MultiThreading,
                      ttype=task.Type.Regular,
                      dependency=[1, 2, 3],
                      time_stamp=TaskStamp(create=strp(
                          "2017-09-22 12:57:44.036185")),
                      data={'sample': 42},
                      is_root=True)
        s = t.to_json()
        dct = json.loads(s)
        self.assertEqual(dct['id'], 10)
        self.assertEqual(dct['desc'], 'test')
        self.assertEqual(dct['dependency'], [1, 2, 3])
        self.assertEqual(dct['data'], {'sample': 42})
        self.assertEqual(dct['type'], 'Regular')
        self.assertEqual(dct['workdir'], '/tmp/test')
        self.assertEqual(dct['worker'], 'MultiThreading')
        self.assertEqual(dct['is_root'], True)
        self.assertEqual(dct['time_stamp'], {
                         'create': "2017-09-22 12:57:44.036185", 'start': None, 'end': None})
        self.assertEqual(dct['state'], 'BeforeSubmit')

    def test_from_json(self):
        dct = {
            '__task__': True,
            'id': 10,
            'desc': 'test',
            'workdir': '/tmp/test',
            'worker': 'Slurm',
            'type': 'Script',
            'dependency': [1, 2, 3],
            'data': {'sample': 42},
            'is_root': True,
            'time_stamp': {
                'create': "2017-09-22 12:57:44.036185",
                'start': None,
                'end': None
            },
            'state': 'BeforeSubmit'
        }
        t = task.Task.from_json(json.dumps(dct))
        self.assertEqual(t.id, 10)
        self.assertEqual(t.desc, 'test')
        self.assertEqual(t.workdir, '/tmp/test')
        self.assertEqual(t.worker, task.Worker.Slurm)
        self.assertEqual(t.type, task.Type.Script)
        self.assertEqual(t.dependency, [1, 2, 3])
        self.assertEqual(t.data, {'sample': 42})
        self.assertEqual(t.is_root, True)
        self.assertEqual(t.time_stamp.create, strp(
            "2017-09-22 12:57:44.036185"))
        self.assertEqual(t.state, task.State.BeforeSubmit)

    def test_submit(self):
        t = task.Task(10, 'test', state=task.State.BeforeSubmit)
        self.assertEqual(t.state, task.State.BeforeSubmit)
        t = task.submit(t)
        self.assertEqual(t.state, task.State.Pending)

    def test_start(self):
        t = task.Task(10, 'test', state=task.State.BeforeSubmit)
        self.assertEqual(t.state, task.State.BeforeSubmit)
        t = task.start(t)
        self.assertEqual(t.state, task.State.Runing)

    def test_complete(self):
        t = task.Task(10, 'test', state=task.State.BeforeSubmit)
        self.assertEqual(t.state, task.State.BeforeSubmit)
        t = task.complete(t)
        self.assertEqual(t.state, task.State.Complete)
