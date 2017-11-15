##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Server Type
"""
from zope.interface import Interface, implementer


class IServerType(Interface):
    """Server type utility.

    This is a pure read-only interface, since the values are set through
    a ZCML directive and we shouldn't be able to change them.
    """

    def create(name, task_dispatcher, db, port=None, verbose=None, ip=None):
        """Create the server knowing the port, task dispatcher and the ZODB.

        Returns the new server.
        """


@implementer(IServerType)
class ServerType(object):

    def __init__(self, factory, requestFactory, logFactory,
                 defaultPort, defaultVerbose, defaultIP=''):
        self._factory = factory
        self._requestFactory = requestFactory
        self._logFactory = logFactory
        self._defaultPort = defaultPort
        self._defaultVerbose = defaultVerbose
        self._defaultIP = defaultIP


    def create(self, name, task_dispatcher, db, port=None,
               verbose=None, ip=None):
        'See IServerType'

        request_factory = self._requestFactory(db)

        if port is None:
            port = self._defaultPort

        if ip is None:
            ip = self._defaultIP

        if verbose is None:
            verbose = self._defaultVerbose

        return self._factory(request_factory, name, ip, port,
                      task_dispatcher=task_dispatcher,
                      verbose=verbose,
                      hit_log=self._logFactory(),
                      )
