import os, traceback, logging, lxml.etree

from cppa3.cppa23 import cpp23, cpa23
from catalog import resolve

import unittest

from inspect import getsourcefile
from os.path import abspath, dirname, join


class CPPA23TestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="cppa23_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.testdatadir = join(thisdir,'data23')
        self.parser = lxml.etree.XMLParser(remove_blank_text=True)
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

    def upconvert_cpp(self, id):
        logging.info('------------------------------------------')
        logging.info('Running test {}'.format(id))
        cppa2_file = os.path.join(self.testdatadir,'cpp2_'+id+'.xml')
        cppa3_file = os.path.join(self.testdatadir,'cpp3_'+id+'.xml')
        inputdoc =  (lxml.etree.parse(cppa2_file, self.parser)).getroot()
        outputdoc = cpp23(inputdoc)
        fd = open(cppa3_file, 'wb')
        fd.write(lxml.etree.tostring(outputdoc, pretty_print=True))
        fd.close()
        self.validate(id, outputdoc)


    def upconvert_cpa(self, id):
        logging.info('------------------------------------------')
        logging.info('Running test {}'.format(id))

        cppa2_file = os.path.join(self.testdatadir,'cpa2_'+id+'.xml')
        cppa3_file = os.path.join(self.testdatadir,'cpa3_'+id+'.xml')
        inputdoc =  (lxml.etree.parse(cppa2_file, self.parser)).getroot()
        outputdoc = cpa23(inputdoc)
        fd = open(cppa3_file, 'wb')
        fd.write(lxml.etree.tostring(outputdoc, pretty_print=True))
        fd.close()
        self.validate(id, outputdoc)

    def validate(self, id, document):
        if self.schema is not None:
            # Change the serial number as many CAs generate values that are
            # too long
            for tmpcpp in [document]:
                for serialnum in tmpcpp.xpath(
                    'descendant::ds:X509SerialNumber',
                    namespaces = { 'ds': 'http://www.w3.org/2000/09/xmldsig#'}
                ):
                    serialnum.text = '1234'
                if not self.schema.validate(tmpcpp):
                    err = str(self.schema.error_log.last_error)
                    raise Exception('Invalid input for {}: {}'.format(id, err))

            if self.schema.validate(document):
                logging.info('Generated a valid document for {}'.format(id))


    def test_0001(self):
        self.upconvert_cpa('0001')

    def test_0002(self):
        self.upconvert_cpp('0002')

    def test_0100(self):
        self.upconvert_cpa('0100')

    def test_0101(self):
        self.upconvert_cpp('0101')


