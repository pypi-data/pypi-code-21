import re
from decimal import Decimal
from typing import List

from attrim.models import Class
from django.http import QueryDict
from rest_framework.request import Request
from shuup.core.models import AttributeType as ShuupAttributeType, Attribute as ShuupAttribute

from scatl.services.query_data.query_data import QueryData, AttrimClsData, ShuupAttrData, Sorting, \
    AttrimOptionData, PriceRange


class params:
    """
    Set of constants for serialization/deserialization of QueryData params.
    """
    class attrim:
        key = 'attrim'

    class shuup:
        key = 'shuup'
        
        class bool:
            true = 'true'
            false = 'false'

    class price:
        key = 'price'
    
    class category:
        key = 'category'
    
    class sorting:
        key = 'sort'
        by_name_AZ = 'name'
        by_name_ZA = '-name'
        by_price_min_max = 'price'
        by_price_max_min = '-price'


class QueryDataSerializer:
    class keys:
        attrim = 'attrim_cls_list'
        shuup = 'shuup_attr_list'
        price_range = 'price_range'
        category = 'category_slug'
        
        sorting = 'sorting'
        
        page_current = 'page'
        page_last = 'page_last'
        
    def __init__(self, query_data: QueryData):
        self._query_data = query_data

    def serialize(self) -> dict:
        data = {
            self.keys.category: self._query_data.category_slug,
            self.keys.attrim: self._serialize_attrim_cls_data_list(),
            self.keys.shuup: self._serialize_shuup_attr_data_list(),
            self.keys.price_range: self._serialize_price_range(),

            self.keys.sorting: self._serialize_sorting(),
            
            self.keys.page_current: self._query_data.page_current,
            self.keys.page_last: self._query_data.page_last,
        }
        return data

    def _serialize_attrim_cls_data_list(self) -> List[dict]:
        cls_list = []
        for cls_data in self._query_data.attrim_cls_data_list:
            cls_serialized = self._serialize_attrim_cls_data(cls_data)
            cls_list.append(cls_serialized)
        return cls_list

    def _serialize_attrim_cls_data(self, cls_data: AttrimClsData) -> dict:
        options_serialized = []
        for option_data in cls_data.option_data_list:
            option_value = option_data.model.get_value()
            option_value_serialized = str(option_value)
            option_dict = {
                'value': option_value_serialized,
                'is_selected': option_data.is_selected,
            }
            options_serialized.append(option_dict)
        # noinspection PyUnresolvedReferences
        cls_dict = {
            'code': cls_data.model.code,
            'name': cls_data.model.name,
            'options': options_serialized,
        }
        return cls_dict

    def _serialize_shuup_attr_data_list(self) -> List[dict]:
        attr_list_serialized = []
        for attr_data in self._query_data.shuup_attr_data_list:
            attr_serialized = self._serialize_shuup_attr_data(attr_data)
            attr_list_serialized.append(attr_serialized)
        return attr_list_serialized

    def _serialize_shuup_attr_data(self, attr_data: ShuupAttrData) -> dict:
        attr_serialized = {
            'identifier': attr_data.identifier,
            'type': attr_data.type.value,
        }
        if attr_data.type == ShuupAttributeType.BOOLEAN:
            attr_serialized['value'] = attr_data.value

        return attr_serialized

    def _serialize_sorting(self) -> str:
        sorting = self._query_data.sorting
        if sorting is Sorting.name_AZ:
            return params.sorting.by_name_AZ
        if sorting is Sorting.name_ZA:
            return params.sorting.by_name_ZA
        if sorting is Sorting.prize_min_max:
            return params.sorting.by_price_min_max
        if sorting is Sorting.prize_max_min:
            return params.sorting.by_price_max_min

    def _serialize_price_range(self) -> dict:
        return {
            'min': int(self._query_data.price_range.min),
            'max': int(self._query_data.price_range.max),
        }


