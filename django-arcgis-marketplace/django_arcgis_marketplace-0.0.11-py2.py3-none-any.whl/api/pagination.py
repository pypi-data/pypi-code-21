from rest_framework import exceptions
from rest_framework import pagination
from rest_framework.settings import api_settings


__all__ = ['ArcgisOffsetPagination']


def _page_number_offset(request, paginator):
    page_number = request.query_params.get(paginator.page_query_param, 1)

    try:
        page_number = int(page_number)
    except (TypeError, ValueError):
        page_number = 1

    return (page_number - 1) * paginator.page_size


def _page_cursor_offset(request, paginator):
    try:
        cursor = paginator.decode_cursor(request)
    except exceptions.NotFound:
        cursor = None

    if cursor is not None:
        return cursor[0]
    return 0


class ArcgisOffsetPagination(api_settings.DEFAULT_PAGINATION_CLASS):
    page_size = api_settings.PAGE_SIZE

    def get_page_size(self, request):
        if isinstance(self, pagination.LimitOffsetPagination):
            return self.get_limit(request)
        return super().get_page_size(request)

    def get_offset(self, request):
        if isinstance(self, pagination.PageNumberPagination):
            return _page_number_offset(request, self)

        elif isinstance(self, pagination.LimitOffsetPagination):
            return super().get_offset(request)

        elif isinstance(self, pagination.CursorPagination):
            return _page_cursor_offset(request, self)
        return 0
