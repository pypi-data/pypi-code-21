import decimal
from typing import List

from django.db.models import QuerySet

from attrim.models import Class
from attrim.trans_str import OptionValue
from attrim.models.type import Type


OptionValueRaw = str


def filter_product_qs_by(
    option_values_raw: List[OptionValueRaw],
    product_qs_source: QuerySet,
    cls: Class,
) -> QuerySet:
    option_values = _parse_option_values(cls, option_values_raw)  # type: List[OptionValue]

    if cls.type == Type.INT or cls.type == Type.DECIMAL:
        product_qs_filtered = product_qs_source.filter(
            attrim_attr__cls=cls,
            attrim_attr__option___value_decimal__in=option_values,
        )
    elif cls.type == Type.STR:
        product_qs_filtered = product_qs_source.filter(
            attrim_attr__cls=cls,
            attrim_attr__option___value_str__in=option_values,
        )
    elif cls.type == Type.TRANS_STR:
        product_qs_filtered = product_qs_source.filter(
            attrim_attr__cls=cls,
            attrim_attr__option__translations___value_trans_str__in=option_values,
        )

    # noinspection PyUnboundLocalVariable
    return product_qs_filtered


def _parse_option_values(
    cls: Class,
    option_values_raw: List[OptionValueRaw],
) -> List[OptionValue]:
    option_values = []  # type: List[OptionValue]
    if cls.type == Type.INT or cls.type == Type.DECIMAL:
        for option_value_raw in option_values_raw:
            option_values.append(_parse_option_value(cls, option_value_raw))
    else:
        option_values = option_values_raw
    return option_values


def _parse_option_value(cls: Class, option_value_raw: OptionValueRaw) -> OptionValue:
    if cls.type == Type.DECIMAL:
        return decimal.Decimal(option_value_raw)
    else:
        return option_value_raw
