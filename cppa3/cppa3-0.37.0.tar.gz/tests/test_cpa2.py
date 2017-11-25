
import unittest, cppa3, logging, lxml, os

from cppa3.cpa2 import downtranslate

from lxml import etree

from inspect import getsourcefile
from os.path import abspath, dirname, join

from copy import deepcopy

class CPPA2TestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="cpa2_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.testdatadir = join(thisdir,'data')

    def do_downtranslate(self, id):
        in_cpa_file = os.path.join(self.testdatadir,'cppa_ab_'+id+'.xml')
        cpa3_in = etree.parse(in_cpa_file)
        cpa2_out = downtranslate(cpa3_in)
        out_cpa_file = os.path.join(self.testdatadir,'cppa_ab_'+id+'_v2.xml')
        cpa_file= os.path.join(out_cpa_file)
        fd = open(cpa_file, 'wb')
        fd.write(lxml.etree.tostring(cpa2_out, pretty_print=True))
        fd.close()




