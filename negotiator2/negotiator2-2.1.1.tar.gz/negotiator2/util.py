"""Unility functions for negotiator2."""

from .negotiator import AcceptParameters, ContentType, ContentNegotiator
from .memento import TimeMap, memento_parse_datetime
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARN)


def conneg_on_accept(supported_types, accept_header):
    """Do content negotiation on content type only.

    Arguments:

    supported_types - List of one or more server supported types given
        in order of server preference. The first is the default type.

    accept_header - Client provided HTTP Accept header (may be empty
        or None).

    Return:

    mimetype - Best match to client preference or default type.
    """
    default_type = supported_types[0]
    try:
        if (accept_header is None or accept_header == ''):
            return(default_type)
        default_params = AcceptParameters(ContentType(default_type))
        acceptable = []
        for t in supported_types:
            acceptable.append(AcceptParameters(ContentType(t)))
        cn = ContentNegotiator(default_params, acceptable)
        acceptable = cn.negotiate(accept=accept_header)
        if (acceptable is not None):
            return(acceptable.content_type.mimetype())
    except Exception as e:
        logging.debug("conneg_on_accept: Ignored: " + str(e))
    return(default_type)


def negotiate_on_datetime(timemap, accept_datetime_header, method=None):
    """Do Memento Datetime negotiation based on the Accept-Datetime header.

    Arguments:

    timemap - A TimeMap object with information about Original Resource and
        all Mementos available
    accept_datetime_header - Value of Accept-Datetime header
    method - Method to be used by TimeMap.best_version() to find the best
        version for the specified datetime.

    Return:

    memento_uri - The URI of the best Memento. If there are any problems
        with the accept_datetime_header then the default return value will
        be the last version in the TimeMap (usually the Memento Orginal
        Resource).
    """
    try:
        dt = memento_parse_datetime(accept_datetime_header)
    except Exception as e:
        logging.debug("negotiate_on_datetime: Ignored bad Accept-Datetime: " + str(e))
        dt = None  # will not be used
        method = TimeMap.LAST
    return timemap.best_version(dt, method)
