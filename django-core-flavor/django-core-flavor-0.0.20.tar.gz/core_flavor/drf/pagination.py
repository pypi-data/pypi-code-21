from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class CursorPageNumberPagination(pagination.PageNumberPagination):
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict({
            'paging': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count
            },
            'cursor': {
                'after': self.page.next_page_number()
                if self.page.has_next() else None,
                'before': self.page.previous_page_number()
                if self.page.has_previous() else None
            },
            'results': data
        }))
