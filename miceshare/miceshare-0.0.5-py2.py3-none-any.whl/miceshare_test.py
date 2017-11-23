# coding: utf-8

import unittest
import miceshare


class MiceShareTest(unittest.TestCase):
    """
        测试miceshare接口
    """

    def test_get_get_stock_basics(self):
        df = miceshare.get_stock_basics()
        print(df.shape)
        print(df.head())

    def test_get_concept(self):
        c = miceshare.get_concept_classified()
        print(c[c['stock_code']=='600822']['board'].tolist())

        c = miceshare.get_concept_classified()
        print(c[c['board'] == '5G概念'])

        c = miceshare.get_concept_classified()
        print(c[c['board'] == '国企改革'])



