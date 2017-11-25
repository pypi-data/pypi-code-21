
import unittest, cppa3, logging, lxml, os
from cppa3 import smp

from inspect import getsourcefile
from os.path import abspath, dirname, join

from copy import deepcopy

class SMPTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="smp_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.testdatadir = join(thisdir,'data/smp')
        self.parser = lxml.etree.XMLParser(remove_blank_text=True)
        if 'SMPXSDDIR' in os.environ:
            # If we have the location of the SMP XSD,  use it to validate inputs and
            # outputs
            smpdirdir = os.environ['SMPXSDDIR']
            smp3xsd = os.path.join(smpdirdir,'bdx-smp-201605.xsd')
            logging.info('Parsing SMP schema')
            xmlschemadoc = lxml.etree.parse(smp3xsd)
            self.schema = lxml.etree.XMLSchema(xmlschemadoc)
            logging.info('Parsed SMP schema')
        else:
            self.schema = None

    def do_cpp2smp(self, id, doc_id_schema='cppa-docid-qns'):
        cpp_file = os.path.join(self.testdatadir,'cpp_'+id+'.xml')
        cpp =  (lxml.etree.parse(cpp_file, self.parser)).getroot()
        results = smp.cpp2smp(cpp, 'https://smp.example.com/', doc_id_schema=doc_id_schema)

        smp_file_to_test_against = os.path.join(self.testdatadir,'smp_'+id+'.xml')
        results_el = lxml.etree.Element('SMPGenerationResultSet')
        for result in results:
            result_el = lxml.etree.SubElement(results_el, 'SMPGenerationResult')
            for el in result:
                if self.schema != None:
                    if not self.schema.validate(el):
                        err = str(self.schema.error_log.last_error)
                        err = 'Invalid input: {}'.format(lxml.etree.tostring(el,
                                                                             pretty_print=True))
                        logging.error(err)
                        #raise Exception(err)
                result_el.append(el)
        smp_file= os.path.join(smp_file_to_test_against)
        fd = open(smp_file, 'wb')
        fd.write(lxml.etree.tostring(results_el, pretty_print=True))
        fd.close()

    def test_0001(self):
       self.do_cpp2smp('0001')

