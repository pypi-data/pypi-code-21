import unittest

from .generic import ContainerGeneric


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class BackendTest(ContainerGeneric):
    params = [
        ("hostname", u"SomeHostName"),
        ("name", u"MyName"),
        ("rmi_port", 1035),
        ("tcp_port", 1235),
        ("lang_ports", {1: 35, 2: 37})
    ]

    mutable_params = [
        ("hostname", u"AnotherHostName"),
        ("name", u"AnotherName"),
        ("rmi_port", 1135),
        ("tcp_port", 1535),
    ]

    class_under_test = Backend


if __name__ == '__main__':
    unittest.main()
