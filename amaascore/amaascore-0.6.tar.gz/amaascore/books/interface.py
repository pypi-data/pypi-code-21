from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.books.utils import json_to_book
from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface


class BooksInterface(Interface):

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        logger = logger or logging.getLogger(__name__)
        super(BooksInterface, self).__init__(endpoint=endpoint, endpoint_type='books', environment=environment,
                                             username=username, password=password, logger=logger)

    def new(self, book):
        self.logger.info('New Book - Asset Manager: %s - Book ID: %s', book.asset_manager_id, book.book_id)
        url = '%s/books/%s' % (self.endpoint, book.asset_manager_id)
        response = self.session.post(url, json=book.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Book - Asset Manager: %s - Book ID: %s', book.asset_manager_id,
                             book.book_id)
            book = json_to_book(response.json())
            return book
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend(self, book):
        self.logger.info('Amend Book - Asset Manager: %s - Book ID: %s', book.asset_manager_id, book.book_id)
        url = '%s/books/%s/%s' % (self.endpoint, book.asset_manager_id, book.book_id)
        response = self.session.put(url, json=book.to_interface())
        if response.ok:
            self.logger.info('Successfully Amended Book - Asset Manager: %s - Book ID: %s', book.asset_manager_id,
                             book.book_id)
            book = json_to_book(response.json())
            return book
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, book_id, version=None):
        self.logger.info('Retrieve Book - Asset Manager: %s - Book ID: %s', asset_manager_id, book_id)
        url = '%s/books/%s/%s' % (self.endpoint, asset_manager_id, book_id)
        if version:
            url += '?version=%d' % int(version)
        response = self.session.get(url)
        if response.ok:
            self.logger.info('Successfully Retrieved Book - Asset Manager: %s - Book ID: %s', asset_manager_id,
                             book_id)
            return json_to_book(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retire(self, asset_manager_id, book_id):
        self.logger.info('Retire Book - Asset Manager: %s - Book ID: %s', asset_manager_id, book_id)
        url = '%s/books/%s/%s' % (self.endpoint, asset_manager_id, book_id)
        json = {'book_status': 'Retired'}
        response = self.session.patch(url, json=json)
        if response.ok:
            self.logger.info('Successfully Retired Book - Asset Manager: %s - Book ID: %s', asset_manager_id, book_id)
            return json_to_book(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_id, book_ids=None, business_units=None, 
                     owner_ids=None, party_ids=None, book_statuses=None):
        self.logger.info('Search Books - Asset Manager: %s', asset_manager_id)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if book_ids:
            search_params['book_ids'] = ','.join(book_ids)
        if business_units:
            search_params['business_units'] = ','.join(business_units)
        if owner_ids:
            search_params['owner_ids'] = ','.join(owner_ids)
        if party_ids:
            search_params['party_ids'] = ','.join(party_ids)
        if book_statuses:
            search_params['book_statuses'] = ','.join(book_statuses)
        url = '%s/books/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url, params=search_params)
        if response.ok:
            books = [json_to_book(json_book)
                     for json_book in response.json()] if response.json() else None
            self.logger.info('Returned %s Books.', len(books) if books else 0)
            return books
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def books_by_asset_manager(self, asset_manager_id):
        self.logger.info('Retrieve Books by Asset Manager: %s', asset_manager_id)
        url = '%s/books/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            books = [json_to_book(json_book) for json_book in response.json()]
            self.logger.info('Returned %s Books.', len(books))
            return books
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def book_config(self, asset_manager_id):
        self.logger.info('Retrieve Book Config by Asset Manager: %s', asset_manager_id)
        url = '%s/book_config/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            book_config = response.json()
            self.logger.info('Successfully returned Book Config for %s', asset_manager_id)
            return book_config
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def clear(self, asset_manager_id):
        """ This method deletes all the data for an asset_manager_id.
            It should be used with extreme caution.  In production it
            is almost always better to Retire rather than delete. """
        self.logger.info('Clear Books - Asset Manager: %s', asset_manager_id)
        url = '%s/clear/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            count = response.json().get('count', 'Unknown')
            self.logger.info('Deleted %s Books.', count)
            return count
        else:
            self.logger.error(response.text)
            response.raise_for_status()
