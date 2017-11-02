###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: tests.py 1600 2008-12-31 02:20:46Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import unittest
import os

class ParseConfTest(unittest.TestCase):

    def test_portSplit(self):
        '''portSplit - split a string port description into a range'''
        from p01.elasticstub.testing import portSplit
        res = portSplit('1000')
        self.assertEqual(res, [1000])
        res = portSplit('1000-1003')
        self.assertEqual(res, [1000, 1001, 1002])

    def test_parseConf(self):
        '''parseConf - get the important parts out of a config dict'''
        from p01.elasticstub.testing import parseConf
        config = \
        {'cluster': {'name': 'p01_elasticstub_testing'},
         'http': {'port': '45200-45300'},
         'index': {'store': {'type': 'memory'}},
         'network': {'host': 'localhost'},
         'transport': {'tcp': {'port': '45300 - 45400'}}}
        res = parseConf(config)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['clusterName'], 'p01_elasticstub_testing')
        self.assertEqual(res['host'], 'localhost')
        self.assertEqual(res['httpPort'][0], 45200)
        self.assertEqual(res['httpPort'][-1], 45299)
        self.assertEqual(res['transportPort'][0], 45300)
        self.assertEqual(res['transportPort'][-1], 45399)
        config['http'] = {'port': '45200'}
        res = parseConf(config)
        self.assertEqual(res['httpPort'], [45200])

    def test_parseConf_defaults(self):
        '''parseConf - get the important parts out of a config dict'''
        from p01.elasticstub.testing import parseConf
        config = {}
        res = parseConf(config)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['clusterName'], 'es-testing')
        self.assertEqual(res['host'], 'localhost')
        self.assertEqual(res['httpPort'][0], 9200)
        self.assertEqual(res['httpPort'][-1], 9299)
        self.assertEqual(res['transportPort'][0], 9300)
        self.assertEqual(res['transportPort'][-1], 9399)
        config = None
        res = parseConf(config)
        self.assertEqual(res['clusterName'], 'es-testing')
        self.assertEqual(res['host'], 'localhost')

    def test_readConfFile_yaml(self):
        '''readConfFile - load a yaml or json config file into a dict'''
        from p01.elasticstub.testing import readConfFile
        here = os.path.dirname(__file__)
        confPath = os.path.join(here, 'config_yaml')
        config = readConfFile(confPath)
        self.assertTrue(isinstance(config, dict))
        self.assertEqual(config['cluster'], {'name': 'p01_elasticstub_testing'})
        self.assertEqual(config['http'], {'port': '45200-45300'})

    def test_readConfFile_json(self):
        '''readConfFile - load a yaml or json config file into a dict'''
        from p01.elasticstub.testing import readConfFile
        here = os.path.dirname(__file__)
        confPath = os.path.join(here, 'config_json')
        config = readConfFile(confPath)
        self.assertTrue(isinstance(config, dict))
        self.assertEqual(config['cluster'], {'name': 'testing'})
        self.assertEqual(config['http'], {'port': '45200-45300'})

    def test_readConfFile_empty(self):
        """
        readConfFile - load an empty yaml config file into a dict.
        This is what happens with the default config file from the
        elasticsearch download: yaml loading returns None
        """
        from p01.elasticstub.testing import readConfFile
        here = os.path.dirname(__file__)
        confPath = os.path.join(here, 'config_empty')
        config = readConfFile(confPath)
        self.assertEqual(config, None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ParseConfTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
