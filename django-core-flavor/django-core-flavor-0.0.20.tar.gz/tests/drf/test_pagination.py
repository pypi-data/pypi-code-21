import math
import random

from rest_framework.settings import api_settings

from core_flavor.drf import pagination
from core_flavor.drf.test import APITestCase


class PaginationTests(APITestCase):

    def test_pagination_cursor_page_number(self):
        paginator = pagination.CursorPageNumberPagination()
        items = range(random.randint(api_settings.PAGE_SIZE + 1, 100))
        num_pages = len(items) / api_settings.PAGE_SIZE
        page = random.randint(1, math.ceil(num_pages))
        request = self.factory.get('/', {})

        request.query_params = {'page': page}
        paginator.paginate_queryset(items, request)
        response = paginator.get_paginated_response(items)

        self.assertEqual(response.data['paging']['count'], len(items))

        self.assertEqual(response.data['cursor']['before'], (
            page - 1 if (page - 1) > 0 else None
        ))

        self.assertEqual(response.data['cursor']['after'], (
            page + 1 if num_pages > page else None
        ))
