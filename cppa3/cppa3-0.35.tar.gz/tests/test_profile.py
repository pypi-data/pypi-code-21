
import unittest, lxml, logging, os

from inspect import getsourcefile
from os.path import abspath, dirname, join

from cppa3.profile import ChannelProfileHandler
from lxml import etree

class ProfileTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="profile_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.configdatadir = join(thisdir,'config')
        config_file = os.path.join(self.configdatadir,
                                   'channelprofiles.xml')
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        configuration_data =  lxml.etree.parse(config_file, parser)
        self.handler = ChannelProfileHandler(configuration_data)
        self.parser = parser

    def _test_regression(self, id, created, expected):
        created_as_text = lxml.etree.tostring(created,
                                              pretty_print=True)
        expected_as_text = lxml.etree.tostring(expected,
                                              pretty_print=True)
        if created_as_text != expected_as_text:
            logging.info('Created {}:\n{}\nExpected:{}\n'.format(id,
                                                                 created_as_text,
                                                                 expected_as_text))
            raise Exception('{}: created:\n{}\nExpected:\n{}'.format(id,
                                                                     created_as_text,
                                                                     expected_as_text))
        else:
            logging.info('Regression test for {} passed'.format(id))

    def test_0001(self):
        logging.info('Test 0001')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/cprofiles/200809/as4ebhandler</cppa:ChannelProfile>
            <cppa:WSSecurityBinding>
                <cppa:Signature>
                   <cppa:SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
                </cppa:Signature>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/cprofiles/200809/as4ebhandler</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
      </cppa:Signature>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0001', result, expected)


    def test_0002(self):
        logging.info('Test 0002')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding pycppa3:ifused="true">
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#aes128-cbc</cppa:EncryptionAlgorithm>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0002', result, expected)

    def test_0003(self):
        logging.info('Test 0003')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding pycppa3:ifused="true">
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Encryption>
                     <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
                </cppa:Encryption>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0003', result, expected)

    def test_0004(self):
        logging.info('Test 0004')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding>
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Encryption>
                    <cppa:EncryptAttachments>true</cppa:EncryptAttachments>
                </cppa:Encryption>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#aes128-cbc</cppa:EncryptionAlgorithm>
        <cppa:EncryptAttachments>true</cppa:EncryptAttachments>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0004', result, expected)


    def test_0005(self):
        logging.info('Test 0005')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding pycppa3:ifused="true">
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Encryption>
                      <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
                      <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes256-gcm</cppa:EncryptionAlgorithm>
                </cppa:Encryption>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes256-gcm</cppa:EncryptionAlgorithm>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0005', result, expected)


    #@unittest.skip('Fix later')
    def test_0006(self):
        logging.info('Test 0006')
        data = etree.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
        <cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
<cppa:ebMS3Channel package="entsog_package">
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:WSSecurityBinding>
        <cppa:Signature>
            <cppa:SigningCertificateRef certId="_OYHRBO"/>
        </cppa:Signature>
        <cppa:Encryption>
            <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
        </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
        <cppa:RetryHandling>
            <cppa:Retries>10</cppa:Retries>
        </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
</cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel package="entsog_package" includeAgreementRef="false">
    <cppa:Description xml:lang="en">Channel for any ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>https://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        <cppa:SigningCertificateRef certId="_OYHRBO"/>
      </cppa:Signature>
      <cppa:Encryption>
        <cppa:KeyEncryption>
          <cppa:EncryptionAlgorithm> http://www.w3.org/2009/xmlenc11#rsa-oaep</cppa:EncryptionAlgorithm>
          <cppa:MaskGenerationFunction>http://www.w3.org/2009/xmlenc11#mgf1sha256</cppa:MaskGenerationFunction>
          <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        </cppa:KeyEncryption>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
      <cppa:DuplicateHandling>
        <cppa:DuplicateElimination>true</cppa:DuplicateElimination>
        <cppa:PersistDuration>P10D</cppa:PersistDuration>
      </cppa:DuplicateHandling>
      <cppa:RetryHandling>
        <cppa:Retries>10</cppa:Retries>
        <cppa:RetryInterval>PT30S</cppa:RetryInterval>
      </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
    <cppa:ErrorHandling>
      <cppa:DeliveryFailuresNotifyProducer>true</cppa:DeliveryFailuresNotifyProducer>
    </cppa:ErrorHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/gzip</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:ebMS3Channel>
