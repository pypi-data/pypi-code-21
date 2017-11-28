import os
import requests
import unittest
import logging
import six
import pkg_resources
import platform
from subprocess import CalledProcessError

from civis_jupyter_notebooks import platform_persistence
from civis_jupyter_notebooks.platform_persistence import NotebookManagementError

if (six.PY2 or pkg_resources.parse_version('.'.join(platform.python_version_tuple()[0:2]))
        == pkg_resources.parse_version('3.4')):
    from mock import patch
    from mock import MagicMock
else:
    from unittest.mock import patch
    from unittest.mock import MagicMock

TEST_PLATFORM_OBJECT_ID = '1914'


class MyTest(unittest.TestCase):

    def setUp(self):
        os.environ['CIVIS_API_KEY'] = 'hi mom'
        os.environ['PLATFORM_OBJECT_ID'] = TEST_PLATFORM_OBJECT_ID

        logging.disable(logging.INFO)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_get_nb_from_platform(self, rg, _client, _op):
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, response={})
        platform_persistence.initialize_notebook_from_platform()
        platform_persistence.get_client().notebooks.get.assert_called_with(TEST_PLATFORM_OBJECT_ID)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.__pull_and_load_requirements')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_pull_nb_from_url(self, rg, _client, requirements, _op):
        url = 'http://whatever'
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, response={})
        platform_persistence.get_client().notebooks.get.return_value.notebook_url = url
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = None
        platform_persistence.initialize_notebook_from_platform()
        rg.assert_called_with(url)
        requirements.assert_not_called()

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_throw_error_on_nb_pull(self, rg, _client, _op):
        rg.return_value = MagicMock(spec=requests.Response, status_code=500, response={})
        self.assertRaises(NotebookManagementError,
                          lambda: platform_persistence.initialize_notebook_from_platform())

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.__pull_and_load_requirements')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_pull_requirements(self, rg, _client, requirements, _op):
        url = 'http://whatever'
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, response={})
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = url
        platform_persistence.initialize_notebook_from_platform()
        requirements.assert_called_with(url)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.__pull_and_load_requirements')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_error_on_requirements_pull(self, rg, _client, _requirements, _op):
        url = 'http://whatever'
        rg.return_value = MagicMock(spec=requests.Response, status_code=500, response={})
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = url
        self.assertRaises(NotebookManagementError,
                          lambda: platform_persistence.initialize_notebook_from_platform())

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_post_save_fetches_urls_from_api(self, _rput, client, _ccc, _op):
        post_save = platform_persistence.post_save(git_enabled=False)
        post_save({'type': 'notebook'}, '', {})
        platform_persistence.get_client().notebooks.list_update_links.assert_called_with(TEST_PLATFORM_OBJECT_ID)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    @patch('civis_jupyter_notebooks.platform_persistence.save_notebook')
    def test_post_save_performs_two_put_operations(self, save, rput, _client, _ccc, _op):
        post_save = platform_persistence.post_save(git_enabled=False)
        post_save({'type': 'notebook'}, '', {})
        self.assertTrue(save.called)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    @patch('civis_jupyter_notebooks.platform_persistence.save_notebook')
    def test_post_save_for_git_does_not_call_save_notebook(self, save, rput, _client, _ccc, _op):
        post_save = platform_persistence.post_save(git_enabled=True)
        post_save({'type': 'notebook'}, '', {})
        self.assertFalse(save.called)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    @patch('civis_jupyter_notebooks.platform_persistence.save_notebook')
    @patch('civis_jupyter_notebooks.platform_persistence.get_update_urls')
    def test_post_save_skipped_for_non_notebook_types(self, guu, save, _rput, _client, _ccc, _op):
        post_save = platform_persistence.post_save(git_enabled=False)
        post_save({'type': 'blargggg'}, '', {})
        self.assertFalse(guu.called)
        self.assertFalse(save.called)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_post_save_generates_preview(self, _rput, _client, check_call, _op):
        post_save = platform_persistence.post_save(git_enabled=False)
        post_save({'type': 'notebook'}, 'x/y', {})
        check_call.assert_called_with(['jupyter', 'nbconvert', '--to', 'html', 'y'], cwd='x')

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_post_save_for_git_generates_preview(self, _rput, _client, check_call, _op):
        post_save = platform_persistence.post_save(git_enabled=True)
        post_save({'type': 'notebook'}, 'x/y', {})
        check_call.assert_called_with(['jupyter', 'nbconvert', '--to', 'html', 'y'], cwd='x')

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_generate_preview_throws_error_on_convert(self, _rput, _client, check_call, _op):
        check_call.side_effect = CalledProcessError('foo', 255)
        self.assertRaises(NotebookManagementError,
                          lambda: platform_persistence.generate_and_save_preview('http://notebook_url_in_s3', 'os/path'))
        check_call.assert_called_with(['jupyter', 'nbconvert', '--to', 'html', 'path'], cwd='os')

    @patch('civis.APIClient')
    def test_will_regenerate_api_client(self, mock_client):
        platform_persistence.get_client()
        mock_client.assert_called_with(resources='all')


if __name__ == '__main__':
    unittest.main()
