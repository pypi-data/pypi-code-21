import json
import unittest

import rx

from dxpy.task.database.config import config as c
from dxpy.task import database as db
from dxpy.task.database.model import TaskDB

from dxpy.task.exceptions import TaskNotFoundError


class TestDataBase(unittest.TestCase):
    def setUp(self):
        c['path'] = ':memory:'
        c['use_web_api'] = False
        db.Database.create()
        self.dummy_dct = {
            '__task__': True,
            'id': 1,
            'desc': 'dummpy task',
            'data': {},
            'time_stamp': {
                'create': "2017-09-22 12:57:44.036185",
                'start': None,
                'end': None,
            },
            'is_root': True,
            'state': 'BeforeSubmit',
            'workdir': '/tmp/test',
            'worker': 'Slurm',
            'dependency': [],
            'type': 'Regular'
        }
        self.dummy_json = json.dumps(self.dummy_dct)
        self.dummy_id = db.create(self.dummy_json)
        self.modify_id = db.create(self.dummy_json)
        self.delete_id = db.create(self.dummy_json)

    def tearDown(self):
        db.Database.clear()
        c.back_to_default()

    def test_create(self):
        tid = db.create(self.dummy_json)
        self.assertIsInstance(tid, int)

    def test_creat_json(self):
        dct = {"__task__": True,
               "id": 1,
               "desc": "test",
               "workdir": "/home/hongxwing/Workspace/dxl/tests_dxpy/task",
               "worker": "NoAction",
               "type": "Regular",
               "state": "BeforeSubmit",
               "dependency": [],
               "time_stamp": {"create": "2017-10-02 05:15:56.349184", "start": None, "end": None},
               "is_root": False,
               "data": {}}
        s = json.dumps(dct)

        tid = db.create(s)

    def test_read(self):
        # TODO: add desired output json
        t = db.read(self.dummy_id)
        self.assertIsInstance(t, str)
        dct = json.loads(t)
        self.assertTrue(dct['__task__'])
        self.assertIsInstance(dct['data'], dict)

    def test_read_invalid_tid(self):
        invalid_tid = self.dummy_id + 1000
        with self.assertRaises(TaskNotFoundError):
            t = db.read(invalid_tid)

    def test_read_all(self):
        t_all = db.read_all()
        self.assertIsInstance(t_all, rx.Observable)
        t_list = (t_all
                  .subscribe_on(rx.concurrency.ThreadPoolScheduler())
                  .to_list()
                  .to_blocking().first())
        self.assertIsInstance(t_list, list)

    def test_update(self):
        new_dct = json.loads(db.read(self.modify_id))
        new_dct['desc'] = 'modified'
        db.update(json.dumps(new_dct))
        data = json.loads(db.read(self.modify_id))
        self.assertEqual(data['desc'], "modified")

    def test_delete(self):
        db.read(self.delete_id)
        db.delete(self.delete_id)
        with self.assertRaises(TaskNotFoundError):
            db.read(self.delete_id)
