from __future__ import unicode_literals

import os
import unittest

import mkdocs
from mkdocs import utils
from mkdocs.config import config_options


class OptionallyRequiredTest(unittest.TestCase):

    def test_empty(self):

        option = config_options.OptionallyRequired()
        value = option.validate(None)
        self.assertEqual(value, None)

        self.assertEqual(option.is_required(), False)

    def test_required(self):

        option = config_options.OptionallyRequired(required=True)
        self.assertRaises(config_options.ValidationError,
                          option.validate, None)

        self.assertEqual(option.is_required(), True)

    def test_required_no_default(self):

        option = config_options.OptionallyRequired(required=True)
        value = option.validate(2)
        self.assertEqual(2, value)

    def test_default(self):

        option = config_options.OptionallyRequired(default=1)
        value = option.validate(None)
        self.assertEqual(1, value)

    def test_replace_default(self):

        option = config_options.OptionallyRequired(default=1)
        value = option.validate(2)
        self.assertEqual(2, value)


class TypeTest(unittest.TestCase):

    def test_single_type(self):

        option = config_options.Type(utils.string_types)
        value = option.validate("Testing")
        self.assertEqual(value, "Testing")

    def test_multiple_types(self):
        option = config_options.Type((list, tuple))

        value = option.validate([1, 2, 3])
        self.assertEqual(value, [1, 2, 3])

        value = option.validate((1, 2, 3))
        self.assertEqual(value, (1, 2, 3))

        self.assertRaises(config_options.ValidationError,
                          option.validate, {'a': 1})

    def test_length(self):
        option = config_options.Type(utils.string_types, length=7)

        value = option.validate("Testing")
        self.assertEqual(value, "Testing")

        self.assertRaises(config_options.ValidationError,
                          option.validate, "Testing Long")


class IpAddressTest(unittest.TestCase):

    def test_valid_address(self):
        addr = '127.0.0.1:8000'

        option = config_options.IpAddress()
        value = option.validate(addr)
        self.assertEqual(utils.text_type(value), addr)
        self.assertEqual(value.host, '127.0.0.1')
        self.assertEqual(value.port, 8000)

    def test_valid_IPv6_address(self):
        addr = '[::1]:8000'

        option = config_options.IpAddress()
        value = option.validate(addr)
        self.assertEqual(utils.text_type(value), addr)
        self.assertEqual(value.host, '[::1]')
        self.assertEqual(value.port, 8000)

    def test_named_address(self):
        addr = 'localhost:8000'

        option = config_options.IpAddress()
        value = option.validate(addr)
        self.assertEqual(utils.text_type(value), addr)
        self.assertEqual(value.host, 'localhost')
        self.assertEqual(value.port, 8000)

    def test_default_address(self):
        addr = '127.0.0.1:8000'

        option = config_options.IpAddress(default=addr)
        value = option.validate(None)
        self.assertEqual(utils.text_type(value), addr)
        self.assertEqual(value.host, '127.0.0.1')
        self.assertEqual(value.port, 8000)

    def test_invalid_address_format(self):
        option = config_options.IpAddress()
        self.assertRaises(
            config_options.ValidationError,
            option.validate, '127.0.0.18000'
        )

    def test_invalid_address_type(self):
        option = config_options.IpAddress()
        self.assertRaises(
            config_options.ValidationError,
            option.validate, 123
        )

    def test_invalid_address_port(self):
        option = config_options.IpAddress()
        self.assertRaises(
            config_options.ValidationError,
            option.validate, '127.0.0.1:foo'
        )

    def test_invalid_address_missing_port(self):
        option = config_options.IpAddress()
        self.assertRaises(
            config_options.ValidationError,
            option.validate, '127.0.0.1'
        )


class URLTest(unittest.TestCase):

    def test_valid_url(self):

        url = "http://mkdocs.org"

        option = config_options.URL()
        value = option.validate(url)
        self.assertEqual(value, url)

    def test_invalid_url(self):

        option = config_options.URL()
        self.assertRaises(config_options.ValidationError,
                          option.validate, "www.mkdocs.org")

    def test_invalid(self):

        option = config_options.URL()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 1)


