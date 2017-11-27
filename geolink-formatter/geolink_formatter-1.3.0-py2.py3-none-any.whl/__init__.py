# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from geolink_formatter.entity import Msg
from geolink_formatter.format import HTML
from geolink_formatter.parser import XML


__version__ = '1.3.0'


class GeoLinkFormatter(object):
    def __init__(self, host_url=None, version='1.1.0', dtd_validation=False):
        """Creates a new GeoLinkFormatter instance.

        Args:
            host_url (str): URL of the OEREBlex host to resolve relative URLs. The complete URL until but
                without the */api* part has to be set, starting with *http://* or *https://*.
            version (str): The version of the geoLink schema to be used. Defaults to `1.1.0`.
            dtd_validation (bool): Enable/disable validation of document type definition (DTD).
                Optional, defaults to False.

        """
        self._host_url = host_url
        self._version = version
        self._dtd_validation = dtd_validation

    def html(self, source):
        """Returns the HTML representation of the geoLink XML form the specified source.

        Args:
            source (str or bytes): The geoLink source. Can be a XML string or an URL to load the XML via
                HTTP/HTTPS request.

        Returns:
            str: An HTML formatted string containing the documents as HTML list.

        Raises:
            TypeError: Raised on invalid source type.
            lxml.etree.XMLSyntaxError: Raised on failed validation.
            requests.HTTPError: Raised on failed HTTP request.

        """
        parser = XML(host_url=self._host_url, version=self._version, dtd_validation=self._dtd_validation)
        if isinstance(source, (str, bytes)):
            http = 'http://' if isinstance(source, str) else b'http://'
            https = 'https://' if isinstance(source, str) else b'https://'
            if source.startswith(http) or source.startswith(https):
                return HTML().format(parser.from_url(source))
            else:
                return HTML().format(parser.from_string(source))
        else:
            raise TypeError(Msg.invalid_argument.format(
                arg='source',
                expected=(str, bytes),
                got=source.__class__
            ))