</cppa:CPP>
""", self.parser)
        self._test_regression('0006', result, expected)



    def test_0007(self):
        logging.info('Test 0007')
        data = etree.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
        <cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel id="ch_receive" transport="tr_receive" package="entsog_package">
    <cppa:Description xml:lang="en">Channel for incoming ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:WSSecurityBinding>
      <cppa:Encryption>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:ErrorHandling>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
    </cppa:ReceiptHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/gzip</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel id="ch_receive" transport="tr_receive" package="entsog_package" includeAgreementRef="false">
    <cppa:Description xml:lang="en">Channel for incoming ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>https://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
      </cppa:Signature>
      <cppa:Encryption>
        <cppa:KeyEncryption>
          <cppa:EncryptionAlgorithm> http://www.w3.org/2009/xmlenc11#rsa-oaep</cppa:EncryptionAlgorithm>
          <cppa:MaskGenerationFunction>http://www.w3.org/2009/xmlenc11#mgf1sha256</cppa:MaskGenerationFunction>
          <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        </cppa:KeyEncryption>
        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
      <cppa:DuplicateHandling>
        <cppa:DuplicateElimination>true</cppa:DuplicateElimination>
        <cppa:PersistDuration>P10D</cppa:PersistDuration>
      </cppa:DuplicateHandling>
      <cppa:RetryHandling>
        <cppa:Retries>5</cppa:Retries>
        <cppa:RetryInterval>PT30S</cppa:RetryInterval>
      </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
    <cppa:ErrorHandling>
      <cppa:DeliveryFailuresNotifyProducer>true</cppa:DeliveryFailuresNotifyProducer>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
    </cppa:ReceiptHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/gzip</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:ebMS3Channel>
</cppa:CPP>
""", self.parser)
        self._test_regression('0007', result, expected)


    def test_0008(self):
        logging.info('Test 0008')
        data = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://docs.oasis-open.org/ebxmlcppa/cppa-3.0 file:../../../cppa3-xsd/cppa3.xsd">
  <cppa:ProfileInfo>
    <cppa:ProfileIdentifier>EASEE-gas AS2 Profile for TSO 2</cppa:ProfileIdentifier>
  </cppa:ProfileInfo>
  <cppa:PartyInfo>
    <cppa:PartyName xml:lang="en">TSO 2</cppa:PartyName>
    <cppa:PartyId type="http://www.entsoe.eu/eic-codes/eic-party-codes-x">21X-EU-B-A0A0A-B</cppa:PartyId>
    <cppa:PartyContact>
      <cppa:ContactType>Technical Contact</cppa:ContactType>
      <cppa:DirectTelephone>+3761234560</cppa:DirectTelephone>
      <cppa:Email>edi@tso2.eu</cppa:Email>
    </cppa:PartyContact>
    <cppa:Certificate id="_SCNXER">
      <ds:KeyInfo>
        <ds:KeyName>Signing certificate for TSO 2</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:Certificate id="_4UP74O">
      <ds:KeyInfo>
        <ds:KeyName>Encryption certificate for TSO 2</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBhbmRlciBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:CertificateDefaults>
      <cppa:SigningCertificateRef certId="_SCNXER"/>
      <cppa:EncryptionCertificateRef certId="_4UP74O"/>
    </cppa:CertificateDefaults>
  </cppa:PartyInfo>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZSZ"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_1_2">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_1_4">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A10</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_2_6">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_2_8">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZHC"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_3_10">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUA"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_4_12">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUF"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A11</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_5_14">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_6_16">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_6_18">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUG"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_7_20">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_7_22">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUE"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_8_24">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUJ"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">N/A</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="N/A" id="ab_9_26">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_10_28">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_10_30">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUH"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A11</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_11_32">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZSO"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_12_34">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_12_36">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_13_38">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_13_40">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_14_42">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_14_44">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A06</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_15_46">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_15_48">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_16_50">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_16_52">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_17_54">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_17_56">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZSH"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_18_58">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_18_60">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_19_62">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A06</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_20_64">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_20_66">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_21_68">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_22_70">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="Meter Read"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_23_72">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="Mark Tr"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_24_74">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="FACILITY OPERATOR"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A10</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_25_76">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="StorageLNGOperator"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_26_78">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTY"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_27_80">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_27_82">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTZ"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_28_84">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_28_86">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTU"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_29_88">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_29_90">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_30_92">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_30_94">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTT"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_31_96">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_31_98">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_32_100">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_32_102">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTV"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A05</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_33_104">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="Consumer"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_34_106">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="SU"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_35_108">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZAA"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_36_110">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator"/>
    <cppa:CounterPartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder"/>
    <cppa:ServiceBinding>
      <cppa:Service>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/service</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/test" id="ab_37_112">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder"/>
    <cppa:CounterPartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator"/>
    <cppa:ServiceBinding>
      <cppa:Service>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/service</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/test" id="ab_38_114">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>

  <cppa:AS2Channel id="b_ch_send" transport="tr_send">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SigningCertificateRef certId="_SCNXER"/>
    </cppa:Signature>
    <cppa:Encryption/>
    <cppa:ErrorHandling>
      <cppa:ReceiverErrorsReportChannelId>b_ch_send_signals</cppa:ReceiverErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>b_ch_send_signals</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
  </cppa:AS2Channel>

  <cppa:AS2Channel id="b_ch_send_signals"  asResponse="true">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile/MDN</cppa:ChannelProfile>
    <cppa:Signature/>
  </cppa:AS2Channel>



  <cppa:AS2Channel id="b_ch_receive" transport="tr_receive" >
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature />
    <cppa:Encryption>
      <cppa:EncryptionCertificateRef certId="_4UP74O"/>
    </cppa:Encryption>
  </cppa:AS2Channel>

  <cppa:HTTPTransport id="tr_send">
    <cppa:ClientIPv4>1.2.3.4</cppa:ClientIPv4>
  </cppa:HTTPTransport>

  <cppa:HTTPTransport id="tr_receive">
    <cppa:Endpoint>https://tso1.eu/as2</cppa:Endpoint>
  </cppa:HTTPTransport>

  <cppa:PayloadProfile id="edigas">
    <cppa:PayloadPart maxOccurs="1" minOccurs="1">
      <cppa:PartName>businessdocument</cppa:PartName>
      <cppa:MIMEContentType>application/xml</cppa:MIMEContentType>
      <cppa:Property maxOccurs="1" minOccurs="1" name="EDIGASDocumentType"/>
    </cppa:PayloadPart>
  </cppa:PayloadProfile>

    <cppa:SOAPWithAttachmentsEnvelope id="entsog_package">
        <cppa:SimpleMIMEPart PartName="businessdocument" />
    </cppa:SOAPWithAttachmentsEnvelope>

