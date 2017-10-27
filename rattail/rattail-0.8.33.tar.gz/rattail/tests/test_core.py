# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from rattail import core


class TestCore(TestCase):

    def test_get_uuid(self):
        uuid = core.get_uuid()
        self.assertTrue(isinstance(uuid, str))
        self.assertEqual(len(uuid), 32)
