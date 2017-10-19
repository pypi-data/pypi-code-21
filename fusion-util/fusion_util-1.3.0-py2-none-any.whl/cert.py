"""
Utility functions for dealing with TLS certificates (and keys).
"""
import re

from incremental import Version
from twisted.python.deprecate import deprecated
from twisted.internet.ssl import Certificate



@deprecated(Version('fusion_util', 1, 2, 0), 'pem.twisted')
def chainCerts(data):
    """
    Matches and returns any certificates found except the first match.

    Regex code copied from L{twisted.internet.endpoints._parseSSL}.
    Related ticket: https://twistedmatrix.com/trac/ticket/7732

    @type path: L{bytes}
    @param data: PEM-encoded data containing the certificates.

    @rtype: L{list} containing L{Certificate}s.
    """
    matches = re.findall(
        r'(-----BEGIN CERTIFICATE-----\n.+?\n-----END CERTIFICATE-----)',
        data,
        flags=re.DOTALL)
    chainCertificates = [
        Certificate.loadPEM(chainCertPEM).original
        for chainCertPEM in matches]
    return chainCertificates[1:]
