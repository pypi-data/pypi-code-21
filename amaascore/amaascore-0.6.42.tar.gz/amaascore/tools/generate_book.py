from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
import random

from amaascore.books.book import Book


def generate_book(asset_manager_id=None, book_id=None, owner_id=None, party_id=None, book_type='Trading',
                  business_unit=None):

    book = Book(asset_manager_id=asset_manager_id or random.randint(1, 1000),
                book_id=book_id or random_string(10),
                book_type=book_type,
                owner_id=owner_id or random.randint(1, 1000),
                base_currency=random.choice(['USD', 'SGD', 'HKD', 'EUR']),
                business_unit=business_unit or random.choice(['Equities', 'Emerging Markets', 'Treasury']),
                party_id=party_id or random_string(10))  # Can also be the asset_manager_id of the book

    return book
