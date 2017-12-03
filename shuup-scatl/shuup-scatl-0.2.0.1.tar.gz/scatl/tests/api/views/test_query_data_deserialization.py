from typing import List

from attrim.models import Option
from attrim.models.type import Type
from attrim.testutils.generators import ModelsGen
from django.db.models import QuerySet
from django.http import QueryDict
from faker import Faker

from scatl.api.serializers.query_data import params
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class QueryDataDeserializationTest(FiltersTestCase):
    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.gen = ModelsGen()

    def test_category_slug_deserialization(self):
        fake = Faker()
        category_slug = fake.word()
        query_params = self._build_query_params(category_slug=category_slug)
        query_data = self._request_query_data(query_params=query_params)
        self.assert_equal(category_slug, query_data['category_slug'])

    def test_attrim_deserialization(self):
        cls_source = self.gen.attrim.cls(type=Type.STR, options_amount=5)

        options_selected_source_qs = cls_source.options.all()[0:2] # type: QuerySet
        options_selected_source = [ # type: List[Option]
            option for option in options_selected_source_qs
        ]
        query_params = self._build_query_params(
            attrim_cls_code=cls_source.code,
            attrim_options=options_selected_source,
        )
        query_data = self._request_query_data(query_params=query_params)

        cls = query_data['attrim_cls_list'][0]
        self.assert_equal(cls_source.code, cls['code'])

        options_selected = [ # type: List[Option]
            option for option in query_data['attrim_cls_list'][0]['options']
        ]
        for index, option_selected_source in enumerate(options_selected_source):
            self.assert_equal(
                option_selected_source.get_value(),
                options_selected[index]['value']
            )

    def test_price_deserialization(self):
        price_min = 500
        price_max = 10000
        query_params = self._build_query_params(price_min=price_min, price_max=price_max)
        query_data = self._request_query_data(query_params=query_params)

        self.assert_equal(price_min, query_data['price_range']['min'])
        self.assert_equal(price_max, query_data['price_range']['max'])

    def test_sorting_deserialization(self):
        query_params = QueryDict(mutable=True)
        query_params.update({params.sorting.key: params.sorting.by_price_min_max})
        query_data = self._request_query_data(query_params=query_params)
        self.assert_equal(params.sorting.by_price_min_max, query_data['sorting'])
