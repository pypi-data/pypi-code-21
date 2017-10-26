# ~*~ coding: utf-8 ~*~

from pyasn1.type import univ, namedtype


class Message(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('peer', univ.OctetString()),
        namedtype.NamedType('checksum', univ.OctetString()),
        namedtype.NamedType('message', univ.OctetString()),
    )
