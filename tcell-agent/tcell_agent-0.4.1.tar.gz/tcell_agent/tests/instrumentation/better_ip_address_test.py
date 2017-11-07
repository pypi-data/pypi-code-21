import unittest

from tcell_agent.instrumentation.better_ip_address import better_ip_address


class BetterIpAddressTest(unittest.TestCase):
    def empty_env_better_ip_address_test(self):
        remote_address = better_ip_address({})
        self.assertEqual(remote_address, "1.1.1.1")
