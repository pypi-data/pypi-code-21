"""
Some testing tools that coop projects can use.

Most projects will want to do something like:

.. code-block:: python

    from coop.test import (
        TestThingsWithContentMixin, TestThingsWithoutContentMixin)
    from django.test import TestCase

    class TestContentThings(TestThingsWithContentMixin, TestCase):
        def setUp(self):
            super().setUp()
            root_page = Page.objects.get(pk=1)
            self.home = root_page.add_child(instance=HomePage(
                title='Home'))
            self.site = Site.objects.create(
                root_page=self.home,
                hostname='localhost',
                is_default_site=True)

    class TestOtherThings(TestThingsWithoutContentMixin, TestCase):
        pass
"""
from io import StringIO
from unittest import mock
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management import call_command
from wagtail.wagtailimages.tests.utils import get_test_image_file

from coop.utils import testdata


def _nested_form_data(data):
    if isinstance(data, dict):
        items = data.items()
    elif isinstance(data, list):
        items = enumerate(data)

    for key, value in items:
        key = str(key)
        if isinstance(value, (dict, list)):
            for child_keys, child_value in _nested_form_data(value):
                yield [key] + child_keys, child_value
        else:
            yield [key], value


def nested_form_data(data):
    """
    Helper that translates nested form data into hyphen-separated form data:

    >>> nested_form_data({
    ...     'foo': 'bar',
    ...     'parent': {
    ...         'child': 'field',
    ...     },
    ... })
    {'foo': 'bar', 'parent-child': 'field'}
    """
    return {'-'.join(key): value for key, value in _nested_form_data(data)}


def streamfield(items):
    """
    Helper that takes a list of (block, value) tuples and turns it in to
    StreamField form data. Works well with :func:`nested_form_data`:

    >>> nested_form_data({'content': streamfield([
    ...     ('text', '<p>Hello, world</p>'),
    ... ])})
    {
        'content-count': '1',
        'content-0-type': 'text',
        'content-0-value': '<p>Hello, world</p>',
        'content-0-deleted': '',
    }
    """
    def to_block(index, item):
        block, value = item
        return {'type': block, 'value': value, 'deleted': '', 'order': index}
    data_dict = {str(index): to_block(index, item)
                 for index, item in enumerate(items)}
    data_dict['count'] = str(len(data_dict))
    return data_dict


def inline_formset(items, initial=0, min=0, max=1000):
    """
    Helper that takes a list of form data for an InlineFormset and translates
    it in to valid POST data:

    >>> nested_form_data({'lines': inline_formset([
    ...     {'text': 'Hello'},
    ...     {'text': 'World'},
    ... ])})
    {
        'lines-TOTAL_FORMS': '2',
        'lines-INITIAL_FORMS': '0',
        'lines-MIN_NUM_FORMS': '0',
        'lines-MAX_NUM_FORMS': '1000',
        'lines-0-text': 'Hello',
        'lines-0-ORDER': '0',
        'lines-0-DELETE': '',
        'lines-1-text': 'World',
        'lines-1-ORDER': '1',
        'lines-1-DELETE': '',
    }
    """
    def to_form(index, item):
        defaults = {
            'ORDER': str(index),
            'DELETE': '',
        }
        defaults.update(item)
        return defaults

    data_dict = {str(index): to_form(index, item)
                 for index, item in enumerate(items)}

    data_dict.update({
        'TOTAL_FORMS': str(len(data_dict)),
        'INITIAL_FORMS': str(initial),
        'MIN_NUM_FORMS': str(min),
        'MAX_NUM_FORMS': str(max),
    })
    return data_dict


class CoopAssertionMixin():
    def assertNoMissingMigrations(self):
        try:
            out = StringIO()
            call_command(
                *'makemigrations --check --dry-run --no-color --name=missing_migration'.split(),
                stdout=out)
        except SystemExit:
            out.seek(0)
            self.fail(msg='Missing migrations:\n\n' + out.read())

    def assertTestdataWorks(self):
        """
        Run the ``testdata`` management command. The tests pass if no errors
        are thrown
        """
        def mocked_download_image(image_url, image_path):
            """
            Don't actually go and download the image from lorem pixel, as that
            is quite slow, but still make an image file in the correct place.
            """
            test_image = get_test_image_file(image_path)
            with open(image_path, 'wb') as f:
                test_image.file.seek(0)
                f.write(test_image.file.read())

        with mock.patch.object(testdata, 'download_image_file', mocked_download_image):
            call_command('testdata', stdout=StringIO())
            call_command('update_index', stdout=StringIO())

    def assertStandardFilesExist(self):
        for standard_file in ['/favicon.ico', '/robots.txt', '/humans.txt']:
            response = self.client.get(standard_file, follow=True)
            final_url = response.redirect_chain[-1][0]
            path = urlsplit(final_url).path
            self.assertTrue(path.startswith(settings.STATIC_URL))
            tail = path[len(settings.STATIC_URL):]
            self.assertTrue(finders.find(tail), msg='{} exists'.format(path))

    def assert404PageRenders(self):
        url = '/quite/likely/not/a/page/'
        response = self.client.get(url)
        self.assertContains(response, url, status_code=404)

    def assert500PageRenders(self):
        response = self.client.get('/500/')
        self.assertEqual(response.status_code, 500)


class TestThingsWithContentMixin(CoopAssertionMixin):
    """
    Run all the standard coop assertions that require all the site content in
    the database.
    """
    def test_error_pages(self):
        """Test that the 404 and 500 pages render without error"""
        # 404 pages need database content to render site menus and stuff.
        self.assert404PageRenders()
        self.assert500PageRenders()

    def test_standard_files_exist(self):
        """Test that some standard files exist"""
        # This test will find the correct URL for the asset by following
        # redirects, which will also cause the 404 page to be rendered, so this
        # needs page content.
        self.assertStandardFilesExist()


class TestThingsWithoutContentMixin(CoopAssertionMixin):
    """
    Run all the standard coop assertions that do not require all the site
    content in the database.
    """
    def test_migrations(self):
        self.assertNoMissingMigrations()

    def test_testdata(self):
        self.assertTestdataWorks()
