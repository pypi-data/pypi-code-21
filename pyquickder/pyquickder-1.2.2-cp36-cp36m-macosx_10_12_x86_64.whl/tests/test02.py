#
# asn2quickder output for RFC3280 -- automatically generated
#
# Read more about Quick `n' Easy DER on https://github.com/vanrein/quick-der
#


#
# Import general definitions and package dependencies
#

import quick_der.api as _api

#
# Classes for ASN.1 type assignments
#

# CertificateSerialNumber ::= INTEGER
class CertificateSerialNumber (_api.ASN1Integer):
    _der_packer = (
        chr(_api.DER_PACK_STORE | _api.DER_TAG_INTEGER) +
        chr(_api.DER_PACK_END) )
    _recipe = ('_TYPTR', ['_api.ASN1Integer'], 0)
    _context = globals ()
    _numcursori = 1

#
# Variables with ASN.1 value assignments
#


# asn2quickder output for RFC3280 ends here
