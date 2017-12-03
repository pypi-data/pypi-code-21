from decimal import Decimal
from enum import Enum
from typing import List, Union, Type

from attrim.models import Class, Option
from shuup.core.models import AttributeType, Shop, Contact

from scatl.services.product.price import get_product_price_min, \
    get_product_price_max


OptionValueRaw = str

ShuupAttrValue = Union[bool, None]


# TODO uppercase?
class Sorting(Enum):
    name_AZ = 0
    name_ZA = 1
    prize_min_max = 2
    prize_max_min = 3


class AttrimOptionData:
    def __init__(self, model: Option, is_selected: bool):
        self.model = model
        self.is_selected = is_selected


class AttrimClsData:
    def __init__(self, model: Class, options: List[AttrimOptionData] = None):
        self.model = model # type: Class
        self.option_data_list = options or [] # type: List[AttrimOptionData]

    def get_option_values_selected(self) -> List[OptionValueRaw]:
        option_values_selected = []
        for option_data in self.option_data_list:
            if option_data.is_selected:
                # noinspection PyArgumentList
                option_values_selected.append(option_data.model.get_value())
        return option_values_selected


class ShuupAttrData:
    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        identifier: str,
        type: AttributeType,
        value: ShuupAttrValue = None,
    ):
        self.identifier = identifier
        self.type = type
        self.value = value


class PriceRange:
    # noinspection PyShadowingBuiltins
    def __init__(self, min: Union[int, Decimal], max: Union[int, Decimal]):
        self.min = min
        self.max = max


class QueryData:
    def __init__(
        self,
        shop: Shop,
        user_contact: Type[Contact],
        category_slug: str = None,
        attrim_cls_data_list: List[AttrimClsData] = None,
        shuup_attr_data_list: List[ShuupAttrData] = None,
        sorting: Sorting = Sorting.name_AZ,
        price_range: PriceRange = None,
        page_current: int = 1,
        page_last: int = 1,
    ):
        self.category_slug = category_slug
        self.attrim_cls_data_list = attrim_cls_data_list or [] # type: List[AttrimClsData]
        self.shuup_attr_data_list = shuup_attr_data_list or [] # type: List[ShuupAttrData]
        self.sorting = sorting
        self.price_range = price_range or PriceRange(
            min=get_product_price_min(),
            max=get_product_price_max(),
        )
        self.page_current = page_current
        self.page_last = page_last
        self.shop = shop
        self.user_contact = user_contact
