from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from scatl.models import Config


class ScatlPageNumberPagination(PageNumberPagination):
    def get_page_size(self, request: Request) -> int:
        config = Config.get_solo() # type: Config
        return config.page_size

    def get_paginated_response(self, data: dict) -> Response:
        """
        Add the `last` attr to the response.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('previous', self.get_previous_link()),
            ('next', self.get_next_link()),
            ('last', self.page.paginator.num_pages),
            ('results', data),
        ]))
