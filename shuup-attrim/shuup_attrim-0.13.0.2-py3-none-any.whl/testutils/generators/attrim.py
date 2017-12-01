from typing import List, Union, Dict

from faker import Faker
from shuup.testing.factories import get_default_product_type
from shuup_testutils.generators import UniqueGen
from shuup_utils.lang_constants import LANG_CODES

from attrim.models import Class
from attrim.models.type import Type
from attrim.models import Option
from attrim.trans_str import TransStr, OptionValue, LangCode


class AttrimGen:
    def __init__(self):
        self._fake = Faker()
        self._unique_gen = UniqueGen()

    # noinspection PyShadowingBuiltins
    def cls(
        self,
        code: str = None,
        name: Union[TransStr, str] = None,
        type: Type = Type.TRANS_STR,
        options_amount: int = 3,
    ) -> Class:
        cls = Class.objects.create(
            code=code or self.code(),
            type=type,
            product_type=get_default_product_type(),
        )
        
        if isinstance(name, str):
            cls.name = name
        elif isinstance(name, TransStr):
            cls.set_name(name)
        elif name is None:
            cls.set_name(self.name())

        options_generated = self.option_list(cls=cls, amount=options_amount)
        cls.options.set(options_generated)

        cls.save()

        return cls

    def option_list(self, cls: Class, amount: int = 4) -> List[Option]:
        options = []  # type: List[Option]
        for option_number in range(0, amount):
            option = self.option(cls=cls, order=option_number)
            options.append(option)
        return options

    def option(self, cls: Class, value: OptionValue = None, order: int = None) -> Option:
        if cls.type == Type.INT:
            return Option.objects.create(
                cls=cls,
                order=order,
                value=value or self._unique_gen.integer(),
            )
        elif cls.type == Type.STR:
            return Option.objects.create(
                cls=cls,
                order=order,
                value=value or self._unique_gen.word(),
            )
        elif cls.type == Type.TRANS_STR:
            return Option.objects.create(
                cls=cls,
                order=order,
                value=value or self.trans_str(),
            )
        else:
            raise NotImplementedError('Given cls.type is not supported.')

    def code(self) -> str:
        return self._unique_gen.word()

    def name(self) -> TransStr:
        return self.trans_str()

    def trans_str(self) -> TransStr:
        unique_gen = UniqueGen()
        trans_str_values = {}  # type: Dict[LangCode, str]
        for lang_code in LANG_CODES:
            value = unique_gen.word()
            trans_str_values.update({lang_code: value})
        return TransStr(**trans_str_values)
