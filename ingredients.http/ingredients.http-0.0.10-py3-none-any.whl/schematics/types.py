import ipaddress

import arrow
import arrow.parser
from schematics.exceptions import ConversionError
from schematics.types import BaseType


class ArrowType(BaseType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_native(self, value, context=None):
        if not isinstance(value, arrow.Arrow):
            try:
                value = arrow.get(value)
            except arrow.parser.ParserError:
                raise ConversionError('Could not parse %s. Should be ISO 8601.' % value)
        return value

    def to_primitive(self, value, context=None):
        return value.isoformat()


class EnumType(BaseType):
    def __init__(self, enum_class, **kwargs):
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def to_native(self, value, context=None):
        if not isinstance(value, self.enum_class):
            try:
                value = self.enum_class(value)
            except ValueError as e:
                raise ConversionError(e.__str__())

        # Always use the primitive type so we can easily json encode/decode
        return self.to_primitive(value, context=context)

    def to_primitive(self, value, context=None):
        return value.value


class IPv4AddressType(BaseType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_native(self, value, context=None):
        if not isinstance(value, ipaddress.IPv4Address):
            try:
                value = ipaddress.IPv4Address(value)
            except ValueError as e:
                raise ConversionError(e.__str__())

        if value.is_multicast:
            raise ConversionError("Cannot use a multicast (RFC 3171) IPv4 Address")

        if value.is_unspecified:
            raise ConversionError("Cannot use an unspecified (RFC 5735) IPv4 Address")

        if value.is_reserved:
            raise ConversionError("Cannot use a reserved (IETF reserved) IPv4 Address")

        if value.is_loopback:
            raise ConversionError("Cannot use a loopback (RFC 3330) IPv4 Address")

        if value.is_link_local:
            raise ConversionError("Cannot use a link local (RFC 3927) IPv4 Address")

        return value

    def to_primitive(self, value, context=None):
        return str(value)


class IPv4NetworkType(BaseType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_native(self, value, context=None):
        if not isinstance(value, ipaddress.IPv4Network):
            try:
                value = ipaddress.IPv4Network(value)
            except ValueError as e:
                raise ConversionError(e.__str__())

        if value.is_multicast:
            raise ConversionError("Cannot use a multicast (RFC 3171) IPv4 Address")

        if value.is_unspecified:
            raise ConversionError("Cannot use an unspecified (RFC 5735) IPv4 Address")

        if value.is_reserved:
            raise ConversionError("Cannot use a reserved (IETF reserved) IPv4 Address")

        if value.is_loopback:
            raise ConversionError("Cannot use a loopback (RFC 3330) IPv4 Address")

        if value.is_link_local:
            raise ConversionError("Cannot use a link local (RFC 3927) IPv4 Address")

        return value

    def to_primitive(self, value, context=None):
        return str(value)