class QueryDataDeserializer:
    def __init__(self, request: Request):
        self._request = request
        self._query_params = request.GET # type: QueryDict

    def deserialize(self) -> QueryData:
        query_data = QueryData(
            category_slug=self._deserialize_category_slug(),
            attrim_cls_data_list=self._deserialize_attrim_cls_data_list(),
            shuup_attr_data_list=self._deserialize_shuup_attr_data_list(),
            sorting=self._deserialize_sorting(),
            price_range=self._deserialize_price_range(),
            page_current=self._deserialize_page_current(),
            shop=self._request.shop,
            user_contact=self._request.customer,
        )
        return query_data

    def _deserialize_category_slug(self) -> str:
        for param_name_raw, param_value_raw in self._query_params.items():
            try:
                param_name, param_name_attr = self._parse_param_name(param_name_raw)
            except NotFoundError:
                continue
            if param_name != params.category.key:
                continue
            
            field_values = param_value_raw.split(',')
            category_slug = field_values[0]
            return category_slug

    def _deserialize_attrim_cls_data_list(self) -> List[AttrimClsData]:
        cls_data_list = [] # type: List[AttrimClsData]
        
        for param_name_raw, param_value_raw in self._query_params.items():
            try:
                param_name, param_name_attr = self._parse_param_name(param_name_raw)
            except NotFoundError:
                continue
            if param_name != params.attrim.key:
                continue
            
            cls_model = Class.objects.get(code=param_name_attr)
            cls_data = AttrimClsData(model=cls_model)
            options_selected_values = param_value_raw.split(',')
            for option_selected_value in options_selected_values:
                option_data = AttrimOptionData(
                    model=cls_model.options.get(value=option_selected_value),
                    is_selected=True,
                )
                cls_data.option_data_list.append(option_data)
            cls_data_list.append(cls_data)
    
        return cls_data_list

    def _deserialize_shuup_attr_data_list(self) -> List[ShuupAttrData]:
        attr_data_list = [] # type: List[ShuupAttrData]
        for param_name_raw, param_value_raw in self._query_params.items():
            try:
                param_name, param_name_attr = self._parse_param_name(param_name_raw)
            except NotFoundError:
                continue
            if param_name != params.shuup.key:
                continue
            
            attr_data = self._deserialize_shuup_attr_data(
                identifier=param_name_attr, value_raw=param_value_raw,
            )
            attr_data_list.append(attr_data)
        return attr_data_list

    def _deserialize_shuup_attr_data(self, identifier: str, value_raw: str) -> ShuupAttrData:
        attr = ShuupAttribute.objects.get(identifier=identifier)
        
        attr_data = ShuupAttrData(identifier=attr.identifier, type=attr.type)
        
        if attr.type == ShuupAttributeType.BOOLEAN:
            if value_raw == params.shuup.bool.true:
                attr_data.value = True
            elif value_raw == params.shuup.bool.false:
                attr_data.value = False
            # TODO error handling
        
        return attr_data

    def _deserialize_sorting(self) -> Sorting:
        for param_name_raw, param_value_raw in self._query_params.items():
            is_sorting_param = param_name_raw == params.sorting.key
            if is_sorting_param:
                if param_value_raw == params.sorting.by_name_AZ:
                    return Sorting.name_AZ
                elif param_value_raw == params.sorting.by_name_ZA:
                    return Sorting.name_ZA
                elif param_value_raw == params.sorting.by_price_min_max:
                    return Sorting.prize_min_max
                elif param_value_raw == params.sorting.by_price_max_min:
                    return Sorting.prize_max_min
                else:
                    return Sorting.name_AZ

    def _deserialize_price_range(self) -> PriceRange:
        for name_raw, value_raw in self._query_params.items():
            try:
                param_name, param_name_attr = self._parse_param_name(name_raw)
            except NotFoundError:
                continue
            is_price_range_param = param_name == params.price.key
            if is_price_range_param:
                price_range_raw = value_raw.split(',')
                price_min = Decimal(price_range_raw[0])
                price_max = Decimal(price_range_raw[1])
                return PriceRange(min=price_min, max=price_max)

    def _parse_param_name(self, name: str) -> (str, str):
        match = re.match(
            r'^filter\[(?P<param_name>\w+).?(?P<param_name_attr>\w+)?]',
            string=name,
        )
        if not match:
            raise NotFoundError
        param_name, param_name_attr = match.group(1, 2)
        return (param_name, param_name_attr)

    def _deserialize_page_current(self) -> int:
        page_current_str = self._query_params.get('page', default=1)
        return int(page_current_str)


class NotFoundError(Exception):
    pass
