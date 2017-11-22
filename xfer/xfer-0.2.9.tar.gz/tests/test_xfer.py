#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# testing for coda
# 
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imporobj
# -------
import unittest
import os
import uuid
import glob
import getpass
import shutil
import subprocess

from xfer import cli, __version__
from . import __base__


def tmpfile(ext, directory=__base__):
    tbase = '.xfer-tmp-' + str(uuid.uuid1()) + ext
    if not os.path.exists(directory):
        os.makedirs(directory)
        cli.run('git init', cwd=directory)
    tf = os.path.join(directory, tbase)
    open(tf, 'a').close()
    return tf


def tearDown():
    for fi in glob.glob(os.path.join(__base__, '.xfer-tmp*')):
        if os.path.isdir(fi):
            shutil.rmtree(fi)
        else:
            os.remove(fi)
    return


# session
# -------
class TestEntryPoints(unittest.TestCase):
    config = os.path.join(__base__, '.git', 'xfer')
    remote = 'testing'
    port = 2222
    location = '/tmp/git-xfer'

    def setUp(self):
        user = getpass.getuser()
        remote = 'ssh://{}@localhost:{}{}.git'.format(user, self.port, self.location)
        cli.run('git remote add {} {}'.format(self.remote, remote))
        if not os.path.exists(self.location):
            os.makedirs(self.location)
        cli.run('git init', cwd=self.location)
        return

    def tearDown(self):
        cli.run('git remote remove {}'.format(self.remote))
        if os.path.exists(self.config):
            os.remove(self.config)
        if os.path.exists(self.location):
            shutil.rmtree(self.location)
        return

    @property
    def cache(self):
        if os.path.exists(self.config):
            with open(self.config, 'r') as fi:
                ret = map(lambda x: x.rstrip(), fi.readlines())
        else:
            ret = []
        return ret

    def call(self, subcommand, cwd=__base__, *args):
        return subprocess.check_output('PYTHONPATH={} python -m xfer {} {}'.format(
            __base__, subcommand, ' '.join(args)
        ), stderr=subprocess.STDOUT, shell=True, cwd=cwd)

    def test_version(self):
        res = self.call('version')
        self.assertTrue(res, __version__)
        return

    def test_add(self):
        self.call('add {}'.format(os.path.join(__base__, 'setup.cfg')))
        self.assertTrue('setup.cfg' in self.cache)
        self.call('add {}'.format(os.path.join(__base__, 'tests')))
        self.assertTrue('tests/test_xfer.py' in self.cache)
        return

    def test_list(self):
        self.call('add {}'.format(os.path.join(__base__, 'setup.cfg')))
        self.call('add {}'.format(os.path.join(__base__, 'tests')))
        listing = self.call('list')
        listing = listing.rstrip().split('\n')
        self.assertTrue('setup.cfg' in listing)
        self.assertTrue('tests/test_xfer.py' in listing)
        return

    def test_prune(self):
        tmp = tmpfile('.txt')
        self.call('add {}'.format(tmp))
        self.assertTrue(os.path.basename(tmp) in self.cache)
        os.remove(tmp)
        self.assertTrue(os.path.basename(tmp) in self.cache)
        self.call('prune')
        self.assertFalse(os.path.basename(tmp) in self.cache)
        return

    def test_reset(self):
        self.call('add {}'.format(os.path.join(__base__, 'setup.cfg')))
        self.assertTrue(os.path.exists(os.path.join(__base__, '.git', 'xfer'))) 
        self.call('reset')
        self.assertFalse(os.path.exists(os.path.join(__base__, '.git', 'xfer')))
        return

    def test_remove(self):
        self.call('add {}'.format(os.path.join(__base__, 'setup.cfg')))
        self.assertTrue('setup.cfg' in self.cache)
        self.call('remove {}'.format(os.path.join(__base__, 'setup.cfg')))
        self.assertFalse('setup.cfg' in self.cache)
        self.call('add {}'.format(os.path.join(__base__, 'tests')))
        self.assertTrue('tests/test_xfer.py' in self.cache)
        self.call('remove {}'.format(os.path.join(__base__, 'tests')))
        self.assertFalse('tests/test_xfer.py' in self.cache)
        return

    def test_rm(self):
        tmp = tmpfile('.txt')
        self.call('add {}'.format(tmp))
        self.assertTrue(os.path.exists(tmp))
        self.assertTrue(os.path.basename(tmp) in self.cache)
        self.call('rm {}'.format(tmp))
        self.assertFalse(os.path.basename(tmp) in self.cache)
        self.assertFalse(os.path.exists(tmp))
        return

    def test_diff(self):
        tmp = tmpfile('.txt')
        self.call('add {}'.format(tmp))
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual('< {}'.format(os.path.basename(tmp)), res)
        rtmp = tmpfile('.txt', directory=self.location)
        self.call('add {}'.format(rtmp), cwd=self.location)
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual('< {}\n> {}'.format(
            os.path.basename(tmp),
            os.path.basename(rtmp)
        ), res)
        self.call('remove {}'.format(tmp))
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual('> {}'.format(os.path.basename(rtmp)), res)
        return

    def test_push(self):
        self.call('add {}'.format(os.path.join(__base__, 'setup.cfg')))
        self.call('add {}'.format(os.path.join(__base__, 'tests/*.py')))
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual(len(res.split('\n')), 3)
        self.call('push {}'.format(self.remote))
        self.assertTrue(os.path.exists(os.path.join(self.location, 'setup.cfg')))
        self.assertTrue(os.path.exists(os.path.join(self.location, 'tests', 'test_xfer.py')))
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual(res, '')
        return

    def test_pull(self):
        tmp = tmpfile('.txt', directory=self.location)
        tmpdir = os.path.join(self.location, '.xfer-tmp')
        ntmp = tmpfile('.txt', directory=tmpdir)
        self.call('add {}'.format(tmp), cwd=self.location)
        self.call('add {}'.format(ntmp), cwd=self.location)
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual(len(res.split('\n')), 2)
        self.call('pull {}'.format(self.remote))
        self.assertTrue(os.path.exists(os.path.basename(tmp)))
        self.assertTrue(os.path.exists('.xfer-tmp/{}'.format(os.path.basename(ntmp))))
        res = self.call('diff {}'.format(self.remote)).rstrip()
        self.assertEqual(res, '')
        return



# exec
# ----
if __name__ == '__main__':
    unittest.main()
