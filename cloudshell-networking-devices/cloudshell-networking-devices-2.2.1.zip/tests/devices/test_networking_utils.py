import unittest

import mock

from cloudshell.devices import networking_utils


class TestNetworkingUtils(unittest.TestCase):
    def test_normalize_path(self):
        path = "#test path"
        # act
        result = networking_utils.normalize_path(path=path)
        # verify
        self.assertEqual(result, "%23test%20path")

    def test_normalize_str(self):
        tmp_str = "test, string N/A, Future "
        # act
        result = networking_utils.normalize_str(tmp_str=tmp_str)
        # verify
        self.assertEqual(result, "test.string.")

    def test_is_integer_returns_true(self):
        # act
        result = networking_utils.is_integer("42")
        # verify
        self.assertTrue(result)

    def test_is_integer_returns_false(self):
        # act
        result = networking_utils.is_integer("test str")
        # verify
        self.assertFalse(result)

    def test_validate_ip_returns_true(self):
        # act
        result = networking_utils.validate_ip(string="192.168.10.10")
        # verify
        self.assertTrue(result)

    def test_validate_ip_wrong_octets_number(self):
        # act
        result = networking_utils.validate_ip(string="192.168.10.10.10")
        # verify
        self.assertFalse(result)

    def test_validate_ip_non_digit_octet(self):
        # act
        result = networking_utils.validate_ip(string="192.somestring.10.10")
        # verify
        self.assertFalse(result)

    def test_validate_ip_non_valid_octet(self):
        # act
        result = networking_utils.validate_ip(string="192.168.10.256")
        # verify
        self.assertFalse(result)

    def test_validate_vlan_number_returns_true(self):
        # act
        for val in (100, "1", "4000"):
            result = networking_utils.validate_vlan_number(number=val)
            # verify
            self.assertTrue(result)

    def test_validate_vlan_number_returns_false(self):
        # act
        for val in ("0", "4001", "some str", .025):
            result = networking_utils.validate_vlan_number(number=val)
            # verify
            self.assertFalse(result)

    def test_validate_vlan_range_returns_true(self):
        networking_utils.validate_vlan_number = mock.MagicMock(return_value=True)
        # act
        result = networking_utils.validate_vlan_range(vlan_range="38,40-45")
        # verify
        self.assertTrue(result)

    def test_validate_vlan_range_returns_false(self):
        networking_utils.validate_vlan_number = mock.MagicMock(return_value=False)
        # act
        result = networking_utils.validate_vlan_range(vlan_range="38,40-45")
        # verify
        self.assertFalse(result)

    def test_validate_spanning_tree_type_returns_true(self):
        # act
        for val in ('bridge', 'domain', 'lc-issu', 'loopguard', 'mode', 'mst',
                    'pathcost', 'port', 'pseudo-information', 'vlan'):
            result = networking_utils.validate_spanning_tree_type(data=val)
            # verify
            self.assertTrue(result)

    def test_validate_spanning_tree_type_returns_false(self):
        # act
        result = networking_utils.validate_spanning_tree_type(data="some test data")
        # verify
        self.assertFalse(result)

    def test_verify_ip_in_range_returns_true(self):
        # act
        result = networking_utils.verify_ip_in_range(ip_address="192.168.20.10",
                                                     start_addr="192.168.10.1",
                                                     end_addr="192.168.30.255")
        # verify
        self.assertTrue(result)

    def test_verify_ip_in_range_returns_false(self):
        # act
        result = networking_utils.verify_ip_in_range(ip_address="192.168.8.10",
                                                     start_addr="192.168.10.1",
                                                     end_addr="192.168.30.255")
        # verify
        self.assertFalse(result)

    def test_validate_mac_returns_true(self):
        # act
        result = networking_utils.validate_mac(str_mac="40:8d:5c:24:c7:04")
        # verify
        self.assertTrue(result)

    def test_validate_mac_returns_false(self):
        # act
        result = networking_utils.validate_mac(str_mac="40:8d:5c:24:c7:04:5d")
        # verify
        self.assertFalse(result)

    def test_normalize_buffer(self):
        input_buffer = "\033[1;31;40m Colored text"
        # act
        result = networking_utils.normalize_buffer(input_buffer=input_buffer)
        # verify
        self.assertEqual(result, "[1;31;40m Colored text")

    def test_get_dictionary_data(self):
        src_dict = {
            "key1": "val1",
            1: "val2",
            "key3": "val3",
            22: "val4",
            "1": "val5",
        }
        forbidden_keys = ["key3", 1]
        expected_dict = src_dict.copy()
        for key in forbidden_keys:
            del expected_dict[key]
        # act
        result = networking_utils.get_dictionary_data(source_dictionary=src_dict,
                                                      forbidden_keys=forbidden_keys)
        # verify
        self.assertEqual(result, expected_dict)

    @mock.patch("cloudshell.devices.networking_utils.math")
    def test_get_bit_size_with_kbit(self, math):
        bandwidth = "100 KBIT/SEC"
        expected_res = mock.MagicMock()
        math.log10.return_value = expected_res
        # act
        result = networking_utils.get_bit_size(bandwidth)
        # verify
        self.assertEqual(result, expected_res)
        math.log10.assert_called_once_with(100 * 2 ** 10)

    @mock.patch("cloudshell.devices.networking_utils.math")
    def test_get_bit_size_with_mbit(self, math):
        bandwidth = "100 MBIT/SEC"
        expected_res = mock.MagicMock()
        math.log10.return_value = expected_res
        # act
        result = networking_utils.get_bit_size(bandwidth)
        # verify
        self.assertEqual(result, expected_res)
        math.log10.assert_called_once_with(100 * 2 ** 20)

    @mock.patch("cloudshell.devices.networking_utils.math")
    def test_get_bit_size_with_gbit(self, math):
        bandwidth = "100 GBIT/SEC"
        expected_res = mock.MagicMock()
        math.log10.return_value = expected_res
        # act
        result = networking_utils.get_bit_size(bandwidth)
        # verify
        self.assertEqual(result, expected_res)
        math.log10.assert_called_once_with(100 * 2 ** 30)

    def test_serialize_to_json(self):
        data = {"key1": "val1"}
        # act
        result = networking_utils.serialize_to_json(result=data)
        # verify
        self.assertEqual(result, '{"key1": "val1"}')


class TestUrlParser(unittest.TestCase):
    def setUp(self):
        self.url_data = {
            "scheme": "https",
            "fragment": "",
            "hostname": "test.host.com",
            "netloc": "cisco:securePassword!1@test.host.com:22",
            "port": 22,
            "query": "",
            "username": "cisco",
            "password": "securePassword!1",
            "path": "/some_path",
            "filename": "test_file_name.ext",
        }
        self.url = "https://cisco:securePassword!1@test.host.com:22/some_path/test_file_name.ext"

    def test_parse_url(self):
        # act
        result = networking_utils.UrlParser.parse_url(url=self.url)
        # verify
        self.assertEqual(result, self.url_data)

    def test_build_url(self):
        # act
        result = networking_utils.UrlParser.build_url(url=self.url_data)
        # verify
        self.assertEqual(result, self.url)
