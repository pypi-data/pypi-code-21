import itertools
import urllib
from abc import ABCMeta, abstractmethod, abstractproperty

import requests

from ..exceptions import APIError, DoesNotExist, reraise


class BaseCollection(object):
    __metaclass__ = ABCMeta

    def __init__(self, client):
        self.client = client

    def __eq__(self, other):
        return self.client == other.client

    def __ne__(self, other):
        return not self.__eq__(other)

    @abstractproperty
    def url_path(self):
        pass  # pragma: no cover

    @abstractmethod
    def make_item(self, **kwargs):
        pass  # pragma: no cover

    def _fetch(self, path):
        return self.client.api_get_json(path)

    def clone(self, *args, **kwargs):
        return self.__class__(client=self.client, *args, **kwargs)


class AddressableCollection(BaseCollection):
    __metaclass__ = ABCMeta

    def item_url_path(self, item_id):
        url_path = self.url_path
        if not url_path.endswith('/'):
            url_path += '/'
        return '{}{:d}'.format(url_path, item_id)

    def get(self, item_id):
        path = self.item_url_path(item_id)
        try:
            data = self.client.api_get_json(path)
        except requests.RequestException as exc:
            if exc.response.status_code == 404:
                raise DoesNotExist
            else:
                reraise(APIError)
        return self.make_item(**data)


class PaginatableCollection(BaseCollection):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.per_page = kwargs.pop('per_page', 25)
        super(PaginatableCollection, self).__init__(*args, **kwargs)
        self._page_meta = None

    def _fetch(self, path):
        response = super(PaginatableCollection, self)._fetch(path)
        self._page_meta = response['page']
        return response

    def make_query_dict(self, **kwargs):
        query_dict = {
            'page': kwargs['page_index'],
            'size': self.per_page,
        }
        return query_dict

    @abstractmethod
    def make_item(self, **kwargs):
        pass  # pragma: no cover

    def _fetch_page(self, page_index):
        query_dict = self.make_query_dict(page_index=page_index)
        query = urllib.urlencode(query_dict)
        url = '{}?{}'.format(self.url_path, query)
        return self._fetch(url)

    def _iterate(self, start_page=0, follow_links=True):
        try:
            response = self._fetch_page(start_page)
        except requests.RequestException as exc:
            if exc.response.status_code == 404:
                return
            else:
                reraise(APIError)
        while True:
            for project_record in response['content']:
                yield self.make_item(**project_record)
            next_url = None
            for link in response.get('links', ()):
                if link.get('rel') == 'next':
                    next_url = link.get('href')
                    break
            if follow_links and next_url:
                response = self._fetch(next_url)
            else:
                break

    def __eq__(self, other):
        return all((
            super(PaginatableCollection, self).__eq__(other),
            self.per_page == other.per_page,
            ))

    def __len__(self):
        if self._page_meta is None:
            self._fetch_page(0)
        return self._page_meta['totalElements']

    def __iter__(self):
        for project in self._iterate():
            yield project

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start is None:
                page_index = 0
                start_index = None
            else:
                page_index = key.start / self.per_page
                start_index = key.start - (page_index * self.per_page)
            if key.stop is None:
                stop_index = None
            else:
                stop_index = key.stop - (page_index * self.per_page)
            iterator = self._iterate(page_index)
            return itertools.islice(iterator, start_index, stop_index, key.step)
        elif isinstance(key, (int, long)):
            if key < 0 or key > len(self) - 1:
                raise IndexError('Index out of range')
            page_index = key / self.per_page
            response = self._fetch_page(page_index)
            item_index = key - (page_index * self.per_page)
            return self.make_item(**response['content'][item_index])
        else:
            raise TypeError('Indices must be integers, not {}'.format(type(key)))

    @property
    def page_count(self):
        if self._page_meta is None:
            self._fetch_page(0)
        return self._page_meta['totalPages']

    def clone(self, *args, **kwargs):
        return super(PaginatableCollection, self).clone(
            per_page=self.per_page,
            *args,
            **kwargs
        )

    def get_page(self, page_index):
        """
        Returns an iterator of items on the requested page
        """
        return self._iterate(page_index, False)

    def filter(self, **kwargs):
        """
        Returns an iterator of items matching the specified criteria. Note that
        this operation is O(n).
        """
        def matches(item):
            for key, value in kwargs.items():
                item_value = getattr(item, key, None)
                if value != item_value:
                    return False
            return True
        for item in itertools.ifilter(matches, self):
            yield item

    def find(self, **kwargs):
        """
        Returns the first item matching the specified criteria, or raises
        DoesNotExist if no items match. Note that this operation is O(n).
        """
        for item in self.filter(**kwargs):
            return item
        raise DoesNotExist


class PaginatableAddressableCollection(AddressableCollection, PaginatableCollection):
    __metaclass__ = ABCMeta


class SortablePaginatableAddressableCollection(PaginatableAddressableCollection):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.sort_by = kwargs.pop('sort_by', None)
        super(SortablePaginatableAddressableCollection, self).__init__(*args, **kwargs)

    def __eq__(self, other):
        return all((
            super(SortablePaginatableAddressableCollection, self).__eq__(other),
            self.sort_by == other.sort_by,
            ))

    @abstractproperty
    def url_path(self):
        pass  # pragma: no cover

    @abstractmethod
    def make_item(self, **kwargs):
        pass  # pragma: no cover


    def make_query_dict(self, **kwargs):
        query_dict = super(SortablePaginatableAddressableCollection, self).make_query_dict(**kwargs)
        if self.sort_by:
            query_dict.update({
                'sort': self.sort_by,
            })
        return query_dict

    def clone(self, *args, **kwargs):
        return super(SortablePaginatableAddressableCollection, self).clone(
            sort_by=self.sort_by,
            *args,
            **kwargs
        )

    def sort(self, sort_by):
        clone = self.clone()
        clone.sort_by = sort_by
        return clone
