from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from shuup.core.models import Product

from scatl.api.pagination import ScatlPageNumberPagination
from scatl.api.serializers.product import ProductSerializer
from scatl.services.filters import filter_product_qs_by_query_params


class ScatlFrontProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = ScatlPageNumberPagination
    
    def get_queryset(self) -> QuerySet:
        queryset_default = Product.objects.listed(
            customer=self.request.customer,
            shop=self.request.shop
        ).filter(
            shop_products__shop=self.request.shop,
            variation_parent__isnull=True
        )
        queryset_filtered = filter_product_qs_by_query_params(
            queryset=queryset_default,
            request=self.request,
        )
        return queryset_filtered
