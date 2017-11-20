# -*- coding: utf-8 -*-
"""Subscribers."""
import json

from DateTime import DateTime
from zope.component import getAdapters
from zope.globalrequest import getRequest

from collective.querynextprev import QUERY, SEARCH_URL
from collective.querynextprev.interfaces import IAdditionalDataProvider
from collective.querynextprev.utils import clean_query


def convert_dates(obj):
    """Convert dates to iso format for json serialization."""
    if isinstance(obj, DateTime):
        return obj.ISO()
    else:
        raise TypeError(repr(obj) + " is not JSON serializable")


def record_query_in_session(obj, event):
    """Record catalog query in session."""
    request = getRequest()
    session = request.SESSION
    session[QUERY] = json.dumps(clean_query(event.query), default=convert_dates)
    session[SEARCH_URL] = request.HTTP_REFERER
    adapters = getAdapters((obj, ), IAdditionalDataProvider)
    for adapter in dict(adapters).values():
        session[adapter.get_key()] = adapter.get_value()
