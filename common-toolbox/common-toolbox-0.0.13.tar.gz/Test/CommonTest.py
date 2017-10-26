#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:27
# @Author  : Hou Rong
# @Site    : 
# @File    : CommonTest.py
# @Software: PyCharm
# from __future__ import unicode_literals
import six
import unittest
from toolbox.Common import *


class TestCommon(unittest.TestCase):
    def test_dot_get(self):
        self.assertEqual(dot_get({'a': 2, 'b': {'a': 2}}, 'b.a.c'), '')
        self.assertEqual(dot_get({'a': 2, 'b': {'a': 2}}, 'b.a'), 2)

    def test_dot_get_multi(self):
        self.assertEqual(dot_get({'a': 2, 'b': {'a': 2}}, 'b.a.c', 'b.a'), 2)

    def test_dot_get_with_list(self):
        self.assertEqual(dot_get({u'hotel': {u'zoneCode': 2, u'code': 254266, u'name': u'Qualys-Hotel Arianis',
                                             u'destinationCode': u'ELF', u'totalSellingRate': u'3275.53',
                                             u'checkIn': u'2017-09-23', u'rooms': [{u'code': u'ROO.ST', u'rates': [
                {u'sellingRate': u'3275.53',
                 u'rateKey': u'20170923|20170924|W|197|254266|ROO.ST|ID_B2B_50|FB|PAQ|1~2~0||P@9C2094326CDF424E81CCBDFC5B054C180816',
                 u'adults': 2, u'paymentType': u'AT_WEB', u'discountPCT': u'10.00', u'rateType': u'BOOKABLE',
                 u'packaging': True, u'discount': u'327.55', u'rooms': 1,
                 u'cancellationPolicies': [{u'amount': u'207.32', u'from': u'2017-09-15T23:59:00+02:00'},
                                           {u'amount': u'414.65', u'from': u'2017-09-20T23:59:00+02:00'}],
                 u'boardName': u'\u5168\u98df\u5bbf', u'net': u'2947.98', u'children': 0, u'boardCode': u'FB',
                 u'rateClass': u'NOR'}], u'name': u'\u623f\u9593 \u6807\u51c6'}],
                                             u'destinationName': u'\u8d1d\u5c14\u798f', u'currency': u'CNY',
                                             u'categoryCode': u'3EST', u'longitude': u'6.831134',
                                             u'totalNet': u'2947.98', u'latitude': u'47.515268',
                                             u'zoneName': u'Montbeliard', u'checkOut': u'2017-09-24', u'upselling': {
                u'rooms': [{u'code': u'ROO.ST', u'rates': [{u'sellingRate': u'3282.83',
                                                            u'rateKey': u'20170923|20170924|W|197|254266|ROO.ST|ID_B2B_50|FB|PAQNRF|1~2~0||P@E4E3B8CD8269437F983B5E334A1371120817',
                                                            u'adults': 2, u'paymentType': u'AT_WEB',
                                                            u'discountPCT': u'10.00', u'rooms': 1,
                                                            u'rateType': u'RECHECK', u'packaging': True,
                                                            u'discount': u'328.28', u'rateup': u'7.30',
                                                            u'allotment': 99, u'cancellationPolicies': [
                        {u'amount': u'186.59', u'from': u'2017-09-15T23:59:00+02:00'},
                        {u'amount': u'373.19', u'from': u'2017-09-20T23:59:00+02:00'}],
                                                            u'boardName': u'\u5168\u98df\u5bbf', u'net': u'2954.55',
                                                            u'children': 0, u'boardCode': u'FB', u'rateClass': u'NRF'},
                                                           {u'sellingRate': u'3282.83',
                                                            u'rateKey': u'20170923|20170924|W|197|254266|ROO.ST|ID_B2B_50|FB|NOR|1~2~0||N@E4E3B8CD8269437F983B5E334A1371120817',
                                                            u'adults': 2, u'paymentType': u'AT_WEB',
                                                            u'discountPCT': u'10.00', u'rooms': 1,
                                                            u'rateType': u'RECHECK', u'packaging': False,
                                                            u'discount': u'328.28', u'rateup': u'7.30',
                                                            u'allotment': 99, u'cancellationPolicies': [
                                                               {u'amount': u'186.59',
                                                                u'from': u'2017-09-15T23:59:00+02:00'},
                                                               {u'amount': u'373.19',
                                                                u'from': u'2017-09-20T23:59:00+02:00'}],
                                                            u'boardName': u'\u5168\u98df\u5bbf', u'net': u'2954.55',
                                                            u'children': 0, u'boardCode': u'FB', u'rateClass': u'NOR'},
                                                           {u'sellingRate': u'3282.83',
                                                            u'rateKey': u'20170923|20170924|W|197|254266|ROO.ST|ID_B2B_50|FB|NRF|1~2~0||N@E4E3B8CD8269437F983B5E334A1371120817',
                                                            u'adults': 2, u'paymentType': u'AT_WEB',
                                                            u'discountPCT': u'10.00', u'rooms': 1,
                                                            u'rateType': u'RECHECK', u'packaging': False,
                                                            u'discount': u'328.28', u'rateup': u'7.30',
                                                            u'allotment': 99, u'cancellationPolicies': [
                                                               {u'amount': u'186.59',
                                                                u'from': u'2017-09-15T23:59:00+02:00'},
                                                               {u'amount': u'373.19',
                                                                u'from': u'2017-09-20T23:59:00+02:00'}],
                                                            u'boardName': u'\u5168\u98df\u5bbf', u'net': u'2954.55',
                                                            u'children': 0, u'boardCode': u'FB', u'rateClass': u'NRF'},
                                                           {u'sellingRate': u'3282.83',
                                                            u'rateKey': u'20170923|20170924|W|197|254266|ROO.ST|ID_B2B_50|FB|PAQ|1~2~0||P@E4E3B8CD8269437F983B5E334A1371120817',
                                                            u'adults': 2, u'paymentType': u'AT_WEB',
                                                            u'discountPCT': u'10.00', u'rooms': 1,
                                                            u'rateType': u'RECHECK', u'packaging': True,
                                                            u'discount': u'328.28', u'rateup': u'7.30',
                                                            u'allotment': 99, u'cancellationPolicies': [
                                                               {u'amount': u'186.59',
                                                                u'from': u'2017-09-15T23:59:00+02:00'},
                                                               {u'amount': u'373.19',
                                                                u'from': u'2017-09-20T23:59:00+02:00'}],
                                                            u'boardName': u'\u5168\u98df\u5bbf', u'net': u'2954.55',
                                                            u'children': 0, u'boardCode': u'FB', u'rateClass': u'NOR'}],
                            u'name': u'\u623f\u9593 \u6807\u51c6'}]}, u'categoryName': u'\u4e09\u661f\u7ea7 '},
                                  u'auditData': {u'timestamp': u'2017-08-09 08:17:58.453',
                                                 u'token': u'a1415cbf-3685-4501-99e5-800c46d776a2',
                                                 u'processTime': u'383', u'environment': u'[int]',
                                                 u'requestHost': u'119.207.76.198',
                                                 u'internal': u'0|9C2094326CDF424E81CCBDFC5B054C180816|CN|05|1|6|||||||||-0.22|V|R|9|1|1~1~2~0||1|TRAVELTINO|1|x7a5zyj9pwztkw9y8kfaev4j||',
                                                 u'release': u'4c0c21f7a3982f3ad0cf88b921c4e04e7c36861f',
                                                 u'serverId': u'sa3RKSJACHXE79K.env#PL'}},
                                 'hotel.rooms.rates.rateType'), 'BOOKABLE')

    def test_i_do_not_care_list_or_dict(self):
        case = ['s', 'd', 'b']
        for index, res in enumerate(i_do_not_care_list_or_dict(case)):
            self.assertEqual(res, case[index])

        case = {'a': 123}
        for i in i_do_not_care_list_or_dict(case):
            self.assertDictEqual(i, case)

    def test_is_legal_false(self):
        self.assertEqual(is_legal(None), False)

    def test_is_legal_true(self):
        self.assertEqual(is_legal('test'), True)

    def test_key_modify(self):
        self.assertEqual(key_modify('  TeST  '), 'test')

    def test_is_chinese_true(self):
        self.assertEqual(is_chinese(u'我'), True)

    def test_is_chinese_false(self):
        self.assertEqual(is_chinese('a'), False)

    def test_is_num_true(self):
        self.assertTrue(is_number(u'1'))

    def test_is_num_false(self):
        self.assertFalse(is_number(u'我'))

    def test_is_alphabet_true(self):
        self.assertTrue(is_alphabet(u'h'))
        self.assertFalse(is_alphabet(u'ñ'))

    def test_is_alphabet_false(self):
        self.assertFalse(is_alphabet(u'我'))

    def test_is_latin_true(self):
        self.assertTrue(is_latin(u'ñ'))

    def test_is_all_latin_true(self):
        self.assertTrue(is_all(u'Español', check_func=is_latin))

    def test_is_all_latin_false(self):
        self.assertFalse(is_all(u'你好世界', check_func=is_latin))

    def test_is_all_chinese_string_true(self):
        self.assertTrue(is_all(u"你好世界", check_func=is_chinese))

    def test_is_all_chinese_string_false(self):
        self.assertFalse(is_all(u"你好世界，Hello World", check_func=is_chinese))

    def test_get_keys(self):
        get_key = GetKey()
        get_key.update_priority({
            ('name', 'name_en'): {
                'daodao': 10,
                'qyer': 5
            },
            ('star', 'grade'): {
                'daodao': 5,
                'qyer': 10
            }
        })

        self.assertEqual(get_key.get_key_by_priority_or_default({'daodao': 'abc', 'qyer': 'bbc'}, 'name'), 'abc')
        self.assertEqual(get_key.get_key_by_priority_or_default({'daodao': 5, 'qyer': 3}, 'grade'), 3)

    def test_get_keys_filter(self):
        get_key = GetKey()
        get_key.update_priority({
            ('name', 'name_en'): {
                'daodao': 10,
                'qyer': 5
            },
            ('star', 'grade'): {
                'daodao': 5,
                'qyer': 10
            }
        })

        def legal_filter(v):
            if v == 'abc':
                return False
            else:
                return True

        get_key.update_filter(legal_filter=legal_filter)

        self.assertEqual(get_key.get_key_by_priority_or_default({'daodao': 'abc', 'qyer': 'bbc'}, 'name'), 'bbc')

    def test_get_keys_special_filter(self):
        get_key = GetKey()
        get_key.update_priority({
            ('name', 'name_en'): {
                'daodao': 10,
                'qyer': 5
            },
            ('star', 'grade'): {
                'daodao': 5,
                'qyer': 10
            }
        })

        def legal_filter(v):
            if v == 'abc':
                return False
            else:
                return True

        self.assertNotEqual(get_key.get_key_by_priority_or_default({'daodao': 'abc', 'qyer': 'bbc'}, 'name'), 'bbc')

        self.assertEqual(get_key.get_key_by_priority_or_default({'daodao': 'abc', 'qyer': 'bbc'}, 'name',
                                                                special_filter=legal_filter), 'bbc')


if __name__ == '__main__':
    unittest.main()
