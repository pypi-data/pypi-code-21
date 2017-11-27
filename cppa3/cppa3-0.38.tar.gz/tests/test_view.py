__author__ = 'pvde'


import unittest, cppa3, logging, lxml, os

from cppa3.view import view_cpp, NSMAP

from inspect import getsourcefile
from os.path import abspath, dirname, join

from copy import deepcopy
from catalog import resolve


class ViewTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="view_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.testdatadir = join(thisdir,'data')
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

    def do_create_view(self, id, viewer_parties=[]):
        logging.info('------------------------------------------')
        logging.info('Running test {}'.format(id))
        #logging.basicConfig(level=logging.DEBUG,
        #                    filename="cppa3_test.log")
        cppa_file = os.path.join(self.testdatadir,'cpp_'+id+'.xml')
        cpp =  (lxml.etree.parse(cppa_file, self.parser)).getroot()
        public_cpp = view_cpp(viewer_parties, cpp)
        if self.schema is not None:
            # Change the serial number as many CAs generate values that are
            # too long
            tmpcpp = deepcopy(public_cpp)

            for serialnum in tmpcpp.xpath(
                    'descendant::ds:X509SerialNumber',
                    namespaces = { 'ds': 'http://www.w3.org/2000/09/xmldsig#'}
            ):
                serialnum.text = '1234'
            if not self.schema.validate(tmpcpp):
                err = str(self.schema.error_log.last_error)
                logging.error('CPP {} is invalid: {}'.format(id, err))
                logging.error(lxml.etree.tostring(tmpcpp, pretty_print=True))
                raise cppa3.unify.UnificationException('CPA {} is invalid: {}'.format(id, err))
            else:
                logging.info('Generated CPP valid for {}'.format(id))
        else:
            logging.info('CPP not validated for {}'.format(id))

        cpp_file_to_test_against = os.path.join(self.testdatadir,'cpp_view_'+id+'.xml')
        if not self.replacemode and os.path.isfile(cpp_file_to_test_against):
            base_cpp = lxml.etree.parse(cpp_file_to_test_against)
            base_cpp_clean = reset_timestamped_values_for_compare(base_cpp)
            base_cpp_clean_string = lxml.etree.tostring(base_cpp_clean,
                                                        pretty_print = True)
            cpp_clean = reset_timestamped_values_for_compare(public_cpp)
            cpp_clean_string = lxml.etree.tostring(cpp_clean,
                                                   pretty_print = True)
            if base_cpp_clean_string != cpp_clean_string:
                logging.error('Regression test failed for CPP {}'.format(id))
                logging.debug('Expected: {}'.format(base_cpp_clean_string))
                logging.debug('Found: {}'.format(cpp_clean_string))
                raise Exception('Regression test failed for CPP {}'.format(id))

        else:
            cpp_file= os.path.join(cpp_file_to_test_against)
            fd = open(cpp_file, 'wb')
            fd.write(lxml.etree.tostring(public_cpp, pretty_print=True))
            fd.close()

        logging.info('------------------------------------------')

    def test_0700_a(self):
        self.do_create_view('a_0700', [('some identifier','sometype')])

    def test_0702_b(self):
        self.do_create_view('b_0702', [('some identifier','sometype')])

    def test_0705_a(self):
        self.assertRaises(cppa3.view.ViewException, self.do_create_view, 'a_0705',
                          [('some identifier','sometype')])

    def test_0705_b(self):
        self.assertRaises(cppa3.view.ViewException, self.do_create_view, 'a_0705',
                          [('B','urn:oasis:names:tc:ebcore:partyid-type:unregistered')])

    def test_0710_a(self):
        self.do_create_view('a_0710',
                            [('urn:oasis:names:tc:ebcore:partyid-type:unregistered:vendor_f',None)])


    def test_0711_a(self):
        self.do_create_view('a_0711',
                            [('urn:oasis:names:tc:ebcore:partyid-type:unregistered:vendor_f',None)])

    def test_0715(self):
        self.do_create_view('a_0715', [('some identifier','sometype')])


    # One ServiceSpecification,  party is not allowed, filtered CPP has no ServiceSpecification
    def test_0716(self):
        self.do_create_view('a_0716',
                            [('cdfsdf','urn:oasis:names:tc:ebcore:partyid-type:unregistered')])

    # One ServiceSpecification,  party is denied, filtered CPP has no ServiceSpecification
    def test_0717(self):
        self.do_create_view('a_0717', [('some identifier','sometype')])

    # view for party not in CPP level denied list, OK
    def test_0718(self):
        self.do_create_view('a_0718', [('asddad','sdndfaiufhfiufiug')])

    # 0718 with an unused channel
    def test_0719(self):
        self.do_create_view('a_0719', [('asddad','sdndfaiufhfiufiug')])


    # ACL:  anonymous party, not allowed, exception
    def test_0720(self):
        self.assertRaises(cppa3.view.ViewException, self.do_create_view, 'a_0720', [])

    # This party can see both service specification
    def test_0721(self):
        self.do_create_view('a_0721', [('some identifier', 'sometype')])

    # This party can only see one service specification
    def test_0722(self):
        self.do_create_view('a_0722', [('yet another identifier', 'yetanothertype')])



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

