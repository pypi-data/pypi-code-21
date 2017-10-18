#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from six import text_type

from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin

from zope.testing import cleanup

class SchemaLayer(ZopeComponentLayer,
                  ConfiguringLayerMixin):

    set_up_packages = ('nti.schema',)

    @classmethod
    def setUp(cls):
        cls.setUpPackages()

    @classmethod
    def tearDown(cls):
        cls.tearDownPackages()
        cleanup.cleanUp()

    @classmethod
    def testSetUp(cls, test=None):
        pass

    testTearDown = testSetUp

from zope.interface import Interface, classImplements

class IUnicode(Interface):
    "Unicode strings"


classImplements(text_type, IUnicode)
