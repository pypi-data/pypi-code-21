from typing import Any, List

from attrim.models import Class, Option
from django.core.paginator import Paginator
from shuup.core.models import Product

from scatl.models import Config
from scatl.services.filters import ProductQuerySetFilter
from scatl.services.query_data.query_data import QueryData, AttrimOptionData, AttrimClsData


def complement_query_data_from_db(query_data: QueryData):
    _complement_absent_attrim_options(query_data)
    _complement_absent_attrim_cls_data(query_data)
    _complement_page_last(query_data)
    _sort_attrim_cls_data_list_by_name(query_data)
    _sort_attrim_options_by_order(query_data)


def _complement_absent_attrim_options(query_data: QueryData):
    for cls_data in query_data.attrim_cls_data_list:
        # noinspection PyUnresolvedReferences
        for option_model in cls_data.model.options.all():
            option_models_present = [ # type: List[Option]
                option_data.model for option_data in cls_data.option_data_list
            ]
            if option_model not in option_models_present:
                option_data = AttrimOptionData(
                    model=option_model,
                    is_selected=False,
                )
                cls_data.option_data_list.append(option_data)


def _complement_absent_attrim_cls_data(query_data: QueryData):
    cls_present_codes = _get_present_attrim_cls_codes(query_data) # type: List[str]
    cls_absent_qs = Class.objects.exclude(code__in=cls_present_codes)
    for cls_model in cls_absent_qs:
        options_data_list = []
        for option_model in cls_model.options.all():
            option_data = AttrimOptionData(
                model=option_model,
                is_selected=False,
            )
            options_data_list.append(option_data)
        cls = AttrimClsData(
            model=cls_model,
            options=options_data_list,
        )
        query_data.attrim_cls_data_list.append(cls)


def _sort_attrim_cls_data_list_by_name(query_data: QueryData):
    query_data.attrim_cls_data_list.sort(key=lambda cls_data: cls_data.model.name)


def _sort_attrim_options_by_order(query_data: QueryData):
    def options_sorting_key(option_data: AttrimOptionData) -> Any:
        if option_data.model.order is None:
            infinity = float('inf')
            return infinity
        else:
            return option_data.model.order

    for cls_data in query_data.attrim_cls_data_list:
        cls_data.option_data_list.sort(key=options_sorting_key)


def _get_present_attrim_cls_codes(query_data: QueryData) -> List[str]:
    cls_codes_present = []
    for cls_data in query_data.attrim_cls_data_list:
        cls_codes_present.append(cls_data.model.code)
    return cls_codes_present


def _complement_page_last(query_data: QueryData):
    # noinspection PyUnresolvedReferences
    product_qs = Product.objects.listed(
        customer=query_data.user_contact,
        shop=query_data.shop,
    ).filter(
        shop_products__shop=query_data.shop,
        variation_parent__isnull=True
    )
    
    product_qs_filter = ProductQuerySetFilter(
        product_qs=product_qs,
        query_data=query_data,
    )
    product_qs_filtered = product_qs_filter.filter()
    
    page_size = Config.get_solo().page_size
    django_paginator = Paginator(object_list=product_qs_filtered, per_page=page_size)
    page_last = django_paginator.num_pages
    query_data.page_last = page_last
