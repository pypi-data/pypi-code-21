#!/usr/bin/python
"""EXAMPLE unittest for AmazonBook

"""

import unittest
import logging

from webparser.amazon import AmazonBook

__version__ = r'1.00'
__author__ = r'Mikhail Ananyevskiy (aka soomrack)'

logging.basicConfig(level=logging.INFO)


class TestAmazonBook(unittest.TestCase):
    amazon_book = None

    @classmethod
    def setUpClass(cls):
        url = 'https://www.amazon.com/Bayesian-Networks-Introduction-Timo-Koski/dp/0470743042/'
        cls.amazon_book = AmazonBook(url)

    def setUp(self):
        self.amazon_book = TestAmazonBook.amazon_book

    def test_title(self):
        self.assertEqual(self.amazon_book.data['title'],
                         'Bayesian Networks: An Introduction')

    @unittest.skip('Cover url is not permanent')
    def test_cover_url(self):
        self.assertEqual(self.amazon_book.data['cover_url'],
                         'https://images-na.ssl-images-amazon.com/images/I/513vaXv0l7L._SX308_BO1,204,203,200_.jpg')


if __name__ == '__main__':
    unittest.main()
