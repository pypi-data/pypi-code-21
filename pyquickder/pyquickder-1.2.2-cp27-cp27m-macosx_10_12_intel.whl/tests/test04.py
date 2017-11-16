#
# asn2quickder output for World-Schema -- automatically generated
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

# Human ::= SEQUENCE { name [0] UTF8String, first-words [1] UTF8String DEFAULT "Hello World", age [2] CHOICE { biblical [0] INTEGER (1..1000), modern [1] INTEGER (1..100) } OPTIONAL }
class Human (_api.ASN1ConstructedType):
    _der_packer = (
        chr(_api.DER_PACK_ENTER | _api.DER_TAG_SEQUENCE) +
        chr(_api.DER_PACK_STORE | _api.DER_TAG_CONTEXT(0)) +
        chr(_api.DER_PACK_OPTIONAL) +
        chr(_api.DER_PACK_STORE | _api.DER_TAG_CONTEXT(1)) +
        chr(_api.DER_PACK_OPTIONAL) +
        chr(_api.DER_PACK_ENTER | _api.DER_TAG_CONTEXT(2)) +
        chr(_api.DER_PACK_CHOICE_BEGIN) +
        chr(_api.DER_PACK_STORE | _api.DER_TAG_CONTEXT(0)) +
        chr(_api.DER_PACK_STORE | _api.DER_TAG_CONTEXT(1)) +
        chr(_api.DER_PACK_CHOICE_END) +
        chr(_api.DER_PACK_LEAVE) +
        chr(_api.DER_PACK_LEAVE) +
        chr(_api.DER_PACK_END) )
    _recipe = ('_NAMED', {
        'age': ('_NAMED', {
            'modern': ('_TYPTR', ['_api.ASN1Integer'], 3),
            'biblical': ('_TYPTR', ['_api.ASN1Integer'], 2) } ),
        'name': ('_TYPTR', ['_api.ASN1UTF8String'], 0),
        'first_words': ('_TYPTR', ['_api.ASN1UTF8String'], 1) } )
    _context = globals ()
    _numcursori = 4

#
# Variables with ASN.1 value assignments
#


# asn2quickder output for World-Schema ends here
