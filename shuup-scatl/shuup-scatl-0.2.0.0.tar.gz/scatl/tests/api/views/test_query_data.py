import json

from attrim.models import Class
from attrim.models.type import Type
from django.core.urlresolvers import reverse
from shuup.core.models import Attribute as ShuupAttribute, \
    AttributeType as ShuupAttributeType

from scatl.api.api_populator import QUERY_DATA_DETAIL
from scatl.api.serializers.query_data import QueryDataSerializer, params
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class QueryDataApiTest(FiltersTestCase):
    json_keys = QueryDataSerializer.keys
    
    def test_attrim_cls_list_sorting(self):
        cls_list = [
            self.gen.attrim.cls(name='alpha'),
            self.gen.attrim.cls(name='beta'),
            self.gen.attrim.cls(name='gamma'),
        ]

        response_raw = self.client.get(reverse(QUERY_DATA_DETAIL))
        response = json.loads(response_raw.content.decode())

        name_list_actual = []
        for cls_json in response[self.json_keys.attrim]:
            name_list_actual.append(cls_json['name'])
        name_list_expected = [cls_list[0].name, cls_list[1].name, cls_list[2].name]
        self.assert_equal(name_list_expected, name_list_actual)

    # TODO not stable? yup
    def test_attrim_cls_list_trans_str_with_select(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, options_amount=3)

        query_data = self._request_query_data(
            query_params=self._build_attrim_query_param(
                code=cls.code, options=[cls.options.all()[2]],
            )
        )
        cls_dict_actual = self._get_attrim_cls_dict_from_query_data(query_data, cls)
        cls_dict_expected = {
            'code': cls.code,
            'name': cls.name,
            'options': [
                {'value': cls.options.all()[0].get_value(), 'is_selected': False},
                {'value': cls.options.all()[1].get_value(), 'is_selected': False},
                {'value': cls.options.all()[2].get_value(), 'is_selected': True},
            ],
        }
        self.assert_equal(cls_dict_expected, cls_dict_actual)

    def test_attrim_cls_list_trans_str(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, options_amount=3)

        response = self.client.get(reverse(QUERY_DATA_DETAIL))
        query_data = json.loads(response.content.decode())

        cls_dict_actual = self._get_attrim_cls_dict_from_query_data(query_data, cls)
        cls_dict_expected = {
            'code': cls.code,
            'name': cls.name,
            'options': [
                {'value': cls.options.all()[0].get_value(), 'is_selected': False},
                {'value': cls.options.all()[1].get_value(), 'is_selected': False},
                {'value': cls.options.all()[2].get_value(), 'is_selected': False},
            ],
        }
        self.assert_equal(cls_dict_expected, cls_dict_actual)

    def test_attrim_cls_list_int(self):
        cls = self.gen.attrim.cls(type=Type.INT, options_amount=3)
        
        response = self.client.get(
            path=reverse(QUERY_DATA_DETAIL),
            data=self._build_attrim_query_param(
                code=cls.code,
                options=[cls.options.all()[0], cls.options.all()[1]],
            )
        )
        query_data = json.loads(response.content.decode())

        cls_expected = {
            'code': cls.code,
            'name': cls.name,
            'options': [
                {'value': str(cls.options.all()[0].get_value()), 'is_selected': True},
                {'value': str(cls.options.all()[1].get_value()), 'is_selected': True},
                {'value': str(cls.options.all()[2].get_value()), 'is_selected': False},
            ],
        }
        cls_actual = self._get_attrim_cls_dict_from_query_data(query_data, cls)
        self.assert_equal(cls_expected, cls_actual)

    def test_shuup_attr_list_bool(self):
        self._test_shuup_attr_list_bool(query_param_value='true')
        self._test_shuup_attr_list_bool(query_param_value='false')

    def test_category(self):
        categories = []
        for _ in range(0, 3):
            category = self.gen.category()
            categories.append(category)

        response = self.client.get(
            path=reverse(QUERY_DATA_DETAIL),
            data=self._build_category_query_param(slug=categories[0].slug)
        )
        query_data = json.loads(response.content.decode())

        category = query_data[self.json_keys.category]
        self.assert_equal(category, categories[0].slug)

    def test_sorting_by_name_AZ(self):
        self.client.get(
            path=reverse(QUERY_DATA_DETAIL),
            data={params.sorting.key: params.sorting.by_name_AZ},
        )

    def test_pagination_data(self):
        self.gen.products(amount=25)
        query_data = self._request_query_data(query_params={'page': 2})
        self.assert_equal(3, query_data['page_last'])
        self.assert_equal(2, query_data['page'])

    def _get_attrim_cls_dict_from_query_data(self, query_data: dict, cls: Class) -> dict:
        for cls_json in query_data[self.json_keys.attrim]:
            if cls_json['code'] == cls.code:
                return cls_json
    
    def _test_shuup_attr_list_bool(self, query_param_value: str):
        attr_identifier = 'bool_attr'
        try:
            attr = ShuupAttribute.objects.get(identifier=attr_identifier)
        except ShuupAttribute.DoesNotExist:
            attr = ShuupAttribute.objects.create(
                identifier=attr_identifier,
                type=ShuupAttributeType.BOOLEAN,
                name='test name',
            )

        response = self.client.get(
            path=reverse(QUERY_DATA_DETAIL),
            data=self._build_shuup_query_param(
                ident=attr.identifier, value=query_param_value,
            )
        )
        query_data = json.loads(response.content.decode())

        attr_expected = {
            'identifier': attr.identifier,
            'type': attr.type.value,
            # TODO use the string constants
            'value': True if query_param_value == 'true' else False,
        }
        attr_actual = self._get_shuup_attr_dict_from_query_data(query_data, attr)
        self.assert_equal(attr_expected, attr_actual)

    def _get_shuup_attr_dict_from_query_data(
        self, query_data: dict, attr: ShuupAttribute,
    ) -> dict:
        for attr_json in query_data['shuup_attr_list']:
            if attr_json['identifier'] == attr.identifier:
                return attr_json
