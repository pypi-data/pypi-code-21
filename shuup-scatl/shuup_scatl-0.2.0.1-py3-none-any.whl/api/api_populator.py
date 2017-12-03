from rest_framework.routers import DefaultRouter

from scatl.api.views.query_data import QueryDataViewSet
from scatl.api.views.product import ScatlFrontProductViewSet


PRODUCT_BASE_NAME = 'scatl-front-product'
PRODUCT_LIST = '{}-list'.format(PRODUCT_BASE_NAME)
PRODUCT_DETAIL = '{}-detail'.format(PRODUCT_BASE_NAME)

QUERY_DATA_BASE_NAME = 'scatl-query-data'
# the `list` in the name, because that's what DefaultRouter will do,
# and shuup requires DefaultRouter
QUERY_DATA_DETAIL = '{}-list'.format(QUERY_DATA_BASE_NAME)


def populate(router: DefaultRouter):
    router.register(
        prefix='scatl/front/query-data',
        viewset=QueryDataViewSet,
        base_name=QUERY_DATA_BASE_NAME,
    )
    router.register(
        prefix='scatl/front/products',
        viewset=ScatlFrontProductViewSet,
        base_name=PRODUCT_BASE_NAME,
    )
