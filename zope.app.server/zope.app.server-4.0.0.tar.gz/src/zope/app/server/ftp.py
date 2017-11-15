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
"""FTP server
"""
from zope.app.publication.ftp import FTPPublication
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.publisher.ftp import FTPRequest
from zope.server.ftp.logger import CommonFTPActivityLogger
from zope.server.ftp.publisher import PublisherFTPServer
from zope.app.server.servertype import ServerType
import zope.interface


@zope.interface.implementer(IPublicationRequestFactory)
class FTPRequestFactory(object):
    """FTP Request factory

    FTP request factories for a given database create FTP requests with
    publications on the given database:

    .. The test below has been disabled and moved to test_ftp.py (LP #257954)

      >>> from ZODB.tests.util import DB
      >>> db = DB()
      >>> factory = FTPRequestFactory(db)
      >>> from io import BytesIO
      >>> request = factory(BytesIO(b''), {'credentials': None, 'path': '/'})
      >>> request.publication.db is db
      True
      >>> db.close()

    """

    def __init__(self, db):
        self.publication = FTPPublication(db)

    def __call__(self, input_stream, env):
        request = FTPRequest(input_stream, env)
        request.setPublication(self.publication)
        return request


server = ServerType(
    PublisherFTPServer,
    FTPRequestFactory,
    CommonFTPActivityLogger,
    8021, True)
