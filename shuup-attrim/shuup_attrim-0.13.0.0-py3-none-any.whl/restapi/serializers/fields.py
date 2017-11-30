from typing import Union

from decimal import Decimal

from parler.models import TranslatableModel
from parler.utils.context import switch_language
from rest_framework import serializers
from shuup_utils.lang_constants import LANG_CODES

from attrim.models import Option, Class
from attrim.models.type import Type
from attrim.trans_str import TransStr, OptionValue
from attrim.trans_str import TransStrDict


ValueSerialized = Union[
    str,
    int,
    TransStrDict,
]


class OptionValueField(serializers.Field):
    def to_internal_value(self, value_raw: ValueSerialized) -> OptionValue:
        cls = Class.objects.get(pk=self.parent.initial_data['cls'])
        if cls.type == Type.INT:
            return int(value_raw)
        elif cls.type == Type.DECIMAL:
            return Decimal(value_raw)
        elif cls.type == Type.STR:
            return str(value_raw)
        elif cls.type == Type.TRANS_STR:
            # noinspection PyArgumentList
            return TransStr(**value_raw)

    def get_attribute(self, instance: Option) -> Option:
        """
        Pass the instance onto `to_representation` in place of just the `value`
        field, as the default `get_attribute` impl does.
        """
        return instance

    def to_representation(self, option: Option) -> ValueSerialized:
        value_serialized = {}
        if option.cls.type == Type.INT:
            value_serialized = int(option.get_value())
        elif option.cls.type == Type.DECIMAL:
            value_serialized = str(option.get_value())
        elif option.cls.type == Type.STR:
            value_serialized = str(option.get_value())
        elif option.cls.type == Type.TRANS_STR:
            for lang_code in LANG_CODES:
                with switch_language(option, lang_code):
                    value_serialized[lang_code] = option.get_value()
        return value_serialized


class TransStrField(serializers.Field):
    def to_internal_value(self, value_raw: TransStrDict) -> TransStr:
        return TransStr(**value_raw)

    def get_attribute(self, instance: TranslatableModel) -> TranslatableModel:
        """
        Pass the instance onto `to_representation` in place of just the `value`
        field, as the default `get_attribute` impl does.
        """
        return instance

    def to_representation(self, instance: TranslatableModel) -> TransStrDict:
        trans_str_dict = {} # type: TransStrDict
        for lang_code in LANG_CODES:
            with switch_language(object=instance, language_code=lang_code):
                field_name = self.source
                field_translation = getattr(instance, field_name)
                trans_str_dict[lang_code] = field_translation
        return trans_str_dict
