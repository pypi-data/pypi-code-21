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
"""Tests for zope.app.server.servertype
"""
import doctest

from zope.interface.verify import verifyObject


def doctest_ServerType():
    r"""Tests for ServerType

    Zope 3 has many server types -- HTTP, FTP, HTTP with postmortem debugging,
    etc.  All of them are registered as IServerType utilities in ZCML.

    ServerType is an implementation of IServerType.  The constructor of
    ServerType takes quite a few arguments, a number of which are factories.
    We will use stubs of those.

    The 'factory' argument specifies the server factory (e.g.
    PublisherHTTPServer from zope.server.http.httpserver)

        >>> def factory(request_factory, name, ip, port,
        ...             task_dispatcher=None, hit_log=None, verbose=False):
        ...     if ip == '':
        ...         ip = '*' # listen on all network interfaces
        ...     print("Starting a server (%s) on %s:%d" % (name, ip, port))
        ...     print("This server will use %s to construct requests" %
        ...           request_factory)
        ...     print("This server will use %s for hit logging" % hit_log)
        ...     if verbose:
        ...         print("This server will be verbose")
        ...     else:
        ...         print("This server will not be verbose")
        ...     print("This server will be managed by %s" % task_dispatcher)

    The 'requestFactory' argument specifies a function that returns a factory
    for requests (e.g.  HTTPPublicationRequestFactory from
    zope.server.http.publisherhttpserver).  It is, in fact, a request factory
    factory.

        >>> def requestFactory(db):
        ...     return 'my request factory for %s' % db

    The 'logFactory' argument specifies the factory for an access logger (e.g.
    CommonAccessLogger from zope.server.http.commonaccesslogger).

        >>> def logFactory():
        ...     return 'my logger'

    The 'defaultPort' argument specifies the default TCP port number for the
    server.

    The 'defaultVerbose' argument specifies the default verbosity.

    The 'defaultIP' argument specifies the network interface for listening on.
    You can specify the network interface IP address, or an empty string if you
    want to listen on all interfaces.

        >>> from zope.app.server.servertype import IServerType
        >>> from zope.app.server.servertype import ServerType
        >>> st = ServerType(factory, requestFactory, logFactory,
        ...                 defaultPort=8080, defaultVerbose=False)
        >>> verifyObject(IServerType, st)
        True

    A server type is then registered as a named utility.  These utilities are
    used while interpreting <server> sections of zope.conf to create instances
    of servers listening on a specific port.

    When you create an instance of a server, you need to tell it the task
    dispatcher (see IDispatcher in zope.server.interfaces), and the ZODB
    database object.

    The `name` argument to create is, as far as I can tell, purely informative.
    It is used to construct a server identifier that appears in log files and,
    for example, the 'Server' HTTP header.

        >>> dispatcher = 'my task dispatcher'
        >>> db = 'my database'
        >>> st.create('Sample Server', dispatcher, db)
        Starting a server (Sample Server) on *:8080
        This server will use my request factory for my database to construct requests
        This server will use my logger for hit logging
        This server will not be verbose
        This server will be managed by my task dispatcher

    You can, of course, create multiple instances of the same server type, and
    bind them to different ports.

        >>> st.create('Sample Server 2', dispatcher, db, port=1234, verbose=True)
        Starting a server (Sample Server 2) on *:1234
        This server will use my request factory for my database to construct requests
        This server will use my logger for hit logging
        This server will be verbose
        This server will be managed by my task dispatcher

        >>> st.create('Sample Server 3', dispatcher, db, port=9090,
        ...           ip='127.0.0.1')
        Starting a server (Sample Server 3) on 127.0.0.1:9090
        This server will use my request factory for my database to construct requests
        This server will use my logger for hit logging
        This server will not be verbose
        This server will be managed by my task dispatcher

    """


def test_suite():
    return doctest.DocTestSuite()
