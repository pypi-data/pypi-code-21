import mock
import unittest

from pastry.resources.search import Search


class SearchTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.search.Base.index', return_value='index')
    def test_index(self, base):
        self.assertEqual(Search.index(), 'index')

    @mock.patch('pastry.resources.search.urllib.urlencode', return_value='query_string')
    @mock.patch('pastry.resources.search.PastryClient.call', return_value='results')
    @mock.patch('pastry.resources.search.Base.escape_query', return_value='escaped')
    def test_run(self, escape_query, call, urlencode):
        self.assertEqual(Search.run(
            'index',
            query='query',
            rows=1,
            start=1,
            filters={'name': 'name'}
        ), 'results')
        urlencode.assert_called_with({'q': 'query', 'rows': 1, 'start': 1})
        escape_query.assert_called_with('query_string')
        call.assert_called_with(
            '/organizations/%(org)s/search/index?escaped',
            method='POST',
            data={'name': 'name'}
        )