class RepoURLTest(unittest.TestCase):

    def test_repo_name_github(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_url'], config['repo_url'])
        self.assertEqual(config['repo_name'], "GitHub")

    def test_repo_name_bitbucket(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://bitbucket.org/gutworth/six/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_url'], config['repo_url'])
        self.assertEqual(config['repo_name'], "Bitbucket")

    def test_repo_name_custom(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://launchpad.net/python-tuskarclient"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_url'], config['repo_url'])
        self.assertEqual(config['repo_name'], "Launchpad")

    def test_edit_uri_github(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], '/edit/master/docs/')

    def test_edit_uri_bitbucket(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://bitbucket.org/gutworth/six/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], 'src/default/docs/')

    def test_edit_uri_custom(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://launchpad.net/python-tuskarclient"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config.get('edit_uri'), '')

    def test_repo_name_custom_and_empty_edit_uri(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs",
                  'repo_name': 'mkdocs'}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config.get('edit_uri'), '/edit/master/docs/')


class DirTest(unittest.TestCase):

    def test_valid_dir(self):

        d = os.path.dirname(__file__)
        option = config_options.Dir(exists=True)
        value = option.validate(d)
        self.assertEqual(d, value)

    def test_missing_dir(self):

        d = os.path.join("not", "a", "real", "path", "I", "hope")
        option = config_options.Dir()
        value = option.validate(d)
        self.assertEqual(os.path.abspath(d), value)

    def test_missing_dir_but_required(self):

        d = os.path.join("not", "a", "real", "path", "I", "hope")
        option = config_options.Dir(exists=True)
        self.assertRaises(config_options.ValidationError,
                          option.validate, d)

    def test_file(self):
        d = __file__
        option = config_options.Dir(exists=True)
        self.assertRaises(config_options.ValidationError,
                          option.validate, d)

    def test_incorrect_type_attribute_error(self):
        option = config_options.Dir()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 1)

    def test_incorrect_type_type_error(self):
        option = config_options.Dir()
        self.assertRaises(config_options.ValidationError,
                          option.validate, [])

    def test_doc_dir_is_config_dir(self):

        test_config = {
            'config_file_path': os.path.join(os.path.abspath('.'), 'mkdocs.yml'),
            'docs_dir': '.'
        }

        docs_dir = config_options.Dir()

        test_config['docs_dir'] = docs_dir.validate(test_config['docs_dir'])

        self.assertRaises(config_options.ValidationError,
                          docs_dir.post_validation, test_config, 'docs_dir')


class SiteDirTest(unittest.TestCase):

    def validate_config(self, config):
        """ Given a config with values for site_dir and doc_dir, run site_dir post_validation. """
        site_dir = config_options.SiteDir()
        docs_dir = config_options.Dir()

        config['config_file_path'] = os.path.join(os.path.abspath('..'), 'mkdocs.yml')

        config['docs_dir'] = docs_dir.validate(config['docs_dir'])
        config['site_dir'] = site_dir.validate(config['site_dir'])
        site_dir.post_validation(config, 'site_dir')
        return True  # No errors were raised

    def test_doc_dir_in_site_dir(self):

        j = os.path.join
        # The parent dir is not the same on every system, so use the actual dir name
        parent_dir = mkdocs.__file__.split(os.sep)[-3]

        test_configs = (
            {'docs_dir': j('site', 'docs'), 'site_dir': 'site'},
            {'docs_dir': 'docs', 'site_dir': '.'},
            {'docs_dir': '.', 'site_dir': '.'},
            {'docs_dir': 'docs', 'site_dir': ''},
            {'docs_dir': '', 'site_dir': ''},
            {'docs_dir': j('..', parent_dir, 'docs'), 'site_dir': 'docs'},
            {'docs_dir': 'docs', 'site_dir': '/'}
        )

        for test_config in test_configs:
            self.assertRaises(config_options.ValidationError,
                              self.validate_config, test_config)

    def test_site_dir_in_docs_dir(self):

        j = os.path.join

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': j('docs', 'site')},
            {'docs_dir': '.', 'site_dir': 'site'},
            {'docs_dir': '', 'site_dir': 'site'},
            {'docs_dir': '/', 'site_dir': 'site'},
        )

        for test_config in test_configs:
            self.assertRaises(config_options.ValidationError,
                              self.validate_config, test_config)

    def test_common_prefix(self):
        """ Legitimate settings with common prefixes should not fail validation. """

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': 'docs-site'},
            {'docs_dir': 'site-docs', 'site_dir': 'site'},
        )

        for test_config in test_configs:
            assert self.validate_config(test_config)


