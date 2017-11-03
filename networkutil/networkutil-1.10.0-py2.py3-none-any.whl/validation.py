# -*- coding: utf-8 -*-
# Description: validation functions

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


def valid_ipv4(ip):
    if len(ip) != len([c for c in ip if c in u'0123456789.']):
        return False
    parts = [part for part in ip.split(u'.')]
    try:
        return len(parts) == 4 and len(parts) == len([part
                                                      for part in parts
                                                      if len(str(int(part))) == len(part) and 0 <= int(part) <= 255])
    except ValueError:
        pass
    return False

if __name__ == u"__main__":
    import logging
    for valid_ip in [u'0.0.0.0',
                     u'0.0.0.1',
                     u'0.0.1.0',
                     u'0.1.0.0',
                     u'1.0.0.0',
                     u'1.1.1.1',
                     u'0.0.0.255',
                     u'0.0.255.0',
                     u'0.255.0.0',
                     u'255.0.0.0',
                     u'255.255.255.255',
                     ]:
        try:
            assert valid_ipv4(valid_ip), (u'"{ip}" should be valid but is not'
                                          .format(ip = valid_ip))
        except Exception as e:
            logging.exception(e)

    for invalid_ip in [u'0.0.0.',
                       u'.0.0.1',
                       u'0..1.0',
                       u'0.1..0',
                       u'1.0.0.x',
                       u'0.0.0.256',
                       u'0.0.300.0',
                       u'0.400.0.0',
                       u'FF.0.0.0',
                       u'',
                       ]:
        try:
            assert not valid_ipv4(invalid_ip),\
                (u'"{ip}" is valid but should not be'
                 .format(ip = invalid_ip))
        except Exception as e:
            logging.exception(e)


def valid_ipv6(ip):
    """
    3ffe:1900:4545:3:200:f8ff:fe21:67cf

    Colons separate 16-bit fields. Leading zeros can be omitted in each field
    as can be seen above where the field :0003: is written :3:. In addition,
    a double colon (::) can be used once in an address to replace multiple
    fields of zeros. For example:

    fe80:0:0:0:200:f8ff:fe21:67cf can be written fe80::200:f8ff:fe21:67cf
    """
    if len(ip) != len([c for c in ip if c in u'0123456789abcdefABCDEF:']):
        return False
    multiple_zeroes = len(ip.split(u'::')) - 1
    if multiple_zeroes > 1:
        return False  # Only one '::' allowed
    parts = [part for part in ip.split(u':')]

    if multiple_zeroes:
        if len(parts) > 8:
            return False

    elif len(parts) != 8:
        return False

    if len([part for part in parts if len(part) < 5]) == len(parts):
        return True

    return False


if __name__ == u'__main__':
    for valid_ip in [u'::',
                     u'::1',
                     u'1::',
                     u'1:2:3:4::',
                     u'1:2:3:4:5:6:7:8',
                     u'a:b:c:d:e:f:1:2',
                     u'abcd:ef12:34fe:dcba:1234:5678:ABCD:EF90',
                     ]:
        try:
            assert valid_ipv6(valid_ip), (u'"{ipv6}" should be valid but is not'
                                          .format(ipv6 = valid_ip))
        except Exception as e:
            logging.exception(e)

    for invalid_ip in [u'abcd:ef12:34fe:dcba:1234:5678:ABCD:ABCDE',
                       u'abcd:ef12:34fe:dcba:1234:5678:ABCD:EFGH',
                       u'abcd:ef12:34fe:dcba:1234:5678:ABCD.EF12',
                       u'abcd:ef12:34fe:dcba:1234:5678:ABCD',
                       ]:
        try:
            assert not valid_ipv6(invalid_ip),\
                (u'"{ipv6}" is valid but should not be'
                 .format(ipv6 = invalid_ip))
        except Exception as e:
            logging.exception(e)
