from typing import List

from attrim.filters import filter_product_qs_by
from django.db.models import Q
from django.db.models import QuerySet
from rest_framework.request import Request
from shuup.core.models import Product, AttributeType as ShuupAttributeType

from scatl.services.query_data.query_data import QueryData, OptionValueRaw, AttrimClsData, Sorting


def filter_product_qs_by_query_params(queryset: QuerySet, request: Request) -> QuerySet:
    from scatl.api.serializers.query_data import QueryDataDeserializer
    query_data = QueryDataDeserializer(request).deserialize()
    product_qs_filter = ProductQuerySetFilter(
        product_qs=queryset,
        query_data=query_data,
    )
    product_qs_filtered = product_qs_filter.filter()
    return product_qs_filtered


class ProductQuerySetFilter:
    def __init__(self, product_qs: QuerySet, query_data: QueryData):
        self._qs_filtered = product_qs
        self._query_data = query_data
    
    def filter(self) -> QuerySet:
        self._filter_by_category()
        self._filter_by_attrim_cls_data_list()
        self._filter_by_shuup_attr_data_list()
        self._filter_by_price()
        self._remove_duplicates_from_qs()
        self._sort_product_qs_filtered()
        return self._qs_filtered

    def _filter_by_category(self):
        category_slug = self._query_data.category_slug
        if category_slug is not None:
            self._qs_filtered = self._qs_filtered.filter(
                Q(shop_products__primary_category__translations__slug=category_slug) |
                Q(shop_products__categories__translations__slug=category_slug),
            )

    def _filter_by_attrim_cls_data_list(self):
        for cls_data in self._query_data.attrim_cls_data_list:
            self._qs_filtered = self._filter_by_attrim_cls(cls_data)
    
    def _filter_by_attrim_cls(self, cls_data: AttrimClsData) -> QuerySet:
        option_values_selected = cls_data.get_option_values_selected() # type: List[OptionValueRaw]
        is_should_be_filtered = len(option_values_selected) > 0
        if is_should_be_filtered:
            # noinspection PyTypeChecker
            qs_filtered = filter_product_qs_by(
                option_values_raw=option_values_selected,
                product_qs_source=self._qs_filtered,
                cls=cls_data.model,
            )
            return qs_filtered
        else:
            return self._qs_filtered

    def _filter_by_shuup_attr_data_list(self):
        for attr_data in self._query_data.shuup_attr_data_list:
            if attr_data.type == ShuupAttributeType.BOOLEAN:
                if attr_data.value is True:
                    value = 1
                else:
                    value = 0
                self._qs_filtered = self._qs_filtered.filter(
                    attributes__attribute__identifier=attr_data.identifier,
                    attributes__numeric_value=value,
                )

    def _filter_by_price(self):
        price_min = self._query_data.price_range.min
        price_max = self._query_data.price_range.max
        self._qs_filtered = self._qs_filtered.filter(
            shop_products__default_price_value__range=[price_min, price_max],
        )

    def _remove_duplicates_from_qs(self):
        """
        For a reason (can't really remember) there are duplicates in the result
        queryset. PostgreSQL `distinct` messes up with the sorting, so the only
        way to eliminate the duplicates it is to create a new queryset.
        
        About the `distinct` and `order_by` see:
        docs.djangoproject.com/en/1.9/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        """
        product_pk_list = []
        for product in self._qs_filtered:
            product_pk_list.append(product.pk)
        qs_without_duplicates = Product.objects.filter(pk__in=product_pk_list)
        self._qs_filtered = qs_without_duplicates

    def _sort_product_qs_filtered(self):
        if self._query_data.sorting is Sorting.name_ZA:
            order_by = '-translations__name'
        elif self._query_data.sorting is Sorting.prize_min_max:
            order_by = 'shop_products__default_price_value'
        elif self._query_data.sorting is Sorting.prize_max_min:
            order_by = '-shop_products__default_price_value'
        else:
            order_by = 'translations__name'
        self._qs_filtered = self._qs_filtered.order_by(order_by)
