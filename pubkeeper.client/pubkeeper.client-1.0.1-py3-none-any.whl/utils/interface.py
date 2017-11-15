"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""


class InvalidInterface(Exception):
    pass


def is_interface(interface_name):
    from netifaces import interfaces
    return interface_name in interfaces()


def get_first_address(interface_name):
    from netifaces import ifaddresses, AF_INET
    try:
        # it’s possible for an interface to have more than one address,
        # even within the same family
        addresses = [i['addr'] for i in ifaddresses(interface_name).setdefault(
            AF_INET, [{'addr': None}])]
        return addresses[0]
    except:
        raise InvalidInterface("Interface: '{0}' does not have a valid "
                               "address assigned".format(interface_name))


def get_interfaces():
    from netifaces import interfaces
    return interfaces()
