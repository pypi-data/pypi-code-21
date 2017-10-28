# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.tests import DataTestCase


class TestModelBase(DataTestCase):

    def test_repr(self):
        # We test this via the Setting class for convenience, since it doesn't
        # have a proper `repr()` method of its own.  I started to add an
        # assertion to prove that, but then wasn't sure how to go about it.
        setting = model.Setting()
        self.assertEqual(repr(setting), b"Setting(name=None)")
        setting.name = 'rattail.test.repr'
        self.assertEqual(repr(setting), b"Setting(name=u'rattail.test.repr')")


class TestSetting(DataTestCase):

    def test_unicode(self):
        setting = model.Setting()
        self.assertEqual(unicode(setting), "")
        setting.name = 'rattail.test.unicode'
        self.assertEqual(unicode(setting), "rattail.test.unicode")


class TestChange(DataTestCase):

    def test_repr(self):
        change = model.Change()
        self.assertEqual(repr(change), b"Change(class_name=None, instance_uuid=None, deleted=None)")
        change.class_name = 'Widget'
        self.assertEqual(repr(change), b"Change(class_name=u'Widget', instance_uuid=None, deleted=None)")
        change.object_key = '42'
        self.assertEqual(repr(change), b"Change(class_name=u'Widget', instance_uuid=u'42', deleted=None)")
        change.deleted = False
        self.assertEqual(repr(change), b"Change(class_name=u'Widget', instance_uuid=u'42', deleted=False)")
