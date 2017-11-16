__author__ = 'pvde'

import unittest, cppa3.schema, lxml.etree, logging, traceback

from StringIO import StringIO

#from cppa3.schema import cppa3 as cppa3

class SchemaTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="schema_test.log")

    def tree_and_c14n_from_string(self, input):
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        f0 = StringIO(input)
        inputtree = lxml.etree.parse(f0, parser)
        f1 = StringIO()
        inputtree.write_c14n(f1)
        return inputtree, f1.getvalue().decode('utf-8')

    def run_ensure_ordered(self, testid, inputstring, expected_output):
        try:
            logging.info('Running test {}'.format(testid))
            inputtree, instring = self.tree_and_c14n_from_string(inputstring)
            expectedtree, expectedstring = self.tree_and_c14n_from_string(expected_output)
            logging.info(instring)

            outputtree = lxml.etree.ElementTree(cppa3.schema.ensure_ordered(inputtree.getroot()))
            f1 = StringIO()
            outputtree.write_c14n(f1)
            outstring = f1.getvalue().decode('utf-8')

            logging.info(outstring)

            logging.info(expectedstring)

            assert outstring == expectedstring
        except:
            exception = traceback.format_exc()
            logging.error("Exception processing {}: {}".format(testid, exception))
            raise

    def test_0001(self):
        self.run_ensure_ordered('1',
                                '<cppa:aap xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0"/>',
                                '<cppa:aap xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0"/>')

    def _test_0002(self):
        self.run_ensure_ordered('2',
                                '<cppa:aap xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0"/>',
                                '<cppa:noot xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0"/>')

    def test_0002(self):
        self.assertRaises(Exception, self._test_0002)

    def test_0003(self):
        self.run_ensure_ordered(
            '3',
            """<cppa:ebMS3Channel id="ch2" asResponse="true" xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:Description xml:lang="en">Synchronous response channel for errors and receipts on incoming</cppa:Description>
        <cppa:ChannelProfile>http://sbr.gov.au/agreement/Largevolume/1.0/Push/PKI/Signals</cppa:ChannelProfile>
        <cppa:WSSecurityBinding>
            <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Signature>
                <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
                <cppa:SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
                <cppa:SigningCertificateRef certId="b_signingcert"/>
            </cppa:Signature>
        </cppa:WSSecurityBinding>
        <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    </cppa:ebMS3Channel>
            """,
            """<cppa:ebMS3Channel id="ch2" asResponse="true" xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:Description xml:lang="en">Synchronous response channel for errors and receipts on incoming</cppa:Description>
        <cppa:ChannelProfile>http://sbr.gov.au/agreement/Largevolume/1.0/Push/PKI/Signals</cppa:ChannelProfile>
        <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
        <cppa:WSSecurityBinding>
            <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Signature>
                <cppa:SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
                <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
                <cppa:SigningCertificateRef certId="b_signingcert"/>
            </cppa:Signature>
        </cppa:WSSecurityBinding>
    </cppa:ebMS3Channel>""")


