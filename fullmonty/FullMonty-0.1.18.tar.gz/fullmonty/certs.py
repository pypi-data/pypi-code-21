# coding=utf-8

"""
Certificate helpers

"""
from fullmonty.simple_logger import error

__docformat__ = 'restructuredtext en'


def self_signed_certs_allowed():
    try:

        import requests

        requests.packages.urllib3.disable_warnings()

        import ssl

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    except ImportError as ex:
        error(str(ex))
