##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Doc tests for the FTP server.
"""

import unittest
from io import BytesIO


class Tests(unittest.TestCase):

    def test_ftp(self):
        from ZODB.tests.util import DB
        from zope.app.server.ftp import FTPRequestFactory
        db = DB()
        factory = FTPRequestFactory(db)
        request = factory(BytesIO(b''), {'credentials': None, 'path': '/'})
        self.assertTrue(request.publication.db is db)
        db.close()
