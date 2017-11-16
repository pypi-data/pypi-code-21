#
# asn2quickder output for Test01 -- automatically generated
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

# Thing ::= SEQUENCE { ding [0] INTEGER }
class Thing (_api.ASN1ConstructedType):
    _der_packer = (
        chr(_api.DER_PACK_ENTER | _api.DER_TAG_SEQUENCE) +
        chr(_api.DER_PACK_STORE | _api.DER_TAG_CONTEXT(0)) +
        chr(_api.DER_PACK_LEAVE) +
        chr(_api.DER_PACK_END) )
    _recipe = ('_NAMED', {
        'ding': ('_TYPTR', ['_api.ASN1Integer'], 0) } )
    _context = globals ()
    _numcursori = 1

#
# Variables with ASN.1 value assignments
#


# asn2quickder output for Test01 ends here
