##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""WSGI-compliant HTTP server setup.
"""

import zope.interface
from zope.server.http.commonaccesslogger import CommonAccessLogger
from zope.server.http import wsgihttpserver

from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.wsgi import WSGIPublisherApplication

from zope.app.server import servertype


@zope.interface.implementer(servertype.IServerType)
class ServerType(object):

    def __init__(self, factory, applicationFactory, logFactory,
                 defaultPort, defaultVerbose, defaultIP='',
                 requestFactory=HTTPPublicationRequestFactory):
        self._factory = factory
        self._applicationFactory = applicationFactory
        self._requestFactory = requestFactory
        self._logFactory = logFactory
        self._defaultPort = defaultPort
        self._defaultVerbose = defaultVerbose
        self._defaultIP = defaultIP


    def create(self, name, task_dispatcher, db, port=None,
               verbose=None, ip=None):
        'See IServerType'

        application = self._applicationFactory(
            db, factory=self._requestFactory)

        if port is None:
            port = self._defaultPort

        if ip is None:
            ip = self._defaultIP

        if verbose is None:
            verbose = self._defaultVerbose

        return self._factory(application, name, ip, port,
                      task_dispatcher=task_dispatcher,
                      verbose=verbose,
                      hit_log=self._logFactory(),
                      )


http = ServerType(wsgihttpserver.WSGIHTTPServer,
                  WSGIPublisherApplication,
                  CommonAccessLogger,
                  8080, True)

pmhttp = ServerType(wsgihttpserver.PMDBWSGIHTTPServer,
                    WSGIPublisherApplication,
                    CommonAccessLogger,
                    8013, True)
