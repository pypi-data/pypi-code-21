import mock
import unittest

from pastry.exceptions import HttpError
from pastry.resources.cookbooks import Cookbooks


class CookbooksTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.cookbooks.Base.index', return_value='index')
    def test_index(self, base):
        self.assertEqual(Cookbooks.index(), 'index')

    @mock.patch('pastry.resources.cookbooks.Base.exists', return_value=True)
    def test_exists(self, base):
        self.assertEqual(Cookbooks.exists('group'), True)

    @mock.patch('pastry.resources.cookbooks.PastryClient.call', return_value='contents')
    def test_contents(self, call):
        self.assertEqual(Cookbooks.contents('name', version='version'), 'contents')
        call.assert_called_with('/organizations/%(org)s/cookbooks/name/version')

    def test_parse_filename(self):
        self.assertEqual(['root_files', 'default', 'filename'], Cookbooks.parse_filename('filename'))
        self.assertEqual(
            ['filetype', 'specificity', 'filename'],
            Cookbooks.parse_filename('filetype/specificity/filename')
        )

    @mock.patch('pastry.resources.cookbooks.Cookbooks.parse_filename', return_value=[
        'filetype', 'specificity', 'filename'
    ])
    @mock.patch('pastry.resources.cookbooks.Cookbooks.contents', return_value={
        'filetype': [{
            'name': 'filename',
            'specificity': 'specificity',
            'url': 'url'
        }]
    })
    @mock.patch('pastry.resources.cookbooks.requests.get')
    def test_file_content(self, get, contents, parse):
        response = mock.MagicMock()
        response.text = 'contents'
        response.ok = False
        get.return_value = response
        self.assertRaises(HttpError, Cookbooks.file_content, 'cookbook', 'filename')
        response.ok = True
        self.assertEqual(Cookbooks.file_content('cookbook', 'filename'), response.text)
