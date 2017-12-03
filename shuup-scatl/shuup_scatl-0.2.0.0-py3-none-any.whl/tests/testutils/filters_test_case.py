import json
from typing import List

from attrim.models import Option
from attrim.testutils.generators import ModelsGen
from django.core.urlresolvers import reverse
from django.http import HttpRequest, QueryDict
from django.test import RequestFactory
from shuup.core.models import Product
from shuup.front.middleware import ShuupFrontMiddleware
from shuup_testutils.cases import ApiAuthAdminTestCase
from shuup_utils.lang_constants import DEFAULT_LANG

from scatl.api.api_populator import PRODUCT_LIST, QUERY_DATA_DETAIL
from scatl.api.serializers.query_data import params

QueryParamName = str
QueryParamValue = str


class FiltersTestCase(ApiAuthAdminTestCase):
    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.gen = ModelsGen()

    def _assert_contains_product(
        self,
        product_json_list: List[dict],
        product: Product,
    ):
        is_contains = self._is_contains_product(product_json_list, product)
        self.assert_true(is_contains, 'the list should contain the product')

    def _assert_not_contains_product(
        self,
        product_json_list: List[dict],
        product: Product,
    ):
        is_contains = self._is_contains_product(product_json_list, product)
        self.assert_false(is_contains, 'the list should not contain the product')

    def _is_contains_product(
        self,
        product_json_list: List[dict],
        product_to_find: Product,
    ) -> bool:
        is_list_contains_product = False
        for product_json in product_json_list:
            product_id = int(product_json['id'])
            product_translations = product_json['translations']
            product_name = product_translations[DEFAULT_LANG]['name']
            is_id_matches = product_id == product_to_find.id
            is_name_matches = product_name == product_to_find.name
            if is_id_matches and is_name_matches:
                is_list_contains_product = True
        return is_list_contains_product

    def _request_product_list(self, query_params: dict = None) -> List[dict]:
        response_raw = self.client.get(
            path=reverse(PRODUCT_LIST),
            data=query_params,
            follow=True,
        )
        response_content = response_raw.content.decode()
        product_list_dict = json.loads(response_content)['results']
        return product_list_dict

    
    def _request_query_data(self, query_params: dict = None) -> dict:
        response = self.client.get(
            path=reverse(QUERY_DATA_DETAIL),
            data=query_params,
        )
        query_data_dict = json.loads(response.content.decode())
        return query_data_dict

    def _build_query_params(
        self,
        category_slug: str = None,
        attrim_cls_code: str = None,
        attrim_options: List[Option] = None,
        price_min: int = None,
        price_max: int = None,
    ) -> QueryDict:
        query_dict = QueryDict(mutable=True)
        
        if category_slug is not None:
            category_query_dict = self._build_category_query_param(category_slug)
            query_dict.update(category_query_dict)
        if attrim_cls_code is not None:
            attrim_query_dict = self._build_attrim_query_param(
                code=attrim_cls_code,
                options=attrim_options,
            )
            query_dict.update(attrim_query_dict)
        if (price_min is not None) and (price_max is not None):
            price_query_dict = self._build_price_query_param(price_min, price_max)
            query_dict.update(price_query_dict)
        
        return query_dict

    def _build_category_query_param(self, slug: str) -> dict:
        param_name = 'filter[{}]'.format(params.category.key)
        return {param_name: slug}

    def _build_attrim_query_param(self, code: str, options: List[Option]) -> dict:
        param_name = 'filter[{}.{}]'.format(params.attrim.key, code)
        values = [] # type: List[str]
        for option in options:
            value_str = str(option.get_value())
            values.append(value_str)
        param_value = ','.join(values)
        return {param_name: param_value}

    def _build_shuup_query_param(self, ident: str, value: str) -> dict:
        param_name = 'filter[{}.{}]'.format(params.shuup.key, ident)
        return {param_name: value}

    # noinspection PyShadowingBuiltins
    def _build_price_query_param(self, min: int, max: int) -> dict:
        param_name = 'filter[{}]'.format(params.price.key)
        return {param_name: '{},{}'.format(min, max)}

    def _create_shuup_request(self) -> HttpRequest:
        request_factory = RequestFactory()
        request = request_factory.get(path=reverse(PRODUCT_LIST))
        ShuupFrontMiddleware().process_request(request)
        return request