</cppa:CPP>""", self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ProfileInfo>
    <cppa:ProfileIdentifier>EASEE-gas AS2 Profile for TSO 2</cppa:ProfileIdentifier>
  </cppa:ProfileInfo>
  <cppa:PartyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <cppa:PartyName xml:lang="en">TSO 2</cppa:PartyName>
    <cppa:PartyId type="http://www.entsoe.eu/eic-codes/eic-party-codes-x">21X-EU-B-A0A0A-B</cppa:PartyId>
    <cppa:PartyContact>
      <cppa:ContactType>Technical Contact</cppa:ContactType>
      <cppa:DirectTelephone>+3761234560</cppa:DirectTelephone>
      <cppa:Email>edi@tso2.eu</cppa:Email>
    </cppa:PartyContact>
    <cppa:Certificate id="_SCNXER">
      <ds:KeyInfo>
        <ds:KeyName>Signing certificate for TSO 2</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:Certificate id="_4UP74O">
      <ds:KeyInfo>
        <ds:KeyName>Encryption certificate for TSO 2</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBhbmRlciBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:CertificateDefaults>
      <cppa:SigningCertificateRef certId="_SCNXER"/>
      <cppa:EncryptionCertificateRef certId="_4UP74O"/>
    </cppa:CertificateDefaults>
  </cppa:PartyInfo>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZSZ"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_1_2">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_1_4">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A10</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_2_6">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_2_8">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZHC"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_3_10">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUA"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_4_12">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUF"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A11</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_5_14">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_6_16">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_6_18">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUG"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_7_20">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_7_22">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUE"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_8_24">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUJ"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">N/A</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="N/A" id="ab_9_26">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_10_28">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_10_30">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZUH"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A11</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_11_32">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZSO"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_12_34">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_12_36">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_13_38">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_13_40">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_14_42">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_14_44">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A06</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_15_46">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_15_48">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_16_50">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_16_52">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_17_54">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_17_56">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZSH"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_18_58">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_18_60">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_19_62">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A06</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_20_64">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_20_66">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_21_68">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_22_70">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="Meter Read"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_23_72">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="Mark Tr"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_24_74">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="FACILITY OPERATOR"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A10</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_25_76">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="StorageLNGOperator"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A09</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_26_78">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTY"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_27_80">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_27_82">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTZ"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A08</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_28_84">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_28_86">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTU"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_29_88">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_29_90">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_30_92">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_30_94">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTT"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_31_96">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_31_98">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A04</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_32_100">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_32_102">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZTV"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A05</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_33_104">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="Consumer"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_34_106">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="SU"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A02</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_35_108">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="ZSO"/>
    <cppa:CounterPartyRole name="ZAA"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">A07</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/as4/200902/action" id="ab_36_110">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator"/>
    <cppa:CounterPartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder"/>
    <cppa:ServiceBinding>
      <cppa:Service>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/service</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/test" id="ab_37_112">
        <cppa:ChannelId>b_ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder"/>
    <cppa:CounterPartyRole name="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator"/>
    <cppa:ServiceBinding>
      <cppa:Service>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/service</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/test" id="ab_38_114">
        <cppa:ChannelId>b_ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:AS2Channel id="easeegas_as2_signal" asResponse="true">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile/MDN</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
    </cppa:Signature>
  </cppa:AS2Channel>
  <cppa:AS2Channel id="b_ch_send" transport="tr_send">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
      <cppa:SigningCertificateRef certId="_SCNXER"/>
    </cppa:Signature>
    <cppa:Encryption>
      <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#tripledes-cbc</cppa:EncryptionAlgorithm>
    </cppa:Encryption>
    <cppa:ErrorHandling>
      <cppa:ReceiverErrorsReportChannelId>b_ch_send_signals</cppa:ReceiverErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>b_ch_send_signals</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/pkcs7-mime</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:AS2Channel>
  <cppa:AS2Channel id="b_ch_send_signals" asResponse="true">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile/MDN</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
    </cppa:Signature>
  </cppa:AS2Channel>
  <cppa:AS2Channel id="b_ch_receive" transport="tr_receive">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
    </cppa:Signature>
    <cppa:Encryption>
      <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#tripledes-cbc</cppa:EncryptionAlgorithm>
      <cppa:EncryptionCertificateRef certId="_4UP74O"/>
    </cppa:Encryption>
    <cppa:ErrorHandling>
      <cppa:ReceiverErrorsReportChannelId>easeegas_as2_signal</cppa:ReceiverErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>easeegas_as2_signal</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/pkcs7-mime</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:AS2Channel>
  <cppa:HTTPTransport id="tr_send">
    <cppa:ClientIPv4>1.2.3.4</cppa:ClientIPv4>
    <cppa:TransportLayerSecurity>
      <cppa:TLSProtocol version="1.2">TLS</cppa:TLSProtocol>
    </cppa:TransportLayerSecurity>
  </cppa:HTTPTransport>
  <cppa:HTTPTransport id="tr_receive">
    <cppa:Endpoint>https://tso1.eu/as2</cppa:Endpoint>
    <cppa:TransportLayerSecurity>
      <cppa:TLSProtocol version="1.2">TLS</cppa:TLSProtocol>
    </cppa:TransportLayerSecurity>
  </cppa:HTTPTransport>
  <cppa:PayloadProfile id="edigas">
    <cppa:PayloadPart maxOccurs="1" minOccurs="1">
      <cppa:PartName>businessdocument</cppa:PartName>
      <cppa:MIMEContentType>application/xml</cppa:MIMEContentType>
      <cppa:Property maxOccurs="1" minOccurs="1" name="EDIGASDocumentType"/>
    </cppa:PayloadPart>
  </cppa:PayloadProfile>
  <cppa:SOAPWithAttachmentsEnvelope id="entsog_package">
    <cppa:SimpleMIMEPart PartName="businessdocument"/>
  </cppa:SOAPWithAttachmentsEnvelope>
</cppa:CPP>
""", self.parser)
        self._test_regression('0008', result, expected)



    def test_0008(self):
        logging.info('Test 0008')
        data = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://docs.oasis-open.org/ebxmlcppa/cppa-3.0 file:../../../cppa3-xsd/cppa3.xsd">
  <cppa:ProfileInfo>
    <cppa:ProfileIdentifier>EASEE-gas AS2 Profile for TSO 1</cppa:ProfileIdentifier>
  </cppa:ProfileInfo>
  <cppa:PartyInfo>
    <cppa:PartyName xml:lang="en">TSO 1</cppa:PartyName>
    <cppa:PartyId type="http://www.entsoe.eu/eic-codes/eic-party-codes-x">21X-EU-A-A0A0A-A</cppa:PartyId>
    <cppa:PartyContact>
      <cppa:ContactType>Technical Contact</cppa:ContactType>
      <cppa:DirectTelephone>+3791234560</cppa:DirectTelephone>
      <cppa:Email>edi@tso1.eu</cppa:Email>
    </cppa:PartyContact>
    <cppa:PartyContact></cppa:PartyContact>
    <cppa:Certificate id="_OYHRBO">
      <ds:KeyInfo>
        <ds:KeyName>Signing certificate for TSO 1</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:Certificate id="_YE5XZF">
      <ds:KeyInfo>
        <ds:KeyName>Encryption certificate for TSO 1</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBhbmRlciBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:CertificateDefaults>
      <cppa:SigningCertificateRef certId="_YE5XZF"/>
      <cppa:EncryptionCertificateRef certId="_OYHRBO"/>
    </cppa:CertificateDefaults>
  </cppa:PartyInfo>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="*"/>
    <cppa:CounterPartyRole name="*"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">*</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="*" id="ab_1_2">
        <cppa:ChannelId>ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="*" id="ab_1_4">
        <cppa:ChannelId>ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>

  <cppa:AS2Channel id="ch_send" transport="tr_send" package="easee-gas_package">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SigningCertificateRef certId="_OYHRBO"/>
    </cppa:Signature>
    <cppa:Encryption/>
  </cppa:AS2Channel>

  <cppa:AS2Channel id="ch_receive" transport="tr_receive" package="easee-gas_package" >
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature/>
    <cppa:Encryption>
      <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
    </cppa:Encryption>
  </cppa:AS2Channel>

  <cppa:HTTPTransport id="tr_send">
    <cppa:ClientIPv4>1.2.3.4</cppa:ClientIPv4>
  </cppa:HTTPTransport>

  <cppa:HTTPTransport id="tr_receive">
    <cppa:Endpoint>https://tso1.eu/as2</cppa:Endpoint>
  </cppa:HTTPTransport>

  <cppa:PayloadProfile id="edigas">
    <cppa:PayloadPart maxOccurs="1" minOccurs="1">
      <cppa:PartName>businessdocument</cppa:PartName>
      <cppa:MIMEContentType>application/xml</cppa:MIMEContentType>
    </cppa:PayloadPart>
  </cppa:PayloadProfile>

  <cppa:MIMEEnvelope id="easee-gas_package">
    <cppa:SimpleMIMEPart PartName="businessdocument"/>
  </cppa:MIMEEnvelope>
