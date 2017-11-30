from shuup.api.urls import AutoRouter

from attrim.restapi.views import OptionViewSet, ProductTypeViewSet
from attrim.restapi.views import ClassViewSet


def populate_api(router: AutoRouter):
    router.register(
        prefix='attrim/product-types',
        viewset=ProductTypeViewSet,
        base_name='product-type',
    )
    router.register(
        prefix='attrim/options',
        viewset=OptionViewSet,
        base_name='option',
    )
    router.register(
        prefix='attrim/classes',
        viewset=ClassViewSet,
        base_name='class',
    )
