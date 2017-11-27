__author__ = 'pvde'

import cppa3.pmode, json, os, traceback, logging

import unittest

from inspect import getsourcefile
from os.path import abspath, dirname, join

class PModeTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="pmode_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.testdatadir = join(thisdir,'data')


    def run_test(self, testid):
        cpafile = os.path.join(self.testdatadir, 'cppa_ab_{}.xml'.format(testid))
        pmodes=[]
        try:
            logging.info('Processing test {} in {}'.format(testid, cpafile))
            pmodes = cppa3.pmode.load_pmodes_from_cpaf(cpafile)
            outfile = os.path.join(self.testdatadir,'pmode_{}.json'.format(testid))
            fd = open(outfile,'w')
            json.dump(pmodes, fd, sort_keys=True, indent=3)
            fd.close()
            logging.info('Created {} pmode(s) into {}'.format(len(pmodes), outfile))
        except:
            exception = traceback.format_exc()
            logging.error("Exception processing {}: {}".format(testid, exception))

    def test_1000(self):
        self.run_test('1000')

    def test_1001(self):
        self.run_test('1001')

    def test_1006(self):
        self.run_test('1006')

    def test_1007(self):
        self.run_test('1007')

    def test_1010(self):
        self.run_test('1010')

    def test_1011(self):
        self.run_test('1011')

    def test_1100(self):
        self.run_test('1100')

    def test_1101(self):
        self.run_test('1101')

    def test_1102(self):
        self.run_test('1102')

    def test_1103(self):
        self.run_test('1103')

    def test_1120(self):
        self.run_test('1120')

    def test_1121(self):
        self.run_test('1121')

    def test_1124(self):
        self.run_test('1125')

    def test_1126(self):
        self.run_test('1126')

    def test_1128(self):
        self.run_test('1128')

    def test_1140(self):
        self.run_test('1140')

    def test_1141(self):
        self.run_test('1141')

    def test_1142(self):
        self.run_test('1142')

    def test_1143(self):
        self.run_test('1143')

    def test_1144(self):
        self.run_test('1144')

    def test_1145(self):
        self.run_test('1145')

    def test_1146(self):
        self.run_test('1146')

    def test_1147(self):
        self.run_test('1147')

    def test_1200(self):
        self.run_test('1200')

    def test_1202(self):
        self.run_test('1202')

    def test_1205(self):
        self.run_test('1205')

    def test_1206(self):
        self.run_test('1206')


