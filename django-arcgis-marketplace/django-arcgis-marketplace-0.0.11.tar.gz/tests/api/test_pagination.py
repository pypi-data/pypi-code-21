import importlib
import random
import urllib.parse

from django.test.utils import override_settings

from rest_framework import pagination as api_pagination
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from core_flavor.drf.test import APITestCase
from arcgis_marketplace.api import pagination as arcgis_pagination


class override_pagination(override_settings):

    def enable(self):
        super().enable()
        importlib.reload(arcgis_pagination)


class RequestFactory(APIRequestFactory):

    def get(self, path, data=None, **extra):
        request = super().get(path, data=None, **extra)
        request.query_params = data
        return request


class PaginationTests(APITestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def settings_pagination(self, pagination_class, **kwargs):
        kwargs.setdefault('REST_FRAMEWORK', {
            'PAGE_SIZE': api_settings.PAGE_SIZE,
            'DEFAULT_PAGINATION_CLASS':
            "rest_framework.pagination.{}".format(pagination_class)
        })

        return override_pagination(**kwargs)

    def test_pagination_number_wrong_page(self):
        request = self.factory.get('/', {'page': 'wrong'})

        with(self.settings_pagination('PageNumberPagination')):
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            self.assertEqual(paginator.get_offset(request), 0)

    def test_pagination_number_page_size(self):
        page_size = random.randint(10, 100)
        request = self.factory.get('/', {'page_size': page_size})

        with(self.settings_pagination('PageNumberPagination')):
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            paginator.page_size_query_param = 'page_size'
            self.assertEqual(paginator.get_page_size(request), page_size)

    def test_pagination_limit_offset(self):
        offset = random.randint(1, 10)
        request = self.factory.get('/', {'offset': offset})

        with(self.settings_pagination('LimitOffsetPagination')):
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            self.assertEqual(paginator.get_offset(request), offset)

    def test_pagination_limit_page_size(self):
        limit = random.randint(10, 100)
        request = self.factory.get('/', {'limit': limit})

        with(self.settings_pagination('LimitOffsetPagination')):
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            self.assertEqual(paginator.get_page_size(request), limit)

    def test_pagination_cursor(self):
        with(self.settings_pagination('CursorPagination')):
            offset = random.randint(1, 10)
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            cursor = api_pagination.Cursor(
                offset=offset,
                reverse=False,
                position=0
            )

            paginator.base_url = ''
            request = self.factory.get('', dict(
                urllib.parse.parse_qsl(
                    paginator.encode_cursor(cursor)[1:]
                )
            ))

            self.assertEqual(paginator.get_offset(request), offset)

    def test_pagination_cursor_wrong(self):
        request = self.factory.get('/', {'cursor': 'wrong'})

        with(self.settings_pagination('CursorPagination')):
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            self.assertEqual(paginator.get_offset(request), 0)

    def test_pagination_unknown(self):
        request = self.factory.get('/')

        with(self.settings_pagination('BasePagination')):
            paginator = arcgis_pagination.ArcgisOffsetPagination()
            self.assertEqual(paginator.get_offset(request), 0)