</cppa:CPP>
""", self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ProfileInfo>
    <cppa:ProfileIdentifier>EASEE-gas AS2 Profile for TSO 1</cppa:ProfileIdentifier>
  </cppa:ProfileInfo>
  <cppa:PartyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <cppa:PartyName xml:lang="en">TSO 1</cppa:PartyName>
    <cppa:PartyId type="http://www.entsoe.eu/eic-codes/eic-party-codes-x">21X-EU-A-A0A0A-A</cppa:PartyId>
    <cppa:PartyContact>
      <cppa:ContactType>Technical Contact</cppa:ContactType>
      <cppa:DirectTelephone>+3791234560</cppa:DirectTelephone>
      <cppa:Email>edi@tso1.eu</cppa:Email>
    </cppa:PartyContact>
    <cppa:PartyContact/>
    <cppa:Certificate id="_OYHRBO">
      <ds:KeyInfo>
        <ds:KeyName>Signing certificate for TSO 1</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:Certificate id="_YE5XZF">
      <ds:KeyInfo>
        <ds:KeyName>Encryption certificate for TSO 1</ds:KeyName>
        <ds:X509Data>
          <ds:X509Certificate>RGl0IGlzIGVlbiBhbmRlciBjZXJ0aWZpY2FhdCBpbiBiYXNlIDY0IGNvZGVyaW5n</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </cppa:Certificate>
    <cppa:CertificateDefaults>
      <cppa:SigningCertificateRef certId="_YE5XZF"/>
      <cppa:EncryptionCertificateRef certId="_OYHRBO"/>
    </cppa:CertificateDefaults>
  </cppa:PartyInfo>
  <cppa:ServiceSpecification>
    <cppa:PartyRole name="*"/>
    <cppa:CounterPartyRole name="*"/>
    <cppa:ServiceBinding>
      <cppa:Service type="http://edigas.org/service">*</cppa:Service>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="send" action="*" id="ab_1_2">
        <cppa:ChannelId>ch_send</cppa:ChannelId>
      </cppa:ActionBinding>
      <cppa:ActionBinding payloadProfileId="edigas" sendOrReceive="receive" action="*" id="ab_1_4">
        <cppa:ChannelId>ch_receive</cppa:ChannelId>
      </cppa:ActionBinding>
    </cppa:ServiceBinding>
  </cppa:ServiceSpecification>
  <cppa:AS2Channel id="easeegas_as2_signal_inbound" asResponse="true">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
    </cppa:Signature>
  </cppa:AS2Channel>
  <cppa:AS2Channel id="ch_send" transport="tr_send" package="easee-gas_package">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
      <cppa:SigningCertificateRef certId="_OYHRBO"/>
    </cppa:Signature>
    <cppa:Encryption>
      <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#tripledes-cbc</cppa:EncryptionAlgorithm>
    </cppa:Encryption>
    <cppa:ErrorHandling>
      <cppa:ReceiverErrorsReportChannelId>easeegas_as2_signal_inbound</cppa:ReceiverErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>easeegas_as2_signal_inbound</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/pkcs7-mime</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:AS2Channel>
  <cppa:AS2Channel id="easeegas_as2_signal_outbound" asResponse="true">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
    </cppa:Signature>
  </cppa:AS2Channel>
  <cppa:AS2Channel id="ch_receive" transport="tr_receive" package="easee-gas_package">
    <cppa:ChannelProfile>http://easee-gas.eu/AS2-Profile</cppa:ChannelProfile>
    <cppa:Signature>
      <cppa:SignatureAlgorithm>http://www.w3.org/2000/09/xmldsig#rsa-sha1</cppa:SignatureAlgorithm>
    </cppa:Signature>
    <cppa:Encryption>
      <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#tripledes-cbc</cppa:EncryptionAlgorithm>
      <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
    </cppa:Encryption>
    <cppa:ErrorHandling>
      <cppa:ReceiverErrorsReportChannelId>easeegas_as2_signal_outbound</cppa:ReceiverErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>easeegas_as2_signal_outbound</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
    <cppa:Compression>
      <cppa:CompressionAlgorithm>application/pkcs7-mime</cppa:CompressionAlgorithm>
    </cppa:Compression>
  </cppa:AS2Channel>
  <cppa:HTTPTransport id="tr_send">
    <cppa:ClientIPv4>1.2.3.4</cppa:ClientIPv4>
    <cppa:TransportLayerSecurity>
      <cppa:TLSProtocol version="1.2">TLS</cppa:TLSProtocol>
    </cppa:TransportLayerSecurity>
  </cppa:HTTPTransport>
  <cppa:HTTPTransport id="tr_receive">
    <cppa:Endpoint>https://tso1.eu/as2</cppa:Endpoint>
    <cppa:TransportLayerSecurity>
      <cppa:TLSProtocol version="1.2">TLS</cppa:TLSProtocol>
    </cppa:TransportLayerSecurity>
  </cppa:HTTPTransport>
  <cppa:PayloadProfile id="edigas">
    <cppa:PayloadPart maxOccurs="1" minOccurs="1">
      <cppa:PartName>businessdocument</cppa:PartName>
      <cppa:MIMEContentType>application/xml</cppa:MIMEContentType>
    </cppa:PayloadPart>
  </cppa:PayloadProfile>
  <cppa:MIMEEnvelope id="easee-gas_package">
    <cppa:SimpleMIMEPart PartName="businessdocument"/>
  </cppa:MIMEEnvelope>
</cppa:CPP>
""", self.parser)
        self._test_regression('0008', result, expected)


