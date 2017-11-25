
import unittest, cppa3, logging, lxml, os
from cppa3.match import match
from cppa3.match import MatchException

from inspect import getsourcefile
from os.path import abspath, dirname, join

from copy import deepcopy

class MatchTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="match_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.unify_testdatadir = join(thisdir,'data')
        self.match_testdatadir = join(thisdir,'data_match')
        self.parser = lxml.etree.XMLParser(remove_blank_text=True)

    def do_reverse_match(self, id):
        logging.info('------------------')
        logging.info('Running test {}'.format(id))
        for letter in ['a','b']:
            logging.info('Match CPP {} against CPA for id {}'.format(letter, id))
            # Reuse the data from the unify test set.  Each CPP that
            # was successfully unified into a CPA should match that CPA
            cpp_file = os.path.join(self.unify_testdatadir,'cpp_{}_{}.xml'.format(letter, id))
            cpp =  (lxml.etree.parse(cpp_file, self.parser)).getroot()
            cpa_file = os.path.join(self.unify_testdatadir,'cppa_ab_{}.xml'.format(id))
            cpa =  (lxml.etree.parse(cpa_file, self.parser)).getroot()
            partyname = match(cpp, cpa)
            logging.info('CPA {} matches CPP {} for party {}'.format(id, letter, partyname))

    def do_non_match_check(self, id):
        logging.info('------------------')
        logging.info('Running non match test {}'.format(id))
        try:
            cpp_file = os.path.join(self.match_testdatadir,'cpp_{}.xml'.format(id))
            cpp =  (lxml.etree.parse(cpp_file, self.parser)).getroot()
            cpa_file = os.path.join(self.match_testdatadir,'cpa_{}.xml'.format(id))
            cpa =  (lxml.etree.parse(cpa_file, self.parser)).getroot()
            match(cpp, cpa)
        except MatchException as e:
            logging.info('MatchException: {}'.format(e.value))
            raise e

    def test_0001(self):
       self.do_reverse_match('0001')

    def test_0007(self):
       self.do_reverse_match('0007')

    def test_0008(self):
       self.do_reverse_match('0008')

    def test_0009(self):
       self.do_reverse_match('0009')

    def test_0090(self):
       self.do_reverse_match('0090')

    def test_0091(self):
       self.do_reverse_match('0091')

    def test_0120(self):
       self.do_reverse_match('0120')

    def test_0121(self):
       self.do_reverse_match('0121')

    def test_0122(self):
       self.do_reverse_match('0122')


    def test_0060(self):
       self.do_reverse_match('0060')

    def test_0300(self):
       self.do_reverse_match('0300')

    def test_0702(self):
       self.do_reverse_match('0702')

    def test_1000(self):
       self.do_reverse_match('1000')

    def test_1001(self):
       self.do_reverse_match('1001')

    def test_1002(self):
       self.do_reverse_match('1002')

    def test_1006(self):
       self.do_reverse_match('1006')

    def test_1007(self):
       self.do_reverse_match('1007')

    def test_1010(self):
       self.do_reverse_match('1010')

    def test_1011(self):
       self.do_reverse_match('1011')


    # Skipped,  CPPs use channel features
    #
    #def test_1012(self):
    #   self.do_reverse_match('1012')
    #def test_1020(self):
    #   self.do_reverse_match('1020')

    def test_1100(self):
       self.do_reverse_match('1100')

    def test_1101(self):
       self.do_reverse_match('1101')

    def test_1102(self):
       self.do_reverse_match('1102')

    def test_1103(self):
       self.do_reverse_match('1103')

    def test_1120(self):
       self.do_reverse_match('1120')

    def test_1121(self):
       self.do_reverse_match('1121')

    def test_1124(self):
       self.do_reverse_match('1124')

    def test_1125(self):
       self.do_reverse_match('1125')

    def test_1126(self):
       self.do_reverse_match('1126')

    def test_1600(self):
       self.do_reverse_match('1600')

    def test_2100(self):
       self.do_reverse_match('2100')

    def test_2110(self):
       self.do_reverse_match('2110')

    def test_2115(self):
       self.do_reverse_match('2115')

    def test_2117(self):
       self.do_reverse_match('2117')

    def test_2120(self):
       self.do_reverse_match('2120')

    def test_2121(self):
       self.do_reverse_match('2121')

    def test_2125(self):
       self.do_reverse_match('2125')

    def test_2140(self):
       self.do_reverse_match('2140')

    def test_2140(self):
       self.do_reverse_match('2140')

    def test_2141(self):
       self.do_reverse_match('2141')

    def test_2142(self):
       self.do_reverse_match('2142')

    def test_2145(self):
       self.do_reverse_match('2145')

    def test_2146(self):
       self.do_reverse_match('2146')

    def test_2147(self):
       self.do_reverse_match('2147')

    def test_2148(self):
       self.do_reverse_match('2148')

    def test_2170(self):
       self.do_reverse_match('2170')


    def test_2300(self):
       self.do_reverse_match('2300')

    def test_2303(self):
       self.do_reverse_match('2303')


    def test_3000(self):
       self.do_reverse_match('3000')

    def test_3001(self):
       self.do_reverse_match('3001')

    def test_3002(self):
       self.do_reverse_match('3002')

    def test_3003(self):
       self.do_reverse_match('3003')

    def test_3004(self):
       self.do_reverse_match('3004')

    def test_3050(self):
       self.do_reverse_match('3050')

    def test_3060(self):
       self.do_reverse_match('3060')

    def test_3062(self):
       self.do_reverse_match('3062')

    def test_3100(self):
       self.do_reverse_match('3100')

    def test_3200(self):
       self.do_reverse_match('3200')

    def test_3201(self):
       self.do_reverse_match('3201')

    def test_3075(self):
       self.do_reverse_match('3075')

    def test_3076(self):
       self.do_reverse_match('3076')

    def test_3210(self):
       self.do_reverse_match('3210')

    def test_3300(self):
       self.do_reverse_match('3300')

    def test_3305(self):
       self.do_reverse_match('3305')

    def test_3310(self):
       self.do_reverse_match('3310')

    def test_3320(self):
       self.do_reverse_match('3320')

    def test_3321(self):
       self.do_reverse_match('3321')

    def test_3400(self):
       self.do_reverse_match('3400')

    def test_4000(self):
       self.do_reverse_match('4000')

    def test_4001(self):
       self.do_reverse_match('4001')

    def test_4010(self):
       self.do_reverse_match('4010')

    def test_4020(self):
       self.do_reverse_match('4020')

    def test_4030(self):
       self.do_reverse_match('4030')

    def test_4031(self):
       self.do_reverse_match('4031')

    # skipped,  uses channel feature
    #def test_4100(self):
    #   self.do_reverse_match('4100')

    def test_4101(self):
       self.do_reverse_match('4101')

    def test_5000(self):
       self.do_reverse_match('5000')

    def test_5001(self):
       self.do_reverse_match('5001')

    def test_5002(self):
       self.do_reverse_match('5002')

    def test_5003(self):
       self.do_reverse_match('5003')

    def test_5006(self):
       self.do_reverse_match('5006')



    # the party in the CPA does not match any party in the CPP on name
    def test_nm_0001(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0001')

    # the party in the CPA does not match any party in the CPP on party id
    def test_nm_0002(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0002')

    # the CPA has a role pair that is not in the CPP
    def test_nm_0003(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0003')

    # the CPA has a service that is not in the CPP
    def test_nm_0004(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0004')

    # the CPA has an action that is not in the CPP
    def test_nm_0005(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0005')

    # the CPA uses an incompatible named channel
    def test_nm_0006(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0006')

    # the CPA uses an incompatible transport
    def test_nm_0007(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0007')

    # CPA has a delegation for the wrong party
    def test_nm_0008(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0008')

    # CPA has a delegation for the wrong counterparty
    def test_nm_0009(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0009')

    # CPA is for a party that is not in the CPP party allowed, CPP party
    # is PartyInfo
    def test_nm_0010(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0010')

    # CPA is for a party that is not in the CPP party allowed, CPP party
    # is CounterPartyInfo
    def test_nm_0011(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0011')

    # CPA is for a party that is not in the CPP party allowed at ActionBinding level
    # CPP party is CounterPartyInfo
    def test_nm_0012(self):
        self.assertRaises(MatchException, self.do_non_match_check, '0012')
