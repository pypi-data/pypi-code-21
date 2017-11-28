# coding: utf-8
# import mock
# from unittest import TestCase
# import swutils.network
#
# class NetWorkTestCase(TestCase):
#
#     @mock.patch('netifaces.interfaces')
#     @mock.patch('netifaces.ifaddresses')
#     def test_get_ip4(self, ifaddresses_mock, interfaces_mock):
#         address = '10.0.1.4'
#         interfaces_mock.return_value = ['eth0']
#         ifaddresses_mock.return_value = {2: [{'broadcast': '10.0.1.255', 'netmask': '255.255.255.0', 'addr': address}]}
#
#         ip4 = swutils.network.get_ip4()
#         self.assertEquals(ip4, [address])