import arcgis_sdk

from .exceptions import ArcgisException
from .pagination import ArcgisOffsetPagination


class ArcgisAPIMixin(object):

    @property
    def account(self):
        return self.request.user.account

    def handle_exception(self, exc):
        if isinstance(exc, arcgis_sdk.ArcgisAPIError):
            exc = ArcgisException(
                detail=dict(
                    info=getattr(exc, 'details', None),
                    message=exc.message
                ),
                status_code=exc.code
            )
        return super().handle_exception(exc)


class ArcgisPaginationMixin(object):
    pagination_class = ArcgisOffsetPagination

    def get_paginated_response(self, data, request):
        self.paginator.paginate_queryset(range(data['total']), request)

        results = next((
            value for key, value in data.items()
            if isinstance(value, list)), []
        )

        return self.paginator.get_paginated_response(results)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
        return self._paginator
