
import unittest, cppa3, logging, lxml, os
from cppa3 import unify

from cppa3.unify import unify

from cppa3.profile import ChannelProfileHandler

from inspect import getsourcefile
from os.path import abspath, dirname, join

from copy import deepcopy
from catalog import resolve

NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0' }

class UnifyTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="unify_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.testdatadir = join(thisdir,'data')
        self.testconfigdir = join(thisdir,'config')
        if 'CPPA3XSDDIR' in os.environ:
            # If we have the location of the CPPA3 XSD,  use it to validate inputs and
            # outputs
            cppa3dir = os.environ['CPPA3XSDDIR']
            cppa3xsd = os.path.join(cppa3dir,'cppa3.xsd')
            xmlschemadoc = lxml.etree.parse(cppa3xsd)
            xmlschemadoc = resolve(xmlschemadoc, thisdir)
            self.schema = lxml.etree.XMLSchema(xmlschemadoc)
        else:
            # Else no schema validation
            self.schema = None

        self.parser = lxml.etree.XMLParser(remove_blank_text=True)

        # If you set the following to True, always generate CPAs
        # If False, preserve and check with previously created CPA
        self.replacemode = False

        self.configdatadir = join(thisdir,'config')
        config_file = os.path.join(self.configdatadir,'channelprofiles.xml')
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        configuration_data =  lxml.etree.parse(config_file, parser)
        self.channel_profile_handler = ChannelProfileHandler(configuration_data).apply_profile_configs

    def do_unification(self, id, agreementid=None,
                       requested_activation_date=None,
                       requested_expiration_date=None,
                       acpp_url=None,
                       bcpp_url=None,
                       handle_defaults=False,
                       remove_unused_certs=True,
                       agreementidfun=None):
        logging.info('------------------------------------------')
        logging.info('Running test {}'.format(id))
        #logging.basicConfig(level=logging.DEBUG,
        #                    filename="cppa3_test.log")
        cppa_file = os.path.join(self.testdatadir,'cpp_a_'+id+'.xml')
        cppb_file = os.path.join(self.testdatadir,'cpp_b_'+id+'.xml')
        acpp =  (lxml.etree.parse(cppa_file, self.parser)).getroot()
        bcpp =  (lxml.etree.parse(cppb_file, self.parser)).getroot()
        if self.schema is not None:
            # Change the serial number as many CAs generate values that are
            # too long
            for tmpcpp in [deepcopy(acpp),
                           deepcopy(bcpp)]:
                for serialnum in tmpcpp.xpath(
                    'descendant::ds:X509SerialNumber',
                    namespaces = { 'ds': 'http://www.w3.org/2000/09/xmldsig#'}
                ):
                    serialnum.text = '1234'
                if not self.schema.validate(tmpcpp):
                    err = str(self.schema.error_log.last_error)
                    raise cppa3.unify.UnificationException('Invalid input: {}'.format(err))

            if self.schema.validate(acpp) and self.schema.validate(bcpp):
                logging.info('CPP A and B are valid for {}'.format(id))
        else:
            logging.info('Not validating {} against CPPA3 schema'.format(id))


        cpa = unify(acpp, bcpp, agreementid=agreementid,
                    requested_activation_date=requested_activation_date,
                    requested_expiration_date=requested_expiration_date,
                    acpp_url=acpp_url,
                    bcpp_url=bcpp_url,
                    default_handler = self.channel_profile_handler,
                    handle_defaults=handle_defaults,
                    delegation_handler=is_connected_to,
                    remove_unused_certs=remove_unused_certs,
                    agreementidfun=agreementidfun
        )
        if self.schema is not None:
            # Change the serial number as many CAs generate values that are
            # too long
            tmpcpa = deepcopy(cpa)

            for serialnum in tmpcpa.xpath(
                    'descendant::ds:X509SerialNumber',
                    namespaces = { 'ds': 'http://www.w3.org/2000/09/xmldsig#'}
            ):
                serialnum.text = '1234'
            if not self.schema.validate(tmpcpa):
                err = str(self.schema.error_log.last_error)
                logging.error('CPA {} is invalid: {}'.format(id, err))
                logging.error(lxml.etree.tostring(cpa, pretty_print=True))
                raise cppa3.unify.UnificationException('CPA {} is invalid: {}'.format(id, err))
            else:
                logging.info('Generated CPA valid for {}'.format(id))
        else:
            logging.info('CPA not validated for {}'.format(id))

        cpa_file_to_test_against = os.path.join(self.testdatadir,'cppa_ab_'+id+'.xml')
        if not self.replacemode and os.path.isfile(cpa_file_to_test_against):
            base_cpa = lxml.etree.parse(cpa_file_to_test_against)
            base_cpa_clean = reset_timestamped_values_for_compare(base_cpa)
            base_cpa_clean_string = lxml.etree.tostring(base_cpa_clean,
                                                        pretty_print = True)
            cpa_clean = reset_timestamped_values_for_compare(cpa)
            cpa_clean_string = lxml.etree.tostring(cpa_clean,
                                                   pretty_print = True)
            if base_cpa_clean_string != cpa_clean_string:
                logging.error('Regression test failed for CPA {}'.format(id))
                logging.debug('Expected: {}'.format(base_cpa_clean_string))
                logging.debug('Found: {}'.format(cpa_clean_string))
                raise Exception('Regression test failed for CPA {}'.format(id))

        else:
            cpa_file= os.path.join(cpa_file_to_test_against)
            fd = open(cpa_file, 'wb')
            fd.write(lxml.etree.tostring(cpa, pretty_print=True))
            fd.close()

        logging.info('------------------------------------------')

    """
    General tests using NamedChannel
    """

    # One Service with complementary Roles one matching Action, matching send-receive, success
    def test_0001(self):
        self.do_unification('0001')

    # One Service with with complementary Roles one non-matching Action, failure
    def test_0002(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0002')

    # One Service with with complementary Roles one matching Action, non-matching send-receive, failure
    def test_0003(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0003' )

    #Sample NamedProtocol for e-SENS
    def test_0007(self):
        self.do_unification('0007')

    #More complete use of NamedProtocol for e-SENS
    def test_0008(self):
        self.do_unification('0008')

    #Another complete use of NamedProtocol for e-SENS
    def test_0009(self):
        self.do_unification('0009')

    #Sample NamedProtocol for ENTSOG
    def test_0010(self):
        self.do_unification('0010')

    # CPP B does not have any services specification with matching roles
    def test_0011(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0011' )

    # CPP B does not have any Service for matching roles
    def test_0012(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0012' )

    # A has two ServiceSpecification, only one of which is relevant for B
    def test_0013(self):
        self.do_unification('0013')

    # B has two ServiceSpecification, only one of which is relevant for A
    def test_0014(self):
        self.do_unification('0014')

    # A has one ActionBinding more in a ServiceBinding than B, and it is a mandatory one
    def test_0015(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0015' )

    # A has one ActionBinding more in a ServiceBinding than B, but it is an optional one
    def test_0016(self):
        self.do_unification('0016')

    # B has one ActionBinding more in a ServiceBinding than A, and it is a mandatory one
    def test_0017(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0017' )

    # A has one ActionBinding more in a ServiceBinding than B, but it is an optional one
    def test_0018(self):
        self.do_unification('0018')

    # No matching Role pair for A and B
    def test_0019(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0019' )

    # Some extra tests
    # Multiple ServiceSpecifications
    def test_0020(self):
        self.do_unification('0020')

    def test_0021(self):
        self.do_unification('0021')

    def test_0022(self):
        self.do_unification('0022')

    def test_0023(self):
        self.do_unification('0023')

    # Wildcard action
    def test_0024(self):
        self.do_unification('0024')

    # to do Wildcard service

    # MaxSize
    # Specified on both sides, first higher
    def test_0026(self):
        self.do_unification('0026')

    # Specified on first side only
    def test_0027(self):
        self.do_unification('0027')

    # Specified on second side only
    def test_0028(self):
        self.do_unification('0028')

    # Tests to show that unification is not commutative, illustrating depth-first
    # backtracking search
    def test_0030(self):
        self.do_unification('0030')

    def test_0031(self):
        self.do_unification('0031')

    # test with explicitly set agreementid
    def test_0040(self):
        self.do_unification('0040', agreementid='our_agreement')

    # test with activation date set
    def test_0041(self):
        import datetime
        requested_date = datetime.datetime(2050,10,5,0,0,0)
        self.do_unification('0041',  requested_activation_date=requested_date)

    # test with expiration date set
    def test_0042(self):
        import datetime
        requested_date = datetime.datetime(2050,10,5,0,0,0)
        self.do_unification('0042',  requested_expiration_date=requested_date)

    # test with CPP URLs
    def test_0043(self):
        self.do_unification('0043',
                            acpp_url='http://a.example.com/acpp.xml',
                            bcpp_url='http://b.example.com/bccp.xml')


    # Extra test, failing ActivationDate
    def test_0050(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0210' )

    def test_0051(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0211' )

    # Named Channel variant of 1007
    def test_0060(self):
        self.do_unification('0060')

    # Variant of 1020 using NamedChannel
    def test_0061(self):
        self.do_unification('0061')

    # IPv4 and IPv6 compatibility
    # A is IPv4 only,  B is any
    def test_0070(self):
        self.do_unification('0070')

    # B is IPv4 only,  A is any
    def test_0071(self):
        self.do_unification('0071')

    # A is IPv4 only,  B is IPv6 only
    def test_0072(self):
        self.assertRaises( cppa3.unify.UnificationException, self.do_unification, '0072' )


    # HTTP version support.
    # B can support 1.1 and 2.0 A only 1.1
    def test_0080(self):
        self.do_unification('0080')

    # Both can support 1.1 and 2.0
    def test_0081(self):
        self.do_unification('0081')

    # HTTP Content Encoding
    def test_0083(self):
        self.do_unification('0083')

    def test_0084(self):
        self.do_unification('0084')

    # HTTP Chunking
    def test_0085(self):
        self.do_unification('0085')


    # Multiple entries for a Service / Action combination
    # In unification a compatible option is to be found
    def test_0090(self):
        self.do_unification('0090')

    def test_0091(self):
        self.do_unification('0091')



    """
    Payload Profile
    """

    # Single part, matching partname, matching namespace, matching root element,
    # matching location, matching cardinality
    def test_0100(self):
        self.do_unification('0100')

    # Single part, non-matching partname, matching namespace, matching root element,
    # matching location, matching cardinality
    def test_0101(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0101')

    # Single part, matching partname, non-matching namespace, matching root element,
    # matching location, matching cardinality
    def test_0102(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0102')

    # Single part, matching partname, matching namespace, non-matching root element,
    # matching location, matching cardinality
    def test_0103(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0103')

    # Single part, matching partname, matching namespace, matching root element,
    # non-matching location, , matching cardinality
    def test_0104(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0104')

    # Single part, matching partname, matching namespace, matching root element,
    # matching location, non-matching cardinality
    def test_0105(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0105')

    # Two parts, matching partnames
    def test_0106(self):
        self.do_unification('0106')

    # Mismatch in number of parts
    def test_0107(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0107')

    # A supports two versions,  newest preferred.  B only supports oldest
    def test_0120(self):
        self.do_unification('0120')

    # A supports two versions,  newest preferred.  B only supports newest
    def test_0121(self):
        self.do_unification('0121')

    # A supports two versions,  newest preferred.  B also supports both but prefers oldest
    def test_0122(self):
        self.do_unification('0122')


    # Payload signature
    def test_0110(self):
        self.do_unification('0110')

    # Payload signature and encryption
    def test_0111(self):
        self.do_unification('0111')

    # Payload encryption

    """
    0200 ...  reserved for future use ...
    """

    """
    0300 Certificates and Trust Anchors for Signing, Encryption and TLS
    """

    # Certificate and Trust Anchor test for Signing cert - positive - Send.
    def test_0300(self):
        self.do_unification('0300')

    # Certificate and Trust Anchor test for Signing cert - negative -Send .
    def test_0301(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0301')

    # Certificate and Trust Anchor test for Encryption cert - positive -Send.
    def test_0302(self):
        self.do_unification('0302')

    # Certificate and Trust Anchor test for Encryption cert - negative.
    def test_0303(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0303')

    # Certificate and Trust Anchor test for Signing cert - positive - Receive.
    def test_0304(self):
        self.do_unification('0304')

    # Certificate and Trust Anchor test for Signing cert - negative - Receive.
    def test_0305(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0305')

    # Certificate and Trust Anchor test for Encryption cert - positive -Receive.
    def test_0306(self):
        self.do_unification('0306')

    # Certificate and Trust Anchor test for TLS Server cert - positive - Send.
    def test_0307(self):
        self.do_unification('0307')

    # Certificate and Trust Anchor test for TLS Server cert - negative - Send.
    def test_0308(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0308')

    # Certificate and Trust Anchor test for TLS Server cert - negative - Receive.
    def test_0309(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0309')

    # Certificate and Trust Anchor test for TLS Server cert - positive - Receive.
    def test_0310(self):
        self.do_unification('0310')

    # Certificate and Trust Anchor test for TLS Client cert - positive - Send.
    def test_0311(self):
        self.do_unification('0311')

    # Certificate and Trust Anchor test for TLS Client cert - negative - Send.
    def test_0312(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0312')

    # Certificate and Trust Anchor test for TLS Client cert - positive - Receive.
    def test_0313(self):
        self.do_unification('0313')

    # Certificate and Trust Anchor test for TLS Client cert - negative - Receive.
    def test_0314(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0314')


    # Only a Trust Anchor, no Signing cert - Send.
    def test_0315(self):
        self.do_unification('0315')



    # XKMS
    def test_0320(self):
        self.do_unification('0320')


    # Certificate Requirements
    # A Signing Certificate is explicitly required and presented
    def test_0330(self):
        self.do_unification('0330')

    # A Signing Certificate is explicitly not required and still presented
    def test_0331(self):
        self.do_unification('0331')

    # A Signing Certificate is explicitly required but not presented
    def test_0332(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0332')

    # An encryption Certificate is explicitly required and presented
    def test_0335(self):
        self.do_unification('0335')

    # An encryption Certificate is explicitly not required and still presented
    def test_0336(self):
        self.do_unification('0336')

    # An encryption Certificate is explicitly required and not presented
    def test_0337(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0337')

    # An TLS server Certificate is explicitly required and presented
    def test_0340(self):
        self.do_unification('0340')

    # A TLS server Certificate is explicitly required and not presented
    def test_0342(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0342')

    # An TLS client Certificate is explicitly required and presented
    def test_0345(self):
        self.do_unification('0345')

    # A TLS client Certificate is explicitly required and not presented
    def test_0347(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0347')



    """
    0400 TLS tests
    """

    # Cipher specified on one side
    def test_0400(self):
        self.do_unification('0400')

    # Cipher specified on other side
    def test_0401(self):
        self.do_unification('0401')

    # Cipher specified on both sides,  intersection exists
    def test_0402(self):
        self.do_unification('0402')

    # Cipher specified on both sides,  intersection does not exist
    def test_0403(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0403')

    # Version mismatch
    def test_0404(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0404')


    """
    0500
    User Authentication
    """

    # Specified on both sides consistently:  success
    def test_0500(self):
        self.do_unification('0500')

    # Specified on both sides inconsistently:  failure
    def test_0501(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0501')

    # Specified on both sides inconsistently:  failure
    def test_0502(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0502')

    # Specified on both sides inconsistently:  failure
    def test_0503(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0503')


    """
    ebBP attributes test

    @@@ to do
    """

    # One Service with complementary Roles one matching Action, matching send-receive, success
    # Consistent ebBP uuid
    def test_0600(self):
        self.do_unification('0600')

    # One Service with complementary Roles one matching Action, matching send-receive, success
    # Inconsistent ebBP uuid
    def test_0601(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0601')

    # One Service with complementary Roles one matching Action, matching send-receive, success
    # Consistent ebBP uuid and name
    def test_0602(self):
        self.do_unification('0602')

    # One Service with complementary Roles one matching Action, matching send-receive, success
    # Consistent ebBP uuid but inconsitent name
    def test_0603(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0603')


    # Both A and B support version "1.0" and "2.0" of a process.  This matches correctly
    def test_0610(self):
        self.do_unification('0610')


    # A support version "1.0" and "2.0" of a process, B only "1.0".  Only "1.0" in result
    def test_0611(self):
        self.do_unification('0611')



    """
    Access Control feature

    Allowed and denied parties, at various levels (CPP, ServiceBinding, ActionBinding).

    """

    # A sets allowed parties and Party B is one of them
    def test_0700(self):
        self.do_unification('0700')

    # A sets allowed parties and Party B is not one of them
    def test_0701(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0701')

    # B sets allowed parties and Party A is one of them
    def test_0702(self):
        self.do_unification('0702')

    # B sets allowed parties and Party A is not one of them
    def test_0703(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0703')

    # A sets denied parties but B is not one of them
    def test_0704(self):
        self.do_unification('0704')

    # A sets denied parties and B is one of them
    def test_0705(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0705')

    # B sets denied parties but A is not one of them
    def test_0706(self):
        self.do_unification('0706')

    # B sets denied parties and A is one of them
    def test_0707(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0707')

    # PartyIdListRef Variant of 0700
    def test_0708(self):
        self.do_unification('0708')

    # PartyIdListRef Variant of 0705
    def test_0709(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '0709')

    # Variant of 0008 where A blacklists B for one ServiceBinding
    def test_0710(self):
        self.do_unification('0710')

    # Variant of 0008 where B blacklists A for one ServiceBinding
    def test_0711(self):
        self.do_unification('0711')

    # Variant of 0008 where A blacklists B for one ServiceSpecification
    def test_0712(self):
        self.do_unification('0712')

    # Variant of 0001 where A blacklists B for one Action
    def test_0713(self):
        self.do_unification('0713')


    """
    ebMS3 tests
    """

    def test_1000(self):
        # two delivery channels,  the first one is compatible and chosen
        self.do_unification('1000')

    def test_1001(self):
        # two delivery channels,  the first one is non compatible so the second must be chosen
        self.do_unification('1001')

    # Channel Profile;  specified on both sides, compatibly
    def test_1002(self):
        self.do_unification('1002')

    # Channel Profile;  specified on both sides, incompatibly
    def test_1003(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1003')

    # Channel Profile;  specified on first side only
    def test_1004(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1004')

    def test_1006(self):
        # two delivery channels,  the first one is non compatible so the second must be chosen
        self.do_unification('1006')

    def test_1007(self):
        # example involving wider variety of services
        self.do_unification('1007')

    def test_1010(self):
        # E-SENS AS4 PoC
        self.do_unification('1010')

    def test_1011(self):
        # E-SENS AS4 PoC for A and B
        self.do_unification('1011')

    def test_1012(self):
        # Variant of 1011 that uses channel features
        self.do_unification('1012')

    def test_1020(self):
        # Variant of 1011 that uses channel features
        self.do_unification('1020')

    # MEPs
    # 1100 range

    # Simple Push MEP Send
    def test_1100(self):
        self.do_unification('1100')

    # Simple Push MEP Receive
    def test_1101(self):
        self.do_unification('1101')

    # Simple Pull MEP Send
    def test_1102(self):
        self.do_unification('1102')

    # Simple Pull MEP Receive
    def test_1103(self):
        self.do_unification('1103')

    # Inconsistency: A expects push,  B pull
    def test_1104(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1104')

    # Inconsistency: A expects pull,  B push
    def test_1105(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1105')

    # Two Way MEP push-and-push Send
    def test_1120(self):
        self.do_unification('1120')

    # Two Way MEP push-and-push Receive
    def test_1121(self):
        self.do_unification('1121')

    # Two Way MEP in one CPP confused with One Way in another
    def test_1122(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1122')

    # Two Way MEP inconsistent in referred to action
    def test_1123(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1123')

    # Two Way MEP sync Send
    def test_1124(self):
        self.do_unification('1124')

    # Two Way MEP sync Receive
    def test_1125(self):
        self.do_unification('1125')

    # Two Way MEP push-and-pull Send
    def test_1126(self):
        self.do_unification('1126')

    # Two Way MEP pull-and-push Send
    #def test_1127(self):
    #    self.do_unification('1127')

    # Two Way MEP pull-and-pull Send
    def test_1128(self):
        self.do_unification('1128')

    # Example that shows negotiation with various options for MEP Bindings

    # Example that shows negotiation with various options for MEP Bindings

    # Example that shows negotiation with various options for MEP Bindings

    # Pull MEP Send with secure Pull Channel
    def test_1140(self):
        self.do_unification('1140')

    # Pull MEP Receive with secure Pull Channel
    def test_1141(self):
        self.do_unification('1141')

    # Pull MEP Send with a specified MPC
    def test_1142(self):
        self.do_unification('1142')

    # Simple Pull MEP Receive with a specified MPC
    def test_1143(self):
        self.do_unification('1143')

    # Simple Push MEP Send with a specified MPC and Username security
    def test_1144(self):
        self.do_unification('1144')

    # Simple Push MEP Receive with a specified MPC and Username security
    def test_1145(self):
        self.do_unification('1145')

    # Simple AS4 Push MEP Send with a single Payload part and a Compressed Payload
    def test_1146(self):
        self.do_unification('1146')

    # Simple Push MEP Send with a mandatory property
    def test_1147(self):
        self.do_unification('1147')

    # Simple Push MEP Send with a two properties, in order, matching
    def test_1148(self):
        self.do_unification('1148')

    # Simple Push MEP Send with a two properties, out of order, matching
    def test_1149(self):
        self.do_unification('1149')

    # Various MPC errors
    # Both Sender and Receiver set the MPC,  but incompatibly
    def test_1150(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1150')

    # Pull client cannot set the MPC for the server, A sends
    def test_1151(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1151')

    # Pull client cannot set the MPC for the server, A receives
    def test_1152(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1152')


    # Property Sets.

    # Two referenced property sets, compatible
    def test_1160(self):
        self.do_unification('1160')

    # Two referenced property sets, incompatible
    def test_1161(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1161')

    # One referenced property set, one inline properties, compatible
    def test_1162(self):
        self.do_unification('1162')

    # One referenced property set, one inline properties, incompatible
    def test_1163(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1163')

    # 1200 range
    # Reliable Messaging:  AS4 reception awareness

    # Specified on both sides consistently:  success
    def test_1200(self):
        self.do_unification('1200')

    # Specified on one side only:  failure
    #def test_1201(self):
    #    self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1201')

    # PersistDuration
    def test_1202(self):
        self.do_unification('1202')

    # Specified on one sides only:  failure

    # Specified on both sides, inconsistent for duplicate elimination:  failure

    # AS4 and ReceiptHandling, Synchronous, Reception Awareness
    # Specified on both sides consistently:  success
    def test_1205(self):
        self.do_unification('1205')

    # AS4 and ReceiptHandling, Asynchronous, Reception Awareness
    def test_1206(self):
        self.do_unification('1206')

    # AS4 and ReceiptHandling, Synchronous, Non-Repudiation

    # AS4 and ReceiptHandling, Synchronous, Non-Repudiation

    # AS4 ReceptionAwareness channel feature
    # Both sides
    def test_1290(self):
        self.do_unification('1290')

    # One side
    def test_1291(self):
        self.do_unification('1291')

    # Other side
    def test_1292(self):
        self.do_unification('1292')

    # 1300 range
    # Compression and Packaging

    # Both have one CompressionType with compatible values
    def test_1300(self):
        self.do_unification('1300')

    # Both have one CompressionType but the values are not compatible
    def test_1301(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1301')

    # Both have multiple CompressionTypes and one value is compatible
    def test_1305(self):
        self.do_unification('1305')

    # Both have multiple CompressionTypes but the values are not compatible
    def test_1310(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1310')

    # 1400 range
    # Advanced features

    # Alternate Channel
    def test_1400(self):
        self.do_unification('1400')

    # External Payload
    def test_1410(self):
        self.do_unification('1410')

    # 1500, 1501, 1502, 1503 Multi Hop:  actorOrRole attribute present on none or on both,
    # and if on both with same value
    def test_1500(self):
        self.do_unification('1500')

    def test_1501(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1501')

    def test_1502(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1502')

    def test_1503(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1503')

    # 1504 Addressing present, inline
    def test_1504(self):
        self.do_unification('1504')

    # 1505 Addressing present in both but inconsistent Endpoint
    def test_1505(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1505')

    # 1506 Addressing in channel present in both but inconsistent Action
    def test_1506(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1506')

    # 1507 Reference parameter: ebMSInferredReverseRoutingInput
    def test_1507(self):
        self.do_unification('1507')

    def test_1508(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1508')

    def test_1509(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1509')

    # Pull mode, with a routed PullRequest based on MPC, no RoutingInput
    # See [EBMS3PART2], section 2.6.1, ad 2 (Signal Messages), first bullet
    def test_1510(self):
        self.do_unification('1510')

    # Pull mode, with a routed PullRequest based on RoutingInput
    # Reference parameter: ebMSInferredPullRequestRoutingInput
    # See [EBMS3PART2], section 2.6.1, ad 2 (Signal Messages), second bullet
    def test_1511(self):
        self.do_unification('1511')

    # Like 1511, but in addition there is a non-bundled error channel
    def test_1512(self):
        self.do_unification('1512')

    # 1515 combination of sorts,  fails because of mismatch in ActionSuffix
    def test_1515(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1515')

    # wsa:From
    def test_1520(self):
        self.do_unification('1520')

    # Bundling,  present on both sides, no Policy,  no Scope
    def test_1530(self):
        self.do_unification('1530')

    # Present on one side only,  fails
    def test_1531(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1531')

    # Present on one side only,  fails

    # Ordering present on both sides, compatible
    def test_1533(self):
        # Policy on both sides,  compatible
        self.do_unification('1533')

    # Ordering present on one side only, incompatible
    def test_1534(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1534')

    # Bundling feature as referenced element
    def test_1535(self):
        self.do_unification('1535')

    # Scope ?

    # Split / Join / Compress
    def test_1550(self):
        # Base case
        self.do_unification('1550')

    def test_1555(self):
        # Compression on both sides,  compatible
        self.do_unification('1555')

    def test_1556(self):
        # FragmentSize
        self.do_unification('1556')

    def test_1557(self):
        # Properties
        self.do_unification('1557')

    def test_1558(self):
        # Properties, this time reusing a PropertySet
        self.do_unification('1558')

    # 1600 Various AS4 tests

    # ENTSOG AS4 Not using ChannelProfile defaults
    def test_1600(self):
        self.do_unification('1600')

    # Use of ChannelProfile and defined defaults for sending and receiving
    # Also, the defaults specify channels for signals.  Those channels are
    # also added to the CPA.
    def test_1601(self):
        self.do_unification('1601', handle_defaults=True)

    # Variant of 1601 that has default signing and encryption certificates in CPP A
    def test_1602(self):
        self.do_unification('1602', handle_defaults=True)

    # Variant of 1601 that has default signing and encryption certificates in CPP B
    def test_1603(self):
        self.do_unification('1603', handle_defaults=True)

    # Variant of 1601 that has default signing and encryption certificates in CPP A and B
    def test_1604(self):
        self.do_unification('1604', handle_defaults=True)

    # Client Certificate,  referenced from transport
    def test_1610(self):
        self.do_unification('1610', handle_defaults=True)

    # Client Certificate,  set as default
    def test_1611(self):
        self.do_unification('1611', handle_defaults=True)

    # Test 1604,  updated for ENTSOG profile v3,  no default processing
    def test_1620(self):
        self.do_unification('1620', handle_defaults=False, agreementidfun=entsog_agreementref)

    # Test 1604,  updated for ENTSOG profile v3,  but referenced certs, no default processing
    def test_1621(self):
        self.do_unification('1621', handle_defaults=False, agreementidfun=entsog_agreementref)

    # Test 1621,  updated for ENTSOG profile v3,  but referenced certs, default processing
    def test_1622(self):
        self.do_unification('1622', handle_defaults=True, agreementidfun=entsog_agreementref)

    def test_1625(self):
        self.do_unification('1625', handle_defaults=True, agreementidfun=entsog_agreementref)


    # SuperAnnuation
    # As defined in DATA AND PAYMENT STANDARDS
    # MESSAGE ORCHESTRATION AND PROFILES
    # https://www.ato.gov.au/uploadedFiles/Content/SPR/downloads/SPR26583msgorchest.pdf
    # For rollover business process, source:
    # https://www.ato.gov.au/uploadedFiles/Content/SPR/downloads/spr00335171_Rollover_Message_Implementation.pdf

    # Ultra Light, Push
    def test_1700(self):
        self.do_unification('1700')

    # Ultra Light, Push, multihop
    def test_1701(self):
        self.do_unification('1701')

    # Light, Push
    def test_1710(self):
        self.do_unification('1710')

    # Light, Pull
    def test_1711(self):
        self.do_unification('1711')

    # Light, Push, multihop
    def test_1715(self):
        self.do_unification('1715')

    # No test for Light, Pull, multihop
    # because AS4 intermediaries don't pull from endpoints


    # High end, Push
    def test_1730(self):
        self.do_unification('1730')

    # High end, Push/PKI
    def test_1731(self):
        self.do_unification('1731')

    # High end, Pull
    def test_1732(self):
        self.do_unification('1732')

    # High end, Pull/PKI
    def test_1733(self):
        self.do_unification('1733')

    # High end, Push, multihop
    def test_1735(self):
        self.do_unification('1735')

    # High end, Push/PKI, multihop
    def test_1736(self):
        self.do_unification('1736')



    # Large volume profile, Push PKI
    def test_1741(self):
        self.do_unification('1741')

    # Large volume profile, Push PKI, more defaults
    def test_1742(self):
        self.do_unification('1742', handle_defaults=True)

    # Large volume profile, Push PKI, channel features
    def test_1743(self):
        self.do_unification('1743', handle_defaults=True)

    # Large volume profile, Push PKI, channel features, multihop
    def test_1744(self):
        self.do_unification('1744', handle_defaults=True)


    # 1900 SAML Conformance Clause

    # One IDP on both sides, matching
    def test_1900(self):
        self.do_unification('1900')

    # Multiple IDPs on both sides, one matching
    def test_1901(self):
        self.do_unification('1901')

    # Multiple IDPs on both sides, none matching
    def test_1902(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1902')

    # One IDP on both sides, mismatch in SAML version
    def test_1903(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1903')

    # One IDP on both sides, mismatch in KeyType
    def test_1904(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1904')

    # One IDP on both sides, required SAML Attribute not provided by sender
    def test_1905(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '1905')

    # 1900, A and B swapped
    def test_1906(self):
        self.do_unification('1906')


    """
    Web Services Tests
    """
    # 2000 base case

    # Fault

    # 2100
    # WS-Security: Signing, Encryption, Signing and Encryption, User Authentication

    # To do:
    # - timestamps

    # Presence match
    def test_2100(self):
        self.do_unification('2100')

    # Presence mismatch 1
    def test_2101(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2101')

    # Presence mismatch 2
    def test_2102(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2102')

    # WSS Version mismatch
    def test_2103(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2103')

    # Signature, minimal content, match
    def test_2110(self):
        self.do_unification('2110')

    # Presence mismatch 1
    def test_2111(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2111')

    # Presence mismatch 2
    def test_2112(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2112')

    # SignatureAlgorithm value mismatch 1
    def test_2113(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2113')

    # DigestAlgorithm value mismatch 1
    def test_2114(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2114')

    # Multiple SignatureAlgorithms
    # All considered equally acceptable
    def test_2115(self):
        self.do_unification('2115')

    # Multiple SignatureAlgorithms, no intersection
    def test_2116(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2116')

    # SignElements
    def test_2117(self):
        self.do_unification('2117')

    # presence mismatch
    def test_2118(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2118')

    # value mismatch
    def test_2119(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2119')

    # Multiple DigestAlgorithms
    def test_2120(self):
        self.do_unification('2120')

    # Multiple Matching SignatureAlgorithms,  only first one selected
    def test_2121(self):
        self.do_unification('2121')

    # @@@ add some variations

    # SignAttachments
    def test_2125(self):
        self.do_unification('2125')

    # Presence mismatch
    def test_2126(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2126')

    # Value mismatch
    def test_2127(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2127')

    # Encryption
    # Base case, data encryption and certificate reference
    def test_2140(self):
        self.do_unification('2140')

    # Multiple options for data encryption
    def test_2141(self):
        self.do_unification('2141')

    # Multiple options for data encryption
    def test_2142(self):
        self.do_unification('2142')

    # Base case and key transport
    def test_2145(self):
        self.do_unification('2145')

    # Encrypt Elements
    def test_2146(self):
        self.do_unification('2146')

    # Encrypt Attachments
    def test_2147(self):
        self.do_unification('2147')

    # Encrypt External Payloads
    def test_2148(self):
        self.do_unification('2148')

    # Encrypt Attachments, mismatch
    def test_2149(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2149')

    # User Authentication

    # Specified on both sides consistently:  success
    def test_2170(self):
        self.do_unification('2170')

    # Specified on both sides inconsistently:  failure
    #def test_2170(self):
    #    self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2171')

    # Channel features

    # WSSecurityBinding is a channel feature on both sides, or on on of the two sides
    def test_2200(self):
        self.do_unification('2200')

    def test_2201(self):
        self.do_unification('2201')

    def test_2202(self):
        self.do_unification('2200')

    # WS Reliable Messaging
    # Base case, Protocol selection
    def test_2300(self):
        self.do_unification('2300')

    # Ack on Receipt
    def test_2303(self):
        self.do_unification('2303')

    def test_2304(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '2304')


    # Packaging


    """
    EDIINT tests
    """

    # AS2 single payload with signing, no receipt requested
    def test_3000(self):
        self.do_unification('3000')

    # AS2 single payload with signing and a synchronous signed receipt
    def test_3001(self):
        self.do_unification('3001')

    # AS2 single payload with signing and a synchronous unsigned receipt
    def test_3002(self):
        self.do_unification('3002')

    # AS2 single payload with signing and an asynchronous signed receipt
    def test_3003(self):
        self.do_unification('3003')

    # AS2 single payload with signing and an asynchronous signed AS1 receipt
    def test_3004(self):
        self.do_unification('3004')

    # AS2 compressed single payload with signing, no receipt requested
    def test_3050(self):
        self.do_unification('3050')

    # 1621,  adapted for AS2 for EASEE-gas portal developers
    def test_3060(self):
        self.do_unification('3060', handle_defaults=False)

    # 1621,  adapted for AS2 for EASEE-gas portal developers with default handling
    def test_3061(self):
        self.do_unification('3061', handle_defaults=True)

    # Wildcard service, action and role
    def test_3062(self):
        self.do_unification('3062', handle_defaults=False)

    # Wildcard service, action and role
    def test_3063(self):
        self.do_unification('3063', handle_defaults=True)

    # AS1 example
    def test_3100(self):
        self.do_unification('3100')

    # AS3 example,  sender puts to receiver
    def test_3200(self):
        self.do_unification('3200')

    # AS3 example,  receiver gets from receiver
    def test_3201(self):
        self.do_unification('3201')

    # AS2 with multiple uncompressed payloads, RFC 6362
    def test_3075(self):
        self.do_unification('3075')

    # AS2 with multiple compressed payloads
    def test_3076(self):
        self.do_unification('3076')

    # AS3 example with multiple compressed payloads
    def test_3210(self):
        self.do_unification('3210')

    # CTE:  Chunked Transfer Encoding
    def test_3300(self):
        self.do_unification('3300')

    # SHA-2: Various SHA2 algorithms
    def test_3305(self):
        self.do_unification('3305')

    # Filename Preservation
    def test_3310(self):
        self.do_unification('3310')

    # AS2 restart
    def test_3320(self):
        self.do_unification('3320')

    # RestartInterval set by Receiver
    def test_3321(self):
        self.do_unification('3321')

    # CEM.  Could be done by defining a CEM service and
    # related actions, as done for ebCore Agreement Update.

    # AS2 example using a registration service.
    # Used in internal discussion paper
    def test_3400(self):
        self.do_unification('3400')


    """
    ebMS2 tests
    """

    # Simple Push MEP Send, no RM, no Security, synchronous errors
    # synReplyMode:  (msh)SignalsOnly
    def test_4000(self):
        self.do_unification('4000')

    # Simple Push MEP Send, no RM, no Security, asynchronous errors
    # synReplyMode:  none
    def test_4001(self):
        self.do_unification('4001')

    # @@@ add some non-matching cases

    # Simple Push MEP Send, RM, toParty, no Security, synchronous receipts
    # 4010
    def test_4010(self):
        self.do_unification('4010')

    # Simple Push MEP Send, RM, toParty, no Security, asynchronous receipts


    # @@@ mismatch in actor


    # 4020
    # Simple Push MEP Send, RM, nextMSH, no Security, synchronous errors
    def test_4020(self):
        self.do_unification('4020')

    # Simple Push MEP Send, RM, nextMSH, no Security, asynchronous errors

    # 4030
    # Simple Push MEP Send, no RM, signing, signed synchronous errors
    def test_4030(self):
        self.do_unification('4030')

    # Simple Push MEP Send, no RM, signing, signed asynchronous errors
    def test_4031(self):
        self.do_unification('4031')


    # SMTP transport,  signing,  signed asynchronous receipts and errors,
    # Two versions of a service,  distinguished by payload profile.
    # B also supports AS4.

    def test_4100(self):
        self.do_unification('4100')

    # Here A also supports AS4
    def test_4101(self):
        self.do_unification('4101', remove_unused_certs=True)



    # Synchronous Business Response

    # Two Way MEP,  asynchronous
    """
    "responseOnly"
    "signalsAndResponse"
    """

    # Two Way MEP,  synchronous

    """
    Extensibility

    """

    """
    Delegation Channels

    """

    # Party Delegates,  CounterParty uses AS2
    def test_5000(self):
        self.do_unification('5000')

    # Party has AS2 channel, CounterParty delegates
    def test_5001(self):
        self.do_unification('5001')

    # Party and CounterParty delegate to same third party
    def test_5002(self):
        self.do_unification('5002')

    # Party and CounterParty delegate to different parties, compatible
    def test_5003(self):
        self.do_unification('5003')

    # Party and CounterParty delegate to different parties, incompatible
    def test_5004(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '5004')

    # Party Delegates,  CounterParty uses AS2, incompatible
    def test_5005(self):
        self.assertRaises(cppa3.unify.UnificationException, self.do_unification, '5005')

    # Like 5002,  but also a receiving channel
    def test_5006(self):
        self.do_unification('5006')

    # Like 5006,  elaborated with payload profile, alternatives
    def test_5007(self):
        self.do_unification('5007')

    # Version of test 3400 using a delegation channel
    def test_5100(self):
        self.do_unification('5100')


    """
    Future transports and messaging protocols
    """

    # Simple AMQP message with AQMP transport
    def test_6000(self):
        self.do_unification('6000')

    # Simple AMQP message with AQMP transport and a TLS tunnel
    def test_6001(self):
        self.do_unification('6001')

    # Simple AMQP message with AQMP transport, anonymous SASL mechanism
    def test_6002(self):
        self.do_unification('6002')

    # Simple AMQP message with AQMP transport, intersection of SASL mechanisms
    def test_6003(self):
        self.do_unification('6003')

    # Simple AMQP message with AQMP transport and SASL and an in-protocol TLS upgrade
    def test_6004(self):
        self.do_unification('6004')

    """
    Future transport bindings
    """

    # Hypothetical ebMS3 binding that uses SFTP
    def test_6200(self):
        self.do_unification('6200')



    """
    Tests for lower level functions

    unify_simple_subelement
    """

    def test_9000(self):
        logging.info('Running test 9000')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=False,
                                        required=False)
        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))

    def _test_9001(self):
        logging.info('Running test 9001')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=False,
                                        required=True)

    def test_9001(self):
        self.assertRaises(cppa3.unify.UnificationException, self._test_9001)

    def test_9002(self):
        logging.info('Running test 9002')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=False,
                                        required=True)
        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))

    def test_9003(self):
        logging.info('Running test 9003')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=False,
                                        required=True)
        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))

    def test_9004(self):
        logging.info('Running test 9004')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        <ns2:b>value2</ns2:b>
        <ns2:b>value3</ns2:b>
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value2</ns2:b>
        <ns2:b>value3</ns2:b>
        <ns2:b>value4</ns2:b>
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=False)
        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))

    def test_9005(self):
        logging.info('Running test 9005')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        <ns2:b>value2</ns2:b>
        <ns2:b>value3</ns2:b>
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value2</ns2:b>
        <ns2:b>value3</ns2:b>
        <ns2:b>value4</ns2:b>
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=False,
                                        strictelements=False)
        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))

    def _test_9006(self):
        logging.info('Running test 9006')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        <ns2:b>value2</ns2:b>
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value3</ns2:b>
        <ns2:b>value4</ns2:b>
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=False,
                                        required=False)

    def test_9006(self):
        self.assertRaises(cppa3.unify.UnificationException, self._test_9006)

    def test_9007(self):
        logging.info('Running test 9007')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        <ns2:b>value2</ns2:b>
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        <ns2:b>value2</ns2:b>
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=True,
                                        required=False)

        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))

    def test_9008(self):
        logging.info('Running test 9008')
        unifier = cppa3.unify.CPABuilder(nsmap={'ns':'urn:namespace',
                                                'ns2':'urn:namespace2'})

        a_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value1</ns2:b>
        <ns2:b>value2</ns2:b>
        </ns:a>
        """)
        b_element = lxml.etree.fromstring("""<ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2">
        <ns2:b>value2</ns2:b>
        <ns2:b>value1</ns2:b>
        </ns:a>
        """)
        ab_element = lxml.etree.fromstring("""
        <ns:a xmlns:ns="urn:namespace" xmlns:ns2="urn:namespace2"/>
        """)
        unifier.unify_simple_subelement(a_element,
                                        b_element,
                                        ab_element,
                                        'ns2',
                                        'b',
                                        intersectifmultiple=True,
                                        strictelements=True,
                                        required=False)

        logging.debug(lxml.etree.tostring(ab_element, pretty_print=True))


def reset_timestamped_values_for_compare(cpa):
    cpa_to_edit = deepcopy(cpa)
    for path in [
        'child::cppa:AgreementInfo/cppa:Description',
        'child::cppa:AgreementInfo/cppa:ActivationDate',
        'child::cppa:AgreementInfo/cppa:ExpirationDate',
        'descendant::cppa:Password']:
        element_to_edit_l = cpa_to_edit.xpath(path,
                                              namespaces = NSMAP)
        if len(element_to_edit_l) > 0:
            for el in element_to_edit_l:
                value = el.text
                logging.info('Resetting {} from {}'.format(path, value))
                el.text = 'NONE'
    return cpa_to_edit

def is_connected_to(
        frompartyid,
        frompartytype,
        fromcppid,
        service,
        action,
        direction,
        topartyid,
        topartyidtype,
        topartycppid):

    logging.info('Called with {} {} {} {} {} {}'.format(frompartyid, frompartytype, fromcppid,
                                                        topartyid, topartyidtype, topartycppid))

    if frompartyid == topartyid \
        and frompartytype == topartyidtype:
        return True
    if frompartyid == 'C' \
        and frompartytype == 'urn:oasis:names:tc:ebcore:partyid-type:unregistered' \
        and topartyid == 'B' \
        and topartyidtype == 'urn:oasis:names:tc:ebcore:partyid-type:unregistered':
        return True
    elif frompartyid == 'A' \
        and frompartytype == 'urn:oasis:names:tc:ebcore:partyid-type:unregistered' \
        and topartyid == 'D' \
        and topartyidtype == 'urn:oasis:names:tc:ebcore:partyid-type:unregistered':
        return True
    elif frompartyid == 'C' \
        and frompartytype == 'urn:oasis:names:tc:ebcore:partyid-type:unregistered' \
        and topartyid == 'D' \
        and topartyidtype == 'urn:oasis:names:tc:ebcore:partyid-type:unregistered':
        return True
    else:
        return False

def entsog_agreementref(acpp, bcpp, version=1):
    a_party_id = acpp.xpath('child::cppa:PartyInfo/cppa:PartyId[1]/text()',
                            namespaces=NSMAP)[0]
    b_party_id = bcpp.xpath('child::cppa:PartyInfo/cppa:PartyId[1]/text()',
                            namespaces=NSMAP)[0]
    [first, second] = sorted([a_party_id, b_party_id])
    return "http://entsog.eu/communication/agreements/{}/{}/{}".format(first, second, version)
