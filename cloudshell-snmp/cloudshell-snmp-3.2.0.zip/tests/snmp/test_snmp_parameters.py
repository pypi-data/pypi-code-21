from unittest import TestCase
from mock import MagicMock
from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2ReadParameters, SNMPV2WriteParameters


class TestSNMPParametersInit(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "S3c@sw0rd"
    SNMP_PRIVATE_KEY = "S3c@tw0rd"

    def test_snmp_v2_write_parameters(self):
        snmp_v2_write_parameters = SNMPV2WriteParameters(ip=self.IP,
                                                         snmp_write_community=self.SNMP_WRITE_COMMUNITY)

        self.assertTrue(snmp_v2_write_parameters.ip == self.IP)
        self.assertTrue(snmp_v2_write_parameters.snmp_community == self.SNMP_WRITE_COMMUNITY)

    def test_snmp_v2_read_parameters(self):
        snmp_v2_read_parameters = SNMPV2ReadParameters(ip=self.IP, snmp_read_community=self.SNMP_READ_COMMUNITY)

        self.assertTrue(snmp_v2_read_parameters.ip == self.IP)
        self.assertTrue(snmp_v2_read_parameters.snmp_community == self.SNMP_READ_COMMUNITY)

    def test_snmp_v3_parameters(self):
        snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER,
                                              snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY)

        self.assertTrue(snmp_v3_parameters.ip == self.IP)
        self.assertTrue(snmp_v3_parameters.snmp_user == self.SNMP_USER)
        self.assertTrue(snmp_v3_parameters.snmp_password == self.SNMP_PASSWORD)
        self.assertTrue(snmp_v3_parameters.snmp_private_key == self.SNMP_PRIVATE_KEY)

    def test_snmp_2950_v2_read_parameters(self):
        snmp_v2_read_parameters = SNMPV2ReadParameters(ip="192.168.42.235", snmp_read_community="Cisco")
        logger = get_qs_logger()
        snmp = QualiSnmp(snmp_parameters=snmp_v2_read_parameters, logger=logger)
        print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")

    def test_snmp_v3_parameters_74(self):
        test_scenario = []
        for key in ["AES-128", "AES-192", "AES-256", "DES", "3DES-EDE"]:
            for auth in ["SHA", "MD5"]:
                test_scenario.append(SNMPV3Parameters(ip="172.16.1.74",
                                                      snmp_user="test_{}_{}".format(auth.lower(),
                                                                                    key.lower().replace("ede",
                                                                                                        "").replace(
                                                                                        "-", "")),
                                                      snmp_password=self.SNMP_PASSWORD,
                                                      snmp_private_key=self.SNMP_PRIVATE_KEY,
                                                      auth_protocol=auth, private_key_protocol=key))
        for scenario in test_scenario:
            print scenario.snmp_user
            logger = MagicMock()
            snmp = QualiSnmp(snmp_parameters=scenario, logger=logger)
            print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")

    def test_snmp_v3_parameters_249(self):
        test_scenario = []
        for key in ["AES-128", "AES-192", "AES-256", "DES", "3DES-EDE"]:
            for auth in ["SHA", "MD5"]:
                test_scenario.append(SNMPV3Parameters(ip="172.16.1.249",
                                                      snmp_user="test_{}_{}".format(auth.lower(),
                                                                                    key.lower().replace("ede",
                                                                                                        "").replace(
                                                                                        "-", "")),
                                                      snmp_password=self.SNMP_PASSWORD,
                                                      snmp_private_key=self.SNMP_PRIVATE_KEY,
                                                      auth_protocol=auth, private_key_protocol=key))
        for scenario in test_scenario:
            print scenario.snmp_user
            logger = MagicMock()
            snmp = QualiSnmp(snmp_parameters=scenario, logger=logger)
            print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")

    def test_snmp_v3_parameters_auth_sha_no_priv(self):
        snmp_v3_parameters = SNMPV3Parameters(ip="172.16.1.72", snmp_user="test_sha_no_priv",
                                              snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY,
                                              auth_protocol="SHA", private_key_protocol="DES")

        logger = get_qs_logger()
        snmp = QualiSnmp(snmp_parameters=snmp_v3_parameters, logger=logger)
        snmp._test_snmp_agent()
        print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")

    def test_snmp_v3_parameters_auth_sha_priv_aes(self):
        snmp_v3_parameters = SNMPV3Parameters(ip="172.16.1.72", snmp_user="test_sha_aes_priv",
                                              snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY,
                                              auth_protocol="SHA", private_key_protocol="AES-128")

        logger = get_qs_logger()
        snmp = QualiSnmp(snmp_parameters=snmp_v3_parameters, logger=logger)
        snmp._test_snmp_agent()
        print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")

    def test_snmp_v3_parameters_auth_sha_priv_des(self):
        snmp_v3_parameters = SNMPV3Parameters(ip="172.16.1.72", snmp_user="test_sha_no_priv",
                                              snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY,
                                              auth_protocol="SHA", private_key_protocol="DES")

        logger = get_qs_logger()
        snmp = QualiSnmp(snmp_parameters=snmp_v3_parameters, logger=logger)
        snmp._test_snmp_agent()
        print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")

    def test_snmp_v3_parameters_auth_md5_priv_des(self):
        snmp_v3_parameters = SNMPV3Parameters(ip="172.16.1.72", snmp_user="test_md5_no_priv",
                                              snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY,
                                              auth_protocol="MD5", private_key_protocol="DES")

        logger = get_qs_logger()
        snmp = QualiSnmp(snmp_parameters=snmp_v3_parameters, logger=logger)
        snmp._test_snmp_agent()
        print snmp.get_property("SNMPv2-MIB", "sysDescr", "0")