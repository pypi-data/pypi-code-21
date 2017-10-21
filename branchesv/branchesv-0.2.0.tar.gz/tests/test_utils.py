# coding: utf-8
import os
import spur
import shlex
import logging
import simplejson as json
from unittest import TestCase
from branchesv import utils, branches

logger = logging.getLogger('deployv')


class TestUtils(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gitbranch = branches.GitBranch()
        cls.shell = spur.LocalShell()
        cls.shell.run(shlex.split('git clone https://github.com/Vauxoo/deploy-templates.git'
                                  ' test_utils/deploy-templates'))
        cls.original_branches = cls.gitbranch.get_branches('test_utils')

    def test_10_load_json(self):
        res = utils.load_json('tests/files/branches.json')
        self.assertTrue(res)
        self.assertIsInstance(res, list)

    def test_15_load_json_exception(self):
        with self.assertRaises(IOError):
            utils.load_json('testing/config')

    def test_20_save_json(self):
        content = utils.load_json('tests/files/branches.json')
        res = utils.save_json(content, 'test_utils/save_test.json')
        new_json = utils.load_json('test_utils/save_test.json')
        self.assertTrue(os.path.exists(res))
        self.assertEquals(content, new_json)

    def test_25_save_json_exception(self):
        with self.assertRaises(IOError):
            res = utils.save_json('info', 'testing/test.json')

    def test_30_simplify_path(self):
        copy_branches = utils.copy_list_dicts(self.original_branches)
        res = utils.simplify_path(copy_branches)
        full_path = 'test_utils/{path}'.format(path=res[0].get('path'))
        self.assertNotEqual(res[0].get('path'), self.original_branches[0].get('path'))
        self.assertEquals(full_path, self.original_branches[0].get('path'))
        self.assertEquals(len(res[0].get('path').split('/')), 1)

    def test_40_name_from_url(self):
        res = utils.name_from_url('https://github.com/odoo/odoo.git')
        self.assertEqual(res, 'odoo')

    def test_50_copy_list_dicts(self):
        copy = utils.copy_list_dicts(self.original_branches)
        self.assertEquals(copy, self.original_branches)
        copy[0].update({'name': 'new_name'})
        self.assertNotEqual(copy, self.original_branches)

    def test_60_set_message(self):
        res_success = utils.set_message(self.original_branches[0])
        res_fatal = utils.set_message(self.original_branches[0], 'fatal: no such branch')
        self.assertEquals(res_success.get('exit_code'), 0)
        self.assertEquals(res_fatal.get('exit_code'), 1)

    def test_90_clean_files(self):
        files = ['/', 'test_utils/save_test.json', 'test_utils/']
        utils.clean_files(files)
        self.assertFalse(os.path.exists('test_utils/save_test.json'))
        self.assertFalse(os.path.exists('test_utils/'))
        self.assertTrue(os.path.exists('/'))