class ThemeTest(unittest.TestCase):

    def test_theme_as_string(self):

        option = config_options.Theme()
        value = option.validate("mkdocs")
        self.assertEqual({'name': 'mkdocs'}, value)

    def test_uninstalled_theme_as_string(self):

        option = config_options.Theme()
        self.assertRaises(config_options.ValidationError,
                          option.validate, "mkdocs2")

    def test_theme_default(self):
        option = config_options.Theme(default='mkdocs')
        value = option.validate(None)
        self.assertEqual({'name': 'mkdocs'}, value)

    def test_theme_as_simple_config(self):

        config = {
            'name': 'mkdocs'
        }
        option = config_options.Theme()
        value = option.validate(config)
        self.assertEqual(config, value)

    def test_theme_as_complex_config(self):

        config = {
            'name': 'mkdocs',
            'custom_dir': 'custom',
            'static_templates': ['sitemap.html'],
            'show_sidebar': False
        }
        option = config_options.Theme()
        value = option.validate(config)
        self.assertEqual(config, value)

    def test_theme_name_is_none(self):

        config = {
            'name': None
        }
        option = config_options.Theme()
        value = option.validate(config)
        self.assertEqual(config, value)

    def test_theme_config_missing_name(self):

        config = {
            'custom_dir': 'custom',
        }
        option = config_options.Theme()
        self.assertRaises(config_options.ValidationError,
                          option.validate, config)

    def test_uninstalled_theme_as_config(self):

        config = {
            'name': 'mkdocs2'
        }
        option = config_options.Theme()
        self.assertRaises(config_options.ValidationError,
                          option.validate, config)

    def test_theme_invalid_type(self):

        config = ['mkdocs2']
        option = config_options.Theme()
        self.assertRaises(config_options.ValidationError,
                          option.validate, config)


class PagesTest(unittest.TestCase):

    def test_old_format(self):

        option = config_options.Pages()
        self.assertRaises(
            config_options.ValidationError,
            option.validate,
            [['index.md', ], ]
        )

    def test_provided_dict(self):

        option = config_options.Pages()
        value = option.validate([
            'index.md',
            {"Page": "page.md"}
        ])
        self.assertEqual(['index.md', {'Page': 'page.md'}], value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')

    def test_provided_empty(self):

        option = config_options.Pages()
        value = option.validate([])
        self.assertEqual(None, value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')

    def test_invalid_type(self):

        option = config_options.Pages()
        self.assertRaises(config_options.ValidationError,
                          option.validate, {})

    def test_invalid_config(self):

        option = config_options.Pages()
        self.assertRaises(config_options.ValidationError,
                          option.validate, [[], 1])


class PrivateTest(unittest.TestCase):

    def test_defined(self):

        option = config_options.Private()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 'somevalue')


class MarkdownExtensionsTest(unittest.TestCase):

    def test_simple_list(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': ['foo', 'bar']
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo', 'bar'],
            'mdx_configs': {}
        }, config)

    def test_list_dicts(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'foo': {'foo_option': 'foo value'}},
                {'bar': {'bar_option': 'bar value'}},
                {'baz': None}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo', 'bar', 'baz'],
            'mdx_configs': {
                'foo': {'foo_option': 'foo value'},
                'bar': {'bar_option': 'bar value'}
            }
        }, config)

    def test_mixed_list(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                'foo',
                {'bar': {'bar_option': 'bar value'}}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo', 'bar'],
            'mdx_configs': {
                'bar': {'bar_option': 'bar value'}
            }
        }, config)

    def test_builtins(self):
        option = config_options.MarkdownExtensions(builtins=['meta', 'toc'])
        config = {
            'markdown_extensions': ['foo', 'bar']
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['meta', 'toc', 'foo', 'bar'],
            'mdx_configs': {}
        }, config)

    def test_duplicates(self):
        option = config_options.MarkdownExtensions(builtins=['meta', 'toc'])
        config = {
            'markdown_extensions': ['meta', 'toc']
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['meta', 'toc'],
            'mdx_configs': {}
        }, config)

    def test_builtins_config(self):
        option = config_options.MarkdownExtensions(builtins=['meta', 'toc'])
        config = {
            'markdown_extensions': [
                {'toc': {'permalink': True}}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['meta', 'toc'],
            'mdx_configs': {'toc': {'permalink': True}}
        }, config)

    def test_configkey(self):
        option = config_options.MarkdownExtensions(configkey='bar')
        config = {
            'markdown_extensions': [
                {'foo': {'foo_option': 'foo value'}}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo'],
            'bar': {
                'foo': {'foo_option': 'foo value'}
            }
        }, config)

    def test_none(self):
        option = config_options.MarkdownExtensions(default=[])
        config = {
            'markdown_extensions': None
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': [],
            'mdx_configs': {}
        }, config)

    def test_not_list(self):
        option = config_options.MarkdownExtensions()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 'not a list')

    def test_invalid_config_option(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'foo': 'not a dict'}
            ]
        }
        self.assertRaises(
            config_options.ValidationError,
            option.validate, config['markdown_extensions']
        )

    def test_invalid_config_item(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                ['not a dict']
            ]
        }
        self.assertRaises(
            config_options.ValidationError,
            option.validate, config['markdown_extensions']
        )

    def test_invalid_dict_item(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'key1': 'value', 'key2': 'too many keys'}
            ]
        }
        self.assertRaises(
            config_options.ValidationError,
            option.validate, config['markdown_extensions']
        )
