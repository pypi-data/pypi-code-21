# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-sentry monkey patches"""

import logging
from raven.utils.wsgi import get_headers, get_environ

from logilab.common.decorators import monkeypatch
from cubicweb.web.application import CubicWebPublisher
try:
    from pyramid_cubicweb.bwcompat import CubicWebPyramidHandler
    HAS_PYRAMID = True
except ImportError:
    try:
        from cubicweb.pyramid.bwcompat import CubicWebPyramidHandler
        HAS_PYRAMID = True
    except ImportError:
        HAS_PYRAMID = False


logger = logging.getLogger(__name__)
_SENTRY_DSN = None


def add_versions(req, extra):
    if hasattr(req, 'get_versions'):
        versions = req.get_versions()
    elif hasattr(req, 'registry'):
        versions = req.registry['cubicweb.repository'].get_versions()
    else:
        return
    for k, v in versions.items():
        version = '.'.join([str(x) for x in v])
        if k == 'cubicweb':
            extra['release'] = version
        else:
            extra.setdefault('modules', {})[k] = version


def add_sentry_support(dsn):
    """ Add support for Sentry (getsentry.com)
    """
    global _SENTRY_DSN
    if _SENTRY_DSN:
        assert dsn == _SENTRY_DSN
        return
    _SENTRY_DSN = dsn

    from raven import Client
    client = Client(_SENTRY_DSN)

    def handle_error(req):
        extra = {'user': req.user.dc_title(),
                 'useragent': req.useragent(),
                 'url': req.url(),
                 'form': req.form,
                 }
        try:
            extra['referer'] = req.get_header('Referer')
        except KeyError:
            pass
        try:
            add_versions(req, extra)
        except AttributeError:
            pass
        ident = client.get_ident(client.captureException(extra=extra))
        msg = "Exception caught; reference is %s" % ident
        logger.critical(msg)

    cw_error_handler = CubicWebPublisher.error_handler

    @monkeypatch(CubicWebPublisher, 'error_handler')
    def error_handler(self, req, ex, tb=False):
        if not req.ajax_request:
            # else ajax_error_handler will be called, don't send the error
            # twice
            handle_error(req)
        return cw_error_handler(self, req, ex, tb)

    cw_ajax_error_handler = CubicWebPublisher.ajax_error_handler

    @monkeypatch(CubicWebPublisher, 'ajax_error_handler')
    def ajax_error_handler(self, req, ex):
        handle_error(req)
        return cw_ajax_error_handler(self, req, ex)

    if HAS_PYRAMID:
        def pyramid_handle_error(req):
            if hasattr(req, 'form'):
                formdata = req.form
            elif hasattr(req, 'POST'):
                formdata = req.POST
            else:
                formdata = {}
            extra = {'url': req.url,
                     'query_string': req.query_string,
                     'method': req.method,
                     'data': formdata,
                     'headers': dict(get_headers(req.environ)),
                     'env': dict(get_environ(req.environ)),
                     'referer': req.referer,
                     }
            add_versions(req, extra)
            ident = client.get_ident(client.captureException(extra=extra))
            msg = "Exception caught; reference is %s" % ident
            logger.critical(msg)

        pyramid_cw_error_handler = CubicWebPyramidHandler.error_handler

        @monkeypatch(CubicWebPyramidHandler, 'error_handler')
        # XXXX beware - order of inputs is different!
        def pyramid_error_handler(self, ex, req, tb=False):
            pyramid_handle_error(req)
            return pyramid_cw_error_handler(self, ex, req)
